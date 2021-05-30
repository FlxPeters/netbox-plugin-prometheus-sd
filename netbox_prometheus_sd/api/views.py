from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions

from .serializers import TargetSerializer
from . import Target

from ipam.models import IPAddress
from virtualization.models import VirtualMachine


class TargetViewSet(viewsets.ViewSet):

    # Dirty workaround to ignore permissions for the moment
    _ignore_model_permissions = True

    def list(self, request):
        data = []

        # Todo: refactor to testable mapper class
        for vm in VirtualMachine.objects.filter(primary_ip4__isnull=False).all():
            target = Target(str(vm.primary_ip))
            target.add_label("__meta_netbox_type", "virtual_machine")
            target.add_label("__meta_netbox_cluster", vm.cluster.name)
            if getattr(vm, "tenant", None):
                target.add_label("__meta_netbox_tenant", vm.tenant.name)
                target.add_label("__meta_netbox_tenant_slug", vm.tenant.slug)
                if vm.tenant.group:
                    target.add_label("tenant_group", vm.tenant.group.name)
                    target.add_label("tenant_group_slug", vm.tenant.group.slug)
            data.append(target)

        for ip in IPAddress.objects.all():
            target = Target(str(ip))
            target.add_label("__meta_netbox_type", "ip")
            data.append(target)

        serializer = TargetSerializer(instance=data, many=True)

        return Response(serializer.data)
