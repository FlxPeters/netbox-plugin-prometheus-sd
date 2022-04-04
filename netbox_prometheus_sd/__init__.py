from extras.plugins import PluginConfig


class PrometheusSD(PluginConfig):
    name = "netbox_prometheus_sd"
    verbose_name = "Netbox Prometheus SD"
    description = (
        "Provide Prometheus url_sd compatible API Endpoint with data from netbox"
    )
    version = "0.1"
    author = "Andrei Protsenko"
    author_email = "prondy@gmail.com"
    base_url = "prometheus-sd"
    required_settings = ["custom_field_name"]
    default_settings = {"target_port": 9100}


config = PrometheusSD
