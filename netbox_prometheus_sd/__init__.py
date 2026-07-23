from netbox.plugins import PluginConfig

# Placeholder for semantic release
__VERSION__ = "1.3.0"


class PrometheusSD(PluginConfig):
    name = "netbox_prometheus_sd"
    verbose_name = "Netbox Prometheus SD"
    description = (
        "Provide Prometheus url_sd compatible API Endpoint with data from netbox"
    )
    version = __VERSION__
    author = "Felix Peters"
    author_email = "mail@felixpeters.de"
    base_url = "prometheus-sd"
    required_settings = []
    default_settings = {}
    min_version = "4.0.0"


config = PrometheusSD
