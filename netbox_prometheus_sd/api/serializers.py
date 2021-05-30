from rest_framework import serializers


class TargetSerializer(serializers.Serializer):
    targets = serializers.ListField(serializers.CharField())
    labels = serializers.DictField(child=serializers.CharField())
