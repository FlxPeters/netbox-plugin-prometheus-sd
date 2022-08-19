from dcim.models.devices import Device
from netbox.api.viewsets import NetBoxModelViewSet
from netbox_prometheus_sd.settings import CUSTOM_FIELD_NAME
from dcim.filtersets import DeviceFilterSet
from .serializers import PrometheusDeviceSerializer


class DeviceViewSet(NetBoxModelViewSet):
    queryset = Device.objects.filter(custom_field_data__contains={CUSTOM_FIELD_NAME: True})
    filterset_class = DeviceFilterSet
    serializer_class = PrometheusDeviceSerializer
    pagination_class = None
