# netbox-plugin-prometheus-sd

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/workflows/CI/badge.svg?event=push)](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/actions?query=workflow%3ACI)

Provide Prometheus http_sd compatible API Endpoint with data from Netbox.

HTTP SD is a new feature in Prometheus 2.28.0 which allows to discover hosts from a URL instead of files only. 
This project is an attempt to provide a compatible API endpoint in Netbox to make devices, IP and virtual machines available to Prometheus.

## Instalation

tbd.


## Usage

The plugin only provides a new API endpoint on the Netbox API. There is no further action required after installation. 

## API

The plugin includes 4 API endpoints to manage the onbarding tasks

```shell
GET        /api/plugins/prometheus-sd/targets/       Get a list of prometheus compatible targets with lables
```

There is currently not authentication. It's planed to use the native Netbox API token method with filters for devices and VMs the user has access to. 

## Development

We use Poetry for dependency management and invoke as task runner. 
As Netbox plugins cannot be tested standalone, we need invoke to start all code embedded in Netbox Docker containers.

All code to run in docker is located under `.devcontainer` which is also the starting point for VScode remote containers (not finished yet).

To start a virtual env managed by poetry run `poetry shell`. 