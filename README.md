# netbox-plugin-prometheus-sd

Provide Prometheus http_sd compatible API Endpoint with data from Netbox.

HTTP SD is a new feature in Prometheus and not available at the moment.
This project is an attempt to provide a compatible API endpoint.

> :warning: **This is work in progress. The feature in Prometheus is still under development and so is this plugin.**

See https://github.com/prometheus/prometheus/pull/8839 for more details.

## Instalation

tbd.

## Usage

The plugin only provides a new API endpoint on the Netbox API. There is no further action required after installation. 

### API

The plugin includes 4 API endpoints to manage the onbarding tasks

```shell
GET        /api/plugins/prometheus-sd/targets/       Get a list of prometheus compatible targets with lables
```

There is currently not authentication. It's planed to use the native Netbox API token method with filters for devices and VMs the user has access to. 
