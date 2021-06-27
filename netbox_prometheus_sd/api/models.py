from enum import Enum


class TargetType(Enum):
    VIRTUAL_MACHINE = "vm"
    DEVICE = "device"
    IP_ADDRESS = "ip_address"


class Target:
    """ Representation of a Prometheus SD target """

    def __init__(self, address):
        self.targets = [address]
        self.labels = dict()

    def add_label(self, key, value):
        """ Add a netbox prefixed meta label to the host """
        # Replace invalid charaters in label name
        key = key.replace("-", "_").replace(" ", "_")
        self.labels[f"%s_%s" % ("__meta_netbox", key)] = value
