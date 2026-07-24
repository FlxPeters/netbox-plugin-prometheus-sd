import json
import os
import time
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
from contextlib import contextmanager

from invoke import task
from testcontainers.core.image import DockerImage
from testcontainers.core.network import Network
from testcontainers.core.container import DockerContainer
from testcontainers.redis import RedisContainer
from testcontainers.postgres import PostgresContainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NETBOX_VER = os.getenv("NETBOX_VER", "latest")
SECRET_KEY = os.getenv(
    "NETBOX_SECRET_KEY",
    "at-least-50-characters-long-for-dev-use-only-please-change-me-in-production",
)

# Netbox listens on 8080 inside the container.
NETBOX_CONTAINER_PORT = 8080
NETBOX_HOST_PORT = 8000
PROMETHEUS_CONTAINER_PORT = 9090
PROMETHEUS_HOST_PORT = 9090

# Demo credentials. These are also hard-coded in example/prometheus.yml, which is
# both the documented example and the config this test suite actually runs, so
# the two cannot drift apart.
DEMO_TOKEN = "0123456789abcdef0123456789abcdef01234567"
DEMO_USER = "admin"
DEMO_PASSWORD = "admin"

PROMETHEUS_IMAGE = "prom/prometheus:v3.9.0"
PROMETHEUS_CONFIG = "example/prometheus.yml"

# Seed data for the demo and for the end-to-end test. The unit-test fixtures are
# reused rather than maintaining a second set: they already cover config context,
# services, contacts and tags, which is exactly what the labels are built from.
SEED_SCRIPT = """
from users.models import Token, User

from netbox_prometheus_sd.tests import utils

# The API token is created here rather than through SUPERUSER_API_TOKEN, because
# that env var stopped being enough in Netbox 4.6: superuser tokens became v2,
# and v2 additionally requires API_TOKEN_PEPPERS to be configured and
# SUPERUSER_API_KEY to be set, so it silently creates no token at all. A v1 token
# sidesteps that and behaves the same on every 4.x release.
#
# Where the secret lives moved too. Up to 4.5 it is `key`. From 4.6 `key` is a
# 12-character v2 identifier and the v1 secret is `plaintext`, assigned through
# the `token=` constructor argument.
user = User.objects.filter(username="%(user)s").first() or User.objects.create_superuser(
    "%(user)s", "admin@example.com", "%(password)s"
)
token_fields = {f.name for f in Token._meta.get_fields()}
if "plaintext" in token_fields:  # Netbox >= 4.6
    Token.objects.filter(plaintext="%(token)s").delete()
    Token.objects.create(user=user, version=1, token="%(token)s")
else:
    Token.objects.filter(key="%(token)s").delete()
    Token.objects.create(user=user, key="%(token)s")

for i in range(1, 4):
    utils.build_device_full(f"demo-device-{i}.example.com", i)

for i in range(1, 4):
    utils.build_vm_full(f"demo-vm-{i}.example.com", 100 + i)

print("seeded")
""" % {"user": DEMO_USER, "password": DEMO_PASSWORD, "token": DEMO_TOKEN}


@dataclass
class NetBoxRuntime:
    image: str
    network: Network
    redis: RedisContainer
    postgres: PostgresContainer
    netbox: DockerContainer


def create_netbox_container(
    image: str,
    network: Network,
    command=None,
    bind_port: bool = False,
    host_port: int = NETBOX_HOST_PORT,
    container_port: int = NETBOX_CONTAINER_PORT,
) -> DockerContainer:
    """
    Return a configured NetBox container, but do not start it yet.
    """
    container = DockerContainer(str(image))
    container.with_network(network)
    # Prometheus reaches Netbox by this name; example/prometheus.yml uses it.
    container.with_network_aliases("netbox")
    container.with_env("REDIS_HOST", "redis")
    container.with_env("DB_HOST", "postgres")
    container.with_env("DB_NAME", "netbox")
    container.with_env("DB_USER", "netbox")
    container.with_env("DB_PASSWORD", "netbox")
    container.with_env("SECRET_KEY", SECRET_KEY)
    container.with_env("SKIP_SUPERUSER", "false")
    container.with_env("SUPERUSER_NAME", DEMO_USER)
    container.with_env("SUPERUSER_PASSWORD", DEMO_PASSWORD)
    container.with_env("SUPERUSER_EMAIL", "admin@example.com")
    container.with_env("SUPERUSER_API_TOKEN", DEMO_TOKEN)

    if bind_port:
        container.with_bind_ports(container_port, host_port)

    if command is None:
        command = ["sleep", "infinity"]

    container.with_command(command)
    return container


def create_prometheus_container(network: Network, bind_port: bool = True):
    """
    Prometheus configured with example/prometheus.yml, on the same network as
    Netbox so the http_sd URLs in that file resolve.
    """
    container = DockerContainer(PROMETHEUS_IMAGE)
    container.with_network(network)
    container.with_network_aliases("prometheus")
    container.with_volume_mapping(
        os.path.abspath(PROMETHEUS_CONFIG),
        "/etc/prometheus/prometheus.yml",
        "ro",
    )
    if bind_port:
        container.with_bind_ports(PROMETHEUS_CONTAINER_PORT, PROMETHEUS_HOST_PORT)
    return container


@contextmanager
def netbox_runtime(
    command=None,
    bind_port: bool = False,
    host_port: int = NETBOX_HOST_PORT,
    container_port: int = NETBOX_CONTAINER_PORT,
):
    """
    Build image, start network + dependencies, and yield a configured runtime.
    """
    image_ctx = DockerImage(
        path=".",
        buildargs={"netbox_ver": NETBOX_VER},
    )

    logger.info("Building Docker image for NetBox %s...", NETBOX_VER)

    with image_ctx as image:
        with Network() as network:
            redis_container = RedisContainer(image="redis:7")
            redis_container.with_network(network)
            redis_container.with_network_aliases("redis")

            postgres_container = PostgresContainer(
                image="postgres:15",
                username="netbox",
                password="netbox",
                dbname="netbox",
            )
            postgres_container.with_network(network)
            postgres_container.with_network_aliases("postgres")

            with redis_container as redis, postgres_container as postgres:
                netbox_container = create_netbox_container(
                    image=str(image),
                    network=network,
                    command=command,
                    bind_port=bind_port,
                    host_port=host_port,
                    container_port=container_port
                )

                with netbox_container as netbox:
                    yield NetBoxRuntime(
                        image=str(image),
                        network=network,
                        redis=redis,
                        postgres=postgres,
                        netbox=netbox,
                    )


def serve_command():
    """
    Run the real Netbox server: the entrypoint waits for the database, migrates
    and creates the superuser, then execs the launcher.
    """
    return [
        "/opt/netbox/docker-entrypoint.sh",
        "/opt/netbox/launch-netbox.sh",
    ]


def wait_for_http(
    url: str,
    timeout: int = 600,
    interval: int = 5,
    token: str = None,
    accept=(200,),
) -> None:
    """
    Poll url until it answers with one of `accept`, or raise on timeout.

    Netbox runs with LOGIN_REQUIRED, so an unauthenticated API request answers
    403. That is still proof the server is up, which is why the readiness probe
    accepts it -- the token cannot be checked earlier than this, because it is
    created by the seed step that runs afterwards.
    """
    request = urllib.request.Request(url)
    if token:
        request.add_header("Authorization", f"Token {token}")

    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                if response.status in accept:
                    return
                last_error = f"HTTP {response.status}"
        except urllib.error.HTTPError as exc:
            if exc.code in accept:
                return
            last_error = exc
        except (urllib.error.URLError, OSError, ConnectionError) as exc:
            last_error = exc
        time.sleep(interval)
    raise TimeoutError(f"{url} did not become ready within {timeout}s: {last_error}")


def seed_demo_data(runtime: NetBoxRuntime) -> None:
    logger.info("Seeding demo data...")
    exit_code, output = runtime.netbox.exec(
        ["python3", "manage.py", "shell", "-c", SEED_SCRIPT]
    )
    if exit_code != 0:
        raise Exception(f"Seeding failed with exit code {exit_code}:\n{output.decode()}")


def prometheus_targets():
    """Active targets Prometheus currently knows about, grouped by job."""
    url = f"http://localhost:{PROMETHEUS_HOST_PORT}/api/v1/targets?state=any"
    with urllib.request.urlopen(url, timeout=10) as response:
        payload = json.load(response)

    grouped = {}
    for target in payload["data"]["activeTargets"]:
        grouped.setdefault(target["labels"].get("job"), []).append(target)
    return grouped


@contextmanager
def demo_stack():
    """Netbox serving real HTTP, seeded with demo data, with Prometheus attached."""
    with netbox_runtime(command=serve_command(), bind_port=True) as runtime:
        netbox_url = f"http://localhost:{NETBOX_HOST_PORT}/api/"
        logger.info("Waiting for Netbox at %s ...", netbox_url)
        # 403 means Netbox is answering but the request is unauthenticated, which
        # is all this probe needs to know: the token does not exist until the
        # seed step below creates it.
        wait_for_http(netbox_url, accept=(200, 403))

        seed_demo_data(runtime)

        # Now that the token exists, confirm it actually authenticates against
        # the plugin's own endpoint -- this is exactly the request Prometheus
        # will make, so failing here is far clearer than an empty target list.
        sd_url = f"http://localhost:{NETBOX_HOST_PORT}/api/plugins/prometheus-sd/devices/"
        wait_for_http(sd_url, timeout=120, token=DEMO_TOKEN)
        logger.info("Plugin endpoint reachable with the demo token.")

        prometheus = create_prometheus_container(runtime.network)
        with prometheus:
            prometheus_url = f"http://localhost:{PROMETHEUS_HOST_PORT}/-/ready"
            logger.info("Waiting for Prometheus at %s ...", prometheus_url)
            wait_for_http(prometheus_url)
            yield runtime, prometheus


@task
def build_dev(c):
    """Run Netbox and Prometheus with demo data, and leave them running."""
    with demo_stack():
        logger.info("Netbox:     http://localhost:%s (%s/%s)", NETBOX_HOST_PORT, DEMO_USER, DEMO_PASSWORD)
        logger.info("API token:  %s", DEMO_TOKEN)
        logger.info("Prometheus: http://localhost:%s (Status -> Target health)", PROMETHEUS_HOST_PORT)
        logger.info("Press Ctrl+C to stop.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping containers...")


def run_unit_tests(runtime: NetBoxRuntime) -> None:
    """
    Django tests, executed inside the Netbox container.

    `manage.py test` builds and tears down its own database, so this is safe to
    run against a container that is also serving the seeded demo data.
    """
    logger.info("Running tests inside NetBox container...")
    exit_code, output = runtime.netbox.exec(["python3", "manage.py", "test", "netbox_prometheus_sd"])
    logger.info(output.decode())
    if exit_code != 0:
        raise Exception(f"Tests failed with exit code {exit_code}")

def assert_prometheus_discovery() -> None:
    """Fail unless Prometheus discovered every job with its expected labels."""
    expectations = {
        # job -> labels every one of its targets must carry after relabeling
        "netbox_devices": ("instance", "site", "role"),
        "netbox_virtual_machines": ("instance", "site"),
        "netbox_services": ("instance", "service"),
        "netbox_ip_addresses_raw": (),
    }

    # Service discovery is not instant; give Prometheus a few refresh cycles.
    deadline = time.time() + 180
    jobs = {}
    while time.time() < deadline:
        jobs = prometheus_targets()
        if all(jobs.get(job) for job in expectations):
            break
        time.sleep(5)

    failures = []
    for job, required_labels in expectations.items():
        targets = jobs.get(job) or []
        if not targets:
            failures.append(f"{job}: Prometheus discovered no targets")
            continue

        logger.info("%s: %s target(s)", job, len(targets))

        for label in required_labels:
            missing = [t for t in targets if not t["labels"].get(label)]
            if missing:
                failures.append(
                    f"{job}: {len(missing)}/{len(targets)} target(s) have no "
                    f"'{label}' label -- relabel_configs did not apply"
                )

        # The whole point of the plugin: Netbox metadata reaches Prometheus.
        meta = [
            key
            for key in targets[0]["discoveredLabels"]
            if key.startswith("__meta_netbox_")
        ]
        if not meta:
            failures.append(f"{job}: no __meta_netbox_* labels were discovered")
        else:
            logger.info("%s: %s __meta_netbox_* labels", job, len(meta))

    if failures:
        raise Exception(
            "Prometheus did not discover the expected targets:\n  - "
            + "\n  - ".join(failures)
        )

    logger.info("Prometheus discovered every expected job.")


@task
def unittest(c):
    """Run only the Django unit tests (no Prometheus)."""
    with netbox_runtime() as runtime:
        run_unit_tests(runtime)


@task
def test_prometheus(c):
    """
    End-to-end check that Prometheus can actually consume the plugin's output.

    The unit tests assert the JSON shape, which is not the same thing as
    Prometheus accepting it as an http_sd source: a structurally valid response
    that Prometheus rejects would pass every other test in this repository. This
    runs the real thing against example/prometheus.yml, so the documented example
    and the tested configuration cannot drift apart.
    """
    with demo_stack():
        assert_prometheus_discovery()


@task(default=True)
def test(c):
    """Run the unit tests and the Prometheus end-to-end check in one stack."""
    with demo_stack() as (runtime, _prometheus):
        run_unit_tests(runtime)
        assert_prometheus_discovery()
