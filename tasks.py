import os
import time
import logging
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
    host_port: int = 8000,
    container_port: int = 8000,
) -> DockerContainer:
    """
    Return a configured NetBox container, but do not start it yet.
    """
    container = DockerContainer(str(image))
    container.with_network(network)
    container.with_env("REDIS_HOST", "redis")
    container.with_env("DB_HOST", "postgres")
    container.with_env("DB_NAME", "netbox")
    container.with_env("DB_USER", "netbox")
    container.with_env("DB_PASSWORD", "netbox")
    container.with_env("SECRET_KEY", SECRET_KEY)

    if bind_port:
        container.with_bind_ports(container_port, host_port)

    if command is None:
        command = ["sleep", "infinity"]

    container.with_command(command)
    return container


@contextmanager
def netbox_runtime(
    command=None,
    bind_port: bool = False,
    host_port: int = 8000,
    container_port: int = 8000,
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


@task
def build_dev(c):
    with netbox_runtime(bind_port=True) as runtime:
        logger.info("Container ID for NetBox: %s", runtime.netbox._container.short_id)
        logger.info("Press Ctrl+C to stop.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping containers...")


@task
def test(c):
    with netbox_runtime() as runtime:
        logger.info("Running tests inside NetBox container...")
        exit_code, output = runtime.netbox.exec(["python3", "manage.py", "test", "netbox_prometheus_sd"])
        logger.info(output.decode())
        if exit_code != 0:
            raise Exception(f"Tests failed with exit code {exit_code}")