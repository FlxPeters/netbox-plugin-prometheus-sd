# netbox-plugin-prometheus-sd

Provide Prometheus http_sd compatible API Endpoint with data from Netbox.

HTTP SD is a new feature in Prometheus 2.28.0 that allows hosts to be found via a URL instead of just files.
This plugin implements API endpoints in Netbox to make devices, IPs and virtual machines available to Prometheus.

## Installation and configuration

1) The plugin is available as a Python package in pypi and can be installed with pip

```
pip install netbox-plugin-prometheus-sd
```

2) Create a boolean custom field in the netbox, which will be used to determine
   if the device is to be in prometheus targets list. Bind this custom field to
   the device objects. In this case we use 'monitored' custom field.

3) Enable the plugin in /opt/netbox/netbox/netbox/configuration.py:

```
PLUGINS = ['netbox_prometheus_sd']
```

4) In the plugin settings, specify a name of boolean custom field which is used 
   for monitoring and target port.

```
PLUGINS_CONFIG = {
    'netbox_prometheus_sd': {
        'custom_field_name': 'monitored',
        'target_port': 5909,
    }
}
```

## Usage

The plugin only provides a new API endpoint on the Netbox API. There is no further 
action required after installation and configuration.

### API

The plugin reuses Netbox API view sets with new serializers for Prometheus.
This means that all filters that can be used on the Netbox api can also be used to filter Prometheus targets.
Paging is disabled because Prometheus does not support paged results.

The plugin also reuses the Netbox authentication and permission model.
Depending on the Netbox configuration, a token with valid object permissions must be passed to Netbox.

```
GET        /api/plugins/prometheus-sd/devices/              Get a list of devices in a prometheus compatible format
```