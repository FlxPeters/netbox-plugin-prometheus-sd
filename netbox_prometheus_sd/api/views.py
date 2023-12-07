from dcim.models.devices import Device
from netbox.api.viewsets import NetBoxModelViewSet
from netbox_prometheus_sd.settings import CUSTOM_FIELD_NAME
from dcim.filtersets import DeviceFilterSet
from .serializers import PrometheusDeviceSerializer, GnmicDeviceSerializer


class PrometheusDeviceViewSet(NetBoxModelViewSet):
    queryset = Device.objects.filter(custom_field_data__contains={CUSTOM_FIELD_NAME: True})
    filterset_class = DeviceFilterSet
    serializer_class = PrometheusDeviceSerializer
    pagination_class = None


class GnmicDeviceViewSet(NetBoxModelViewSet):
    queryset = Device.objects.filter(custom_field_data__contains={CUSTOM_FIELD_NAME: True})
    filterset_class = DeviceFilterSet
    serializer_class = GnmicDeviceSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        response = super(NetBoxModelViewSet, self).list(request, *args, **kwargs)  # call the original 'list'
        response.data = {data['name']: data for data in response.data}  # replace the list with a dict
        return response
