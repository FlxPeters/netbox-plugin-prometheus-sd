from django.conf import settings
from . import config

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("netbox_prometheus_sd", dict())
CUSTOM_FIELD_NAME = PLUGIN_SETTINGS["custom_field_name"]
TARGET_PORT = PLUGIN_SETTINGS.get("target_port", config.default_settings["target_port"])
