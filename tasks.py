import os
from invoke import task

NETBOX_VER = os.getenv("NETBOX_VER", "latest")

# Name of the docker image/container
NAME = os.getenv("IMAGE_NAME", "netbox-plugin-prometheus")
PWD = os.getcwd()

COMPOSE_BIN = os.getenv("COMPOSE_BIN", "docker compose")
COMPOSE_FILE = "develop/docker-compose.yml"
DOCKER_FILE = "develop/Dockerfile"
BUILD_NAME = "netbox_prometheus_sd"


# ------------------------------------------------------------------------------
# BUILD
# ------------------------------------------------------------------------------
@task
def build(context, netbox_ver=NETBOX_VER):
    """Build all docker images.
    Args:
        context (obj): Used to run specific commands
        netbox_ver (str): NetBox version to use to build the container
    """
    print(f"Build Netbox image for version {netbox_ver} ...")
    context.run(
        f"{COMPOSE_BIN} -f {COMPOSE_FILE} -p {BUILD_NAME} build --build-arg netbox_ver={netbox_ver}",
        env={"NETBOX_VER": netbox_ver},
    )


# ------------------------------------------------------------------------------
# START / STOP / DEBUG
# ------------------------------------------------------------------------------
@task
def debug(context, netbox_ver=NETBOX_VER):
    """Start NetBox and its dependencies in debug mode.
    Args:
        context (obj): Used to run specific commands
        netbox_ver (str): NetBox version to use to build the container
    """
    print("Starting Netbox .. ")
    context.run(
        f"{COMPOSE_BIN} -f {COMPOSE_FILE} -p {BUILD_NAME} up",
        env={"NETBOX_VER": netbox_ver},
    )


@task
def start(context, netbox_ver=NETBOX_VER):
    """Start NetBox and its dependencies in detached mode.
    Args:
        context (obj): Used to run specific commands
        netbox_ver (str): NetBox version to use to build the container
    """
    print("Starting Netbox in detached mode.. ")
    context.run(
        f"{COMPOSE_BIN} -f {COMPOSE_FILE} -p {BUILD_NAME} up -d",
        env={"NETBOX_VER": netbox_ver},
    )


@task
def stop(context, netbox_ver=NETBOX_VER):
    """Stop NetBox and its dependencies.
    Args:
        context (obj): Used to run specific commands
        netbox_ver (str): NetBox version to use to build the container
    """
    print("Stopping Netbox .. ")
    context.run(
        f"{COMPOSE_BIN} -f {COMPOSE_FILE} -p {BUILD_NAME} down",
        env={"NETBOX_VER": netbox_ver},
    )


@task
def destroy(context, netbox_ver=NETBOX_VER):
    """Destroy all containers and volumes.
    Args:
        context (obj): Used to run specific commands
        netbox_ver (str): NetBox version to use to build the container
    """
    context.run(
        f"{COMPOSE_BIN} -f {COMPOSE_FILE} -p {BUILD_NAME} down",
        env={"NETBOX_VER": netbox_ver},
    )
    context.run(
        f"docker volume rm -f {BUILD_NAME}_pgdata_netbox_prometheus_sd",
        env={"NETBOX_VER": netbox_ver},
    )


# ------------------------------------------------------------------------------
# ACTIONS
# ------------------------------------------------------------------------------
@task
def nbshell(context, netbox_ver=NETBOX_VER):
    """Launch a nbshell session.
    Args:
        context (obj): Used to run specific commands
        netbox_ver (str): NetBox version to use to build the container
        python_ver (str): Will use the Python version docker image to build from
    """
    context.run(
        f"{COMPOSE_BIN} -f {COMPOSE_FILE} -p {BUILD_NAME} exec netbox python manage.py nbshell",
        env={"NETBOX_VER": netbox_ver},
        pty=True,
    )


@task
def cli(context, netbox_ver=NETBOX_VER):
    """Launch a bash shell inside the running NetBox container.
    Args:
        context (obj): Used to run specific commands
        netbox_ver (str): NetBox version to use to build the container
    """
    context.run(
        f"{COMPOSE_BIN} -f {COMPOSE_FILE} -p {BUILD_NAME} exec netbox bash",
        env={"NETBOX_VER": netbox_ver},
        pty=True,
    )


@task
def create_user(context, user="admin", netbox_ver=NETBOX_VER):
    """Create a new user in django (default: admin), will prompt for password.
    Args:
        context (obj): Used to run specific commands
        user (str): name of the superuser to create
        netbox_ver (str): NetBox version to use to build the container
    """
    context.run(
        f"{COMPOSE_BIN} -f {COMPOSE_FILE} -p {BUILD_NAME} "
        f"exec netbox python manage.py createsuperuser --username {user}",
        env={"NETBOX_VER": netbox_ver},
        pty=True,
    )


# ------------------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------------------
@task
def tests(context, netbox_ver=NETBOX_VER):
    """Run Django unit tests for the plugin.
    Args:
        context (obj): Used to run specific commands
        netbox_ver (str): NetBox version to use to build the container
    """
    docker = f"{COMPOSE_BIN} -f {COMPOSE_FILE} -p {BUILD_NAME} run netbox"
    context.run(
        f'{docker} sh -c "python manage.py test netbox_prometheus_sd --keepdb"',
        env={"NETBOX_VER": netbox_ver},
        pty=True,
    )
