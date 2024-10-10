ARG netbox_ver=latest

FROM netboxcommunity/netbox:${netbox_ver}

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /source
COPY .. /source

# Install Python build dependencies
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -qq \
    && apt-get upgrade \
      --yes -qq --no-install-recommends \
    && apt-get install \
      --yes -qq --no-install-recommends \
      build-essential \
      python3-dev \
      python3-pip

# Install the plugin in netbox
RUN /opt/netbox/venv/bin/pip install -r /source/requirements.txt
RUN /opt/netbox/venv/bin/pip install --editable /source

WORKDIR /opt/netbox/netbox/
