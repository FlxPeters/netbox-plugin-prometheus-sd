ARG netbox_ver=latest

FROM netboxcommunity/netbox:${netbox_ver}

RUN mkdir -p /source
COPY .. /source

# Install the plugin in netbox
RUN /usr/local/bin/uv pip install --editable /source || /opt/netbox/venv/bin/pip install  --no-warn-script-location /source

WORKDIR /opt/netbox/netbox/
