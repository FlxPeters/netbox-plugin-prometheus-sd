FROM netboxcommunity/netbox:v3.4

RUN apt -y update && apt -y install git

COPY ./plugin_requirements.txt /
RUN /opt/netbox/venv/bin/pip install  --no-warn-script-location -r /plugin_requirements.txt
