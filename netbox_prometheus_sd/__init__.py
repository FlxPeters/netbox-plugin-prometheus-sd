from extras.plugins import PluginConfig


class PrometheusSD(PluginConfig):
    name = "netbox_prometheus_sd"
    verbose_name = "Netbox Prometheus SD"
    description = (
        "Provide Prometheus url_sd compatible API Endpoint with data from netbox"
    )
    version = "0.4"
    author = "Felix Peters"
    author_email = "mail@felixpeters.de"
    base_url = "prometheus-sd"
    required_settings = []
    default_settings = {}


config = PrometheusSD  # pylint:disable=invalid-name
