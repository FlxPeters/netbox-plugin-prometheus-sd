def render_labels(labels: dict):
    """Prefix and replace invalid key chars for prometheus labels"""

    prefix = "__meta_netbox_"

    result = {}
    for key, val in labels.items():
        new_key = prefix + str(key.replace("-", "_").replace(" ", "_"))
        result[new_key] = val

    return result
