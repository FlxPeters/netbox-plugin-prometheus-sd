from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions

from .serializers import TargetSerializer
from . import Target

from ipam.models import IPAddress


class TargetViewSet(viewsets.ViewSet):

    # Dirty workaround to ignore permissions for the moment
    _ignore_model_permissions = True

    def list(self, request):
        data = []

        for ip in IPAddress.objects.all():
            t = Target(str(ip))
            t.add_label("foo", "bar")
            data.append(t)

        serializer = TargetSerializer(instance=data, many=True)

        return Response(serializer.data)
