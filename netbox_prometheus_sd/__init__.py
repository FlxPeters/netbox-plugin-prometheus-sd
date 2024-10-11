try:
    from netbox.plugins import PluginConfig
except ImportError:
    # Fallback for old NetBox versions < 4.0
    from extras.plugins import PluginConfig


__VERSION__ = "1.1.1"


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


config = PrometheusSD
