ARG netbox_ver=latest

FROM netboxcommunity/netbox:${netbox_ver}

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /source
COPY .. /source

# Install the plugin in netbox
RUN /opt/netbox/venv/bin/pip install -r /source/requirements.txt
RUN /opt/netbox/venv/bin/pip install --editable /source

WORKDIR /opt/netbox/netbox/
