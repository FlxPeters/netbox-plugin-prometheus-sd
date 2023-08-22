# netbox-plugin-prometheus-sd

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/workflows/CI/badge.svg?event=push)](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/actions?query=workflow%3ACI)
[![PyPI](https://img.shields.io/pypi/v/netbox-plugin-prometheus-sd)](https://pypi.org/project/netbox-plugin-prometheus-sd/)

Provide Prometheus http_sd compatible API Endpoint with data from Netbox.

HTTP SD is a new feature in Prometheus 2.28.0 that allows hosts to be found via a URL instead of just files.
This plugin implements API endpoints in Netbox to make devices, IPs and virtual machines available to Prometheus.

## Compatibility

We aim to support the latest major versions of Netbox. For now we Support Netbox `3.2`, `3.3`, `3.4` and `3.5` including bugfix versions.
Check the `.github/workflows/ci.yml` pipeline for the current tested builds. Other versions may work, but we do not test them explicitly.
All relevant target versions are tested in CI. Have a look at the Github Actions definition for the current build targets.

## Installation

The plugin is available as a Python package in pypi and can be installed with pip

    pip install netbox-plugin-prometheus-sd

Enable the plugin in /opt/netbox/netbox/netbox/configuration.py:

    PLUGINS = ['netbox_prometheus_sd']

The plugin has not further plugin configuration at the moment.

## Usage

The plugin only provides a new API endpoint on the Netbox API. There is no further action required after installation.

### API

The plugin reuses Netbox API view sets with new serializers for Prometheus.
This means that all filters that can be used on the Netbox api can also be used to filter Prometheus targets.
Paging is disabled because Prometheus does not support paged results.

The plugin also reuses the Netbox authentication and permission model.
Depending on the Netbox configuration, a token with valid object permissions must be passed to Netbox.

```
GET        /api/plugins/prometheus-sd/devices/              Get a list of devices in a prometheus compatible format
GET        /api/plugins/prometheus-sd/virtual-machines/     Get a list of vms in a prometheus compatible format
GET        /api/plugins/prometheus-sd/services/             Get a list of services in a prometheus compatible format
GET        /api/plugins/prometheus-sd/ip-addresses/         Get a list of ip in a prometheus compatible format
```

### Config context

The plugin can also discover extra config to inject in the HTTP SD JSON from the config context of the devices/virtual machines.
If you have a `prometheus-plugin-prometheus-sd` entry in your config context with the following schema it will be automatically picked up:

```
prometheus-plugin-prometheus-sd:
  - metrics_path: /not/metrics
    port: 4242
    scheme: https
  - port: 4243
```

This allow you to configure those values directly into netbox instead of doing that inside the Prometheus
config and filtering each scenario by a specific tag for instance.

If there is only one entry you can also use this form:

```
prometheus-plugin-prometheus-sd:
  metrics_path: /not/metrics
  port: 4242
  scheme: https
```

### Example

A working example on how to use this plugin with Prometheus is located at the `example` folder. Netbox content is created by using Netbox docker initializers.

The demo data doesn't make sense, but they are good enough for demonstrating how to configure Prometheus and get demo data to Prometheus service discovery.

Go to the `example` folder and run `docker-compose up`. Prometheus should get available on `http://localhost:9090`.

Push some example devices and objects to Netbox using the initializers:

```
docker-compose exec  netbox /opt/netbox/netbox/manage.py load_initializer_data --path /opt/netbox/initializers
```

Netbox content should then be available in the service discovery tab.

## Development

We use Poetry for dependency management and invoke as task runner.
As Netbox plugins cannot be tested standalone, we need invoke to start all code embedded in Netbox Docker containers.

All code to run in docker is located under `development`.
To start a virtual env managed by poetry run `poetry shell`.
All following commands are started inside this environment.

In order to run tests invoke the test steps

``` bash
# Execute all tests
invoke tests

# Execute unit tests only
invoke unittest
```

Features should be covered by a unit test, but some times it's easier to develop on an running system.

``` bash
# Start a local Netbox with docker
invoke start

# Create an user named `admin`
invoke create-user
```

Visit http://localhost:8000 and log in with the new user.
You can now define Netbox entities and test around.

API endpoints for testing can be found at http://localhost:8000/api/plugins/prometheus-sd/
