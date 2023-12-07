from rest_framework.serializers import ModelSerializer, SerializerMethodField
from dcim.models import Device
from netbox_prometheus_sd.settings import TARGET_PORT, GNMIC_TARGET_PORT

from netaddr import IPNetwork

from .utils import render_labels


class PrometheusDeviceSerializer(ModelSerializer):
    """Serialize a device to Prometheus target representation"""

    class Meta:
        model = Device
        fields = ["targets", "labels"]

    targets = SerializerMethodField(read_only=True)
    labels = SerializerMethodField(read_only=True)

    def get_targets(self, obj):
        if obj.primary_ip is not None:
            target = IPNetwork(obj.primary_ip.address).ip
        else:
            target = obj.name
        return [f"{target}:{TARGET_PORT}"]

    def get_labels(self, obj):
        labels = {"status": obj.status}
        labels["name"] = obj.name
        if obj.site is not None:
            labels["site"] = obj.site.slug

        return render_labels(labels)


class GnmicDeviceSerializer(ModelSerializer):
    """Serialize a device to gNMIc target representation"""

    class Meta:
        model = Device
        fields = ["name", "address"]

    name = SerializerMethodField(read_only=True)
    address = SerializerMethodField(read_only=True)

    def get_name(self, obj):
        return obj.name

    def get_address(self, obj):
        if obj.primary_ip is not None:
            address = IPNetwork(obj.primary_ip.address).ip
        else:
            address = obj.name
        return f"{address}:{GNMIC_TARGET_PORT}"
