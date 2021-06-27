from ipam.models import IPAddress
from virtualization.models import VirtualMachine, VMInterface
from django.contrib.contenttypes.models import ContentType


def create_vm(name, address, cluster, tenant):
    vm = VirtualMachine.objects.create(name=name, cluster=cluster, tenant=tenant)

    ip = IPAddress.objects.create(address=address)
    interface = VMInterface.objects.create(virtual_machine=vm, name="default")

    vm_interface_ct = ContentType.objects.get_for_model(VMInterface)

    ip.assigned_object_id = interface.id
    ip.assigned_object_type = vm_interface_ct
    ip.save()

    vm.primary_ip4 = ip
    vm.save()
