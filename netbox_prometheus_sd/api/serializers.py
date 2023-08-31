from rest_framework import serializers
from django.db import models
from virtualization.models import VirtualMachine
from dcim.models import Device
from ipam.models import IPAddress, Service

from netaddr import IPNetwork

from .utils import LabelDict
from . import utils

class SDConfigContextDuplicateSerializer(serializers.ListSerializer):

    def update(self, instance, validated_data):
        raise NotImplementedError("ListSerializer does not support update")

    def to_representation(self, data):
        """
        Override ListSerializer to duplicate config context list into a new field "_injected_prometheus_sd_config"
        List of object instances -> List of dicts of primitive datatypes.
        """
        iterable = data.all() if isinstance(data, models.manager.BaseManager) else data

        ret = []
        for item in iterable:
            appended = False
            prometheus_sd_configs = item.get_config_context().get("prometheus-plugin-prometheus-sd", [])
            if not isinstance(prometheus_sd_configs, list):
                prometheus_sd_configs = [prometheus_sd_configs]

            for prometheus_sd_config in prometheus_sd_configs:
                if not isinstance(prometheus_sd_config, dict) or (
                    "port" not in prometheus_sd_config and
                    "metrics_path" not in prometheus_sd_config and
                    "scheme" not in prometheus_sd_config
                ):
                    continue

                item._injected_prometheus_sd_config = prometheus_sd_config # pylint: disable=protected-access
                appended = True
                ret.append(self.child.to_representation(item))

            if not appended:
                ret.append(self.child.to_representation(item))
        return ret

class PrometheusTargetsMixin:
    def get_targets(self, obj):
        target = obj.name
        prometheus_sd_config = getattr(obj, "_injected_prometheus_sd_config", {})

        port = prometheus_sd_config.get("port", None)
        if port and isinstance(port, int):
            target += f":{port}"

        return [target]

class PrometheusDeviceSerializer(serializers.ModelSerializer, PrometheusTargetsMixin):
    """Serialize a device to Prometheus target representation"""

    class Meta:
        model = Device
        fields = ["targets", "labels"]
        list_serializer_class = SDConfigContextDuplicateSerializer

    targets = serializers.SerializerMethodField()
    labels = serializers.SerializerMethodField()


    def get_labels(self, obj):
        labels = LabelDict(
            {"status": obj.status, "model": obj.__class__.__name__, "name": obj.name, "id": str(obj.id)}
        )

        utils.extract_primary_ip(obj, labels)
        utils.extracts_platform(obj, labels)
        utils.extract_tags(obj, labels)
        utils.extract_tenant(obj, labels)
        utils.extract_cluster(obj, labels)
        utils.extract_services(obj, labels)
        utils.extract_contacts(obj, labels)
        utils.extract_rack(obj, labels)
        utils.extract_custom_fields(obj, labels)

        if hasattr(obj, "role") and obj.role is not None:
            labels["role"] = obj.role.name
            labels["role_slug"] = obj.role.slug
        elif hasattr(obj, "device_role") and obj.device_role is not None:  # netbox <3.6.0
            labels["role"] = obj.device_role.name
            labels["role_slug"] = obj.device_role.slug

        if hasattr(obj, "device_type") and obj.device_type is not None:
            labels["device_type"] = obj.device_type.model
            labels["device_type_slug"] = obj.device_type.slug

        if hasattr(obj, "site") and obj.site is not None:
            labels["site"] = obj.site.name
            labels["site_slug"] = obj.site.slug

        labels = labels.get_labels()

        # Those shouldn't have the netbox prefix
        utils.extract_prometheus_sd_config(obj, labels)

        return labels


class PrometheusVirtualMachineSerializer(serializers.ModelSerializer, PrometheusTargetsMixin):
    """Serialize a virtual machine to Prometheus target representation"""

    class Meta:
        model = VirtualMachine
        fields = ["targets", "labels"]
        list_serializer_class = SDConfigContextDuplicateSerializer

    targets = serializers.SerializerMethodField()
    labels = serializers.SerializerMethodField()

    def get_labels(self, obj):
        labels = LabelDict(
            {"status": obj.status, "model": obj.__class__.__name__, "name": obj.name, "id": str(obj.id)}
        )

        utils.extract_primary_ip(obj, labels)
        utils.extracts_platform(obj, labels)
        utils.extract_tags(obj, labels)
        utils.extract_tenant(obj, labels)
        utils.extract_cluster(obj, labels)
        utils.extract_services(obj, labels)
        utils.extract_contacts(obj, labels)
        utils.extract_custom_fields(obj, labels)

        if hasattr(obj, "role") and obj.role is not None:
            labels["role"] = obj.role.name
            labels["role_slug"] = obj.role.slug

        labels = labels.get_labels()

        # Those shouldn't have the netbox prefix
        utils.extract_prometheus_sd_config(obj, labels)

        return labels


class PrometheusServiceSerializer(serializers.ModelSerializer):
    """Serialize a service to Prometheus target representation"""

    class Meta:
        model = Service
        fields = ["targets", "labels"]

    targets = serializers.SerializerMethodField()
    labels = serializers.SerializerMethodField()

    def get_targets(self, obj):
        return [obj.name]

    def get_labels(self, obj):
        labels = LabelDict(
            {"id": str(obj.id), "name": obj.name, "display": str(obj)}
        )

        utils.extract_service_ips(obj, labels)
        utils.extract_service_ports(obj, labels)
        utils.extract_tags(obj, labels)
        utils.extract_parent(obj, labels)
        utils.extract_custom_fields(obj, labels)

        return labels.get_labels()


class PrometheusIPAddressSerializer(serializers.ModelSerializer):
    """Serialize an IP address to Prometheus target representation"""

    class Meta:
        model = IPAddress
        fields = ["targets", "labels"]

    targets = serializers.SerializerMethodField()
    labels = serializers.SerializerMethodField()

    def extract_ip(self, obj):
        return str(IPNetwork(obj.address).ip)

    def get_targets(self, obj):
        if obj.dns_name:
            return [obj.dns_name]

        return [self.extract_ip(obj)]

    def get_labels(self, obj):
        """Get IP address labels"""
        labels = LabelDict(
            {
                "status": obj.status,
                "model": obj.__class__.__name__,
                "ip": self.extract_ip(obj),
                "id": str(obj.id)
            }
        )
        if obj.role:
            labels["role"] = obj.role

        utils.extract_tags(obj, labels)
        utils.extract_tenant(obj, labels)
        utils.extract_custom_fields(obj, labels)

        return labels.get_labels()
