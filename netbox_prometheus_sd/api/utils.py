from netaddr import IPNetwork


class LabelDict(dict):
    """Wrapper around dict to render labels"""

    def get_labels(self):
        """Prefix and replace invalid key chars for prometheus labels"""
        return {
            "__meta_netbox_" + str(key.replace("-", "_").replace(" ", "_")): val
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
    if hasattr(obj, "primary_ip") and obj.primary_ip is not None:
        labels["primary_ip"] = str(IPNetwork(obj.primary_ip.address).ip)


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
