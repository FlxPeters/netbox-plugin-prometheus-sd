# netbox-plugin-prometheus-sd

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/workflows/CI/badge.svg?event=push)](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/actions?query=workflow%3ACI)
[![PyPI](https://img.shields.io/pypi/v/netbox-plugin-prometheus-sd)](https://pypi.org/project/netbox-plugin-prometheus-sd/)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/flxpeters)

Provide Prometheus `http_sd` compatible API Endpoint with data from Netbox.

HTTP SD is a feature since Prometheus 2.28.0 that allows hosts to be found via a URL instead of just files.
This plugin implements API endpoints in Netbox to make devices, services, IPs and virtual machines available to Prometheus.

## Compatibility

We aim to support the latest major versions of Netbox.

| Plugin | Netbox |
|---|---|
| `2.x` | `>= 4.0` |
| `1.x` | `3.x` (no longer maintained) |

Check the `.github/workflows/ci.yml` pipeline for the current tested builds.
Other versions may work, but we do not test them explicitly. All relevant target versions are tested in CI.

Plugin `2.0` also fixed a set of N+1 queries that made the endpoints very slow on
larger installations ([#265](https://github.com/FlxPeters/netbox-plugin-prometheus-sd/issues/265)).
If service discovery is putting noticeable load on your Netbox database, upgrading
is worthwhile.

## Installation

The plugin is available as a Python package in pypi and can be installed with pip

```bash
pip install netbox-plugin-prometheus-sd
```

Enable the plugin in /opt/netbox/netbox/netbox/configuration.py:

```python
    PLUGINS = ['netbox_prometheus_sd']
```

The plugin has not further plugin configuration.

## Usage

The plugin only provides a new API endpoint on the Netbox API. There is no further action required after installation.

### API

The plugin reuses Netbox API view sets with new serializers for Prometheus.
This means that all filters that can be used on the Netbox API can also be used to filter Prometheus targets.
Paging is disabled because Prometheus does not support paged results.

The plugin also reuses the Netbox authentication and permission model.
Depending on the Netbox configuration, a token with valid object permissions must be passed to Netbox.

```
GET        /api/plugins/prometheus-sd/devices/              Get a list of devices in a prometheus compatible format
GET        /api/plugins/prometheus-sd/virtual-machines/     Get a list of vms in a prometheus compatible format
GET        /api/plugins/prometheus-sd/services/             Get a list of services in a prometheus compatible format
GET        /api/plugins/prometheus-sd/ip-addresses/         Get a list of ip in a prometheus compatible format
```

#### Extended services filters

Apart from standard Netbox filters, services endpoint also supports `tenant=<slug>` or `tenant_id=<id>` parameters.
The lookup is only executed against the `tenant` attribute of the object associated with the service.

#### Filtering and response size

Because paging is disabled, one request serializes every object the token is
allowed to see. Filtering with the standard Netbox query parameters is the
supported way to keep responses small, and it is usually what you want anyway —
Prometheus should not be told about decommissioned hardware:

```
/api/plugins/prometheus-sd/devices/?status=active&tag=monitoring&site=dc1
```

### Labels

Every target carries `__meta_netbox_*` labels describing the Netbox object.
**Prometheus discards labels starting with `__` after service discovery**, so
they have to be copied into real labels with `relabel_configs` (see below) if you
want them on your metrics.

A label is only present when the underlying field is populated — a device with no
tenant has no `__meta_netbox_tenant`.

| Label | Devices | VMs | Services | IPs |
|---|:-:|:-:|:-:|:-:|
| `id`, `name`, `status`, `model` | ✓ | ✓ | id/name only | ✓ (no name) |
| `primary_ip`, `primary_ip4`, `primary_ip6` | ✓ | ✓ | from parent | |
| `oob_ip` | ✓ | | from parent | |
| `ip` | | | | ✓ |
| `role`, `role_slug` | ✓ | ✓ | | `role` only |
| `platform`, `platform_slug` | ✓ | ✓ | | |
| `device_type`, `device_type_slug` | ✓ | | | |
| `site`, `site_slug` | ✓ | ✓ | from parent | |
| `scope`, `scope_slug` | | ✓ ¹ | | |
| `location`, `location_slug` | ✓ | | | |
| `rack`, `rack_u_position` | ✓ | | | |
| `cluster`, `cluster_group`, `cluster_type` | ✓ ² | ✓ | | |
| `tenant`, `tenant_slug` | ✓ | ✓ | from parent | ✓ |
| `tenant_group`, `tenant_group_slug` | ✓ | ✓ | from parent | ✓ |
| `tags`, `tag_slugs` | ✓ | ✓ | ✓ | ✓ |
| `services` | ✓ | ✓ | | |
| `contact_<priority>_{name,email,comments,role}` | ✓ | ✓ | from parent | |
| `custom_field_<name>` | ✓ | ✓ | ✓ | ✓ |
| `description` | ✓ | | | |
| `parent`, `display`, `ports`, `ipaddresses` | | | ✓ | |

¹ Netbox 4.2 replaced the cluster's site with a generic `scope`. On 4.2+ a VM
emits `scope`/`scope_slug` for the cluster, and `site`/`site_slug` for its own
site; below 4.2 the cluster's site is reported as `site`.
² Only when the device is assigned to a cluster.

Config context can additionally set `__metrics_path__` and `__scheme__`, which
Prometheus consumes directly (see [Config context](#config-context)).

### Relabeling

The `__meta_netbox_*` labels are dropped unless you map them. A typical device job
scraping node_exporter on the primary IP:

```yaml
scrape_configs:
  - job_name: netbox-devices
    http_sd_configs:
      - url: http://netbox:8080/api/plugins/prometheus-sd/devices/?status=active&tag=monitoring
        refresh_interval: 60s
        authorization:
          type: Token
          credentials: "<your-netbox-api-token>"

    relabel_configs:
      # Skip anything without a primary IPv4, otherwise the address below is empty.
      - source_labels: [__meta_netbox_primary_ip4]
        regex: ^$
        action: drop

      # Scrape the primary IP instead of the device name, which may not resolve.
      - source_labels: [__meta_netbox_primary_ip4]
        target_label: __address__
        replacement: "$1:9100"

      # Keep the Netbox name as the instance label rather than the IP.
      - source_labels: [__meta_netbox_name]
        target_label: instance

      # Promote the dimensions worth alerting and grouping on.
      - source_labels: [__meta_netbox_site_slug]
        target_label: site
      - source_labels: [__meta_netbox_role_slug]
        target_label: role
      - source_labels: [__meta_netbox_tenant_slug]
        target_label: tenant
```

Two things worth knowing:

- `tags` and `tag_slugs` are comma-joined, so match them with `.*,?value,?.*`
  rather than `=`.
- Devices and VMs use the same label names, so one set of `relabel_configs` can
  be reused across both jobs.

### Config context

The plugin can also discover extra config to inject in the HTTP SD JSON from the config context of the devices/virtual machines.
If you have a `prometheus-plugin-prometheus-sd` entry in your config context with the following schema it will be automatically picked up:

```yaml
prometheus-plugin-prometheus-sd:
  - metrics_path: /not/metrics
    port: 4242
    scheme: https
  - port: 4243
```

This allow you to configure those values directly into netbox instead of doing that inside the Prometheus
config and filtering each scenario by a specific tag for instance.

If there is only one entry you can also use this form:

```yaml
prometheus-plugin-prometheus-sd:
  metrics_path: /not/metrics
  port: 4242
  scheme: https
```

### Example

[`example/prometheus.yml`](example/prometheus.yml) is a complete Prometheus
configuration covering all four endpoints, with `relabel_configs` mapping the
`__meta_netbox_*` labels onto real ones.

It is not a snippet that happens to be in the repository: the test suite runs
Prometheus against this exact file and asserts that the expected targets and
labels are discovered, so it cannot quietly stop working.

To see it running, with a Netbox that has demo data already loaded:

```bash
poetry run invoke build-dev
```

- Netbox: <http://localhost:8000> (`admin` / `admin`)
- Prometheus: <http://localhost:9090> — discovered targets are under
  Status → Target health, and expanding one shows the raw `__meta_netbox_*`
  labels before relabeling.

The demo data is the unit-test fixtures, so it also exercises config context
(the VMs get two targets each, on different ports), services, contacts and tags.

## Development

We use [Poetry](https://python-poetry.org/) for dependency management and [invoke](https://www.pyinvoke.org/) as task runner.
To test the plugin in an isolated environment, we use [testcontainers](https://testcontainers.com/?language=python)
which creates "throwaway, lightweight" Netbox Docker containers.

Install the dependencies with `poetry install`, then run the tasks through
`poetry run` (this works on every Poetry version, whereas `poetry shell` was moved
into a separate plugin in Poetry 2.0):

```bash
# Unit tests plus the Prometheus end-to-end check
poetry run invoke test

# Test against a specific Netbox release (default: latest)
NETBOX_VER=v4.6.5 poetry run invoke test

# Either half on its own
poetry run invoke unittest
poetry run invoke test-prometheus
```

The Netbox image is built from the `Dockerfile` in the repository root.

Testing has two layers:

- **Unit tests** — plain Django tests under `netbox_prometheus_sd/tests/`,
  executed inside the Netbox container. These cover the serializers and the
  label output.
- **Prometheus end-to-end** — Netbox serving real HTTP with seeded data, and a
  real Prometheus configured from `example/prometheus.yml`. It asserts that the
  expected jobs discover targets and that relabeling produced the expected
  labels.

The second layer exists because "valid JSON with targets and labels" is not the
same as "Prometheus accepts this as an `http_sd` source". A response that
Prometheus rejects would pass every unit test in this repository. It also keeps
the documented example honest, since it is the file under test.

Features should be covered by a test, but sometimes it is easier to develop
against a running system:

```bash
# Netbox + Prometheus with demo data, left running until Ctrl+C
poetry run invoke build-dev
```

Netbox is on <http://localhost:8000> (`admin` / `admin`) and Prometheus on
<http://localhost:9090>, already scraping it.

API endpoints for testing can be found at http://localhost:8000/api/plugins/prometheus-sd/

## Conventional Commits

This repository follows the Conventional Commits specification for versioning and changelog generation.
Conventional Commits provide a standardized way of writing commit messages to convey semantic meaning
about the changes made. Each commit message follows a defined format that includes a type,
an optional scope, and a message. The types typically include features, fixes, documentation, and more.
By adhering to this convention, we ensure clear and automated versioning, release notes, and changelog generation.
