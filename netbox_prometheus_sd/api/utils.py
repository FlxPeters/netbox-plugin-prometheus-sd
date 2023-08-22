import json
from netaddr import IPNetwork


class LabelDict(dict):
    """Wrapper around dict to render labels"""

    @staticmethod
    def promsafestr(labelval: str):
        # add any special chars here that may appear in custom label names
        special_chars = " -/\\!"
        for special_char in special_chars:
            labelval = labelval.replace(special_char, '_')
        return labelval

    def get_labels(self):
        """Prefix and replace invalid key chars for prometheus labels"""
        return {
            "__meta_netbox_" + str(self.promsafestr(key)): val
            for key, val in self.items()
        }


def extract_tags(obj, labels):
    if hasattr(obj, "tags") and obj.tags is not None and len(obj.tags.all()):
        labels["tags"] = ",".join([t.name for t in obj.tags.all()])
        labels["tag_slugs"] = ",".join([t.slug for t in obj.tags.all()])


def extract_tenant(obj, labels: LabelDict):
    """Extract tenant and group"""
    if hasattr(obj, "tenant") and obj.tenant:
        labels["tenant"] = obj.tenant.name
        labels["tenant_slug"] = obj.tenant.slug

        if obj.tenant.group:
            labels["tenant_group"] = obj.tenant.group.name
            labels["tenant_group_slug"] = obj.tenant.group.slug


def extract_cluster(obj, labels: LabelDict):
    if hasattr(obj, "cluster") and obj.cluster is not None:
        labels["cluster"] = obj.cluster.name
        if obj.cluster.group:
            labels["cluster_group"] = obj.cluster.group.name
        if obj.cluster.type:
            labels["cluster_type"] = obj.cluster.type.name
        if obj.cluster.site:
            labels["site"] = obj.cluster.site.name
            labels["site_slug"] = obj.cluster.site.slug


def extract_primary_ip(obj, labels: LabelDict):
    if getattr(obj, "primary_ip", None) is not None:
        labels["primary_ip"] = str(IPNetwork(obj.primary_ip.address).ip)

    if getattr(obj, "primary_ip4", None) is not None:
        labels["primary_ip4"] = str(IPNetwork(obj.primary_ip4.address).ip)

    if getattr(obj, "primary_ip6", None) is not None:
        labels["primary_ip6"] = str(IPNetwork(obj.primary_ip6.address).ip)


def extracts_platform(obj, label: LabelDict):
    if hasattr(obj, "platform") and obj.platform is not None:
        label["platform"] = obj.platform.name
        label["platform_slug"] = obj.platform.slug


def extract_services(obj, labels: LabelDict):
    if (
        hasattr(obj, "services")
        and obj.services is not None
        and len(obj.services.all())
    ):
        labels["services"] = ",".join([srv.name for srv in obj.services.all()])


def extract_contacts(obj, labels: LabelDict):
    if (
        hasattr(obj, "contacts")
        and obj.contacts is not None
    ):
        for contact in obj.contacts.all():
            if hasattr(contact, "contact") and contact.contact is not None:
                labels[f"contact_{contact.priority}_name"] = contact.contact.name
            if contact.contact.email:
                labels[f"contact_{contact.priority}_email"] = contact.contact.email
            if contact.contact.comments:
                labels[f"contact_{contact.priority}_comments"] = contact.contact.comments
            if hasattr(contact, "role") and contact.role is not None:
                labels[f"contact_{contact.priority}_role"] = contact.role.name


def extract_rack(obj, labels: LabelDict):
    """Extract rack"""
    if hasattr(obj, "rack") and obj.rack:
        labels["rack"] = obj.rack.name


def extract_custom_fields(obj, labels: LabelDict):
    if hasattr(obj, "custom_field_data") and obj.custom_field_data is not None:
        for key, value in obj.custom_field_data.items():
            # Render primitive value as string representation
            if not hasattr(value, '__dict__'):
                labels["custom_field_" + key.lower()] = str(value)
            # Complex types are rendered as json
            else:
                labels["custom_field_" + key.lower()] = json.dumps(value)


def extract_prometheus_sd_config(obj, labels):
    prometheus_sd_config = getattr(obj, "_injected_prometheus_sd_config", {})

    metrics_path = prometheus_sd_config.get("metrics_path", None)
    if metrics_path and isinstance(metrics_path, str):
        labels["__metrics_path__"] = metrics_path

    scheme = prometheus_sd_config.get("scheme", None)
    if scheme and isinstance(scheme, str):
        labels["__scheme__"] = scheme


def extract_parent(obj, labels: LabelDict):
    labels['parent'] = obj.parent.name
    extract_primary_ip(obj.parent, labels)
    extract_tenant(obj.parent, labels)
    extract_cluster(obj.parent, labels)
    extract_contacts(obj.parent, labels)


def extract_service_ips(obj, labels: LabelDict):
    if (
        hasattr(obj, "ipaddresses")
        and obj.ipaddresses is not None
        and len(obj.ipaddresses.all())
    ):
        labels["ipaddresses"] = ",".join([str(ipaddr.address.ip) for ipaddr in obj.ipaddresses.all()])


def extract_service_ports(obj, labels: LabelDict):
    if (
        hasattr(obj, "ports")
        and obj.ports is not None
        and len(obj.ports)
    ):
        labels["ports"] = ",".join([str(port) for port in obj.ports])
