from dcim.models.devices import Device
from netbox_prometheus_sd.api import mapper
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions

from .serializers import TargetSerializer
from .models import Target, TargetType


from ipam.models import IPAddress
from virtualization.models import VirtualMachine


class TargetViewSet(viewsets.ViewSet):

    # Dirty workaround to ignore permissions for the moment
    _ignore_model_permissions = True

    # todo: Add filters from request
    def list(self, request):
        data = list()

        for vm in VirtualMachine.objects.filter(primary_ip4__isnull=False).all():
            data.append(mapper.vm_to_target(vm))

        for device in Device.objects.filter(primary_ip4__isnull=False).all():
            data.append(mapper.device_to_target(device))

        for ip in IPAddress.objects.all():
            data.append(mapper.ip_to_target(ip))

        serializer = TargetSerializer(instance=data, many=True)

        return Response(serializer.data)
