FROM netboxcommunity/netbox:v4.4.10

RUN apt -y update && apt -y install git

COPY ./plugin_requirements.txt /
RUN /usr/local/bin/uv pip install -r /plugin_requirements.txt || /opt/netbox/venv/bin/pip install  --no-warn-script-location -r /plugin_requirements.txt

CMD ["/bin/sh", "-c", \
     "/opt/netbox/netbox/manage.py load_initializer_data --path /etc/netbox/initializer-data && \
      /opt/netbox/docker-entrypoint.sh /opt/netbox/launch-netbox.sh"]
