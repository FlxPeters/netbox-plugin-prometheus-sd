from rest_framework.serializers import ModelSerializer, SerializerMethodField
from dcim.models import Device
from netbox_prometheus_sd.settings import TARGET_PORT

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
        if hasattr(obj, "primary_ip") and obj.primary_ip is not None:
            target = str(IPNetwork(obj.primary_ip.address).ip)
        else:
            target = obj.name
        return [f"{target}:{TARGET_PORT}"]

    def get_labels(self, obj):
        labels = {"status": obj.status}

        if hasattr(obj, "site") and obj.site is not None:
            labels["site"] = obj.site.name

        return render_labels(labels)
