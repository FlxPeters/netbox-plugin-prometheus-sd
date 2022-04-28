
FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /opt

RUN pip install --upgrade pip\
    && pip install poetry

# -------------------------------------------------------------------------------------
# Install NetBox
# -------------------------------------------------------------------------------------
ARG netbox_ver=master

RUN git clone --single-branch --branch ${netbox_ver} https://github.com/netbox-community/netbox.git /opt/netbox/ && \
    cd /opt/netbox/ && \
    pip install -r /opt/netbox/requirements.txt

# Make the django-debug-toolbar always visible when DEBUG is enabled,
# except when we're running Django unit-tests.
RUN echo "import sys" >> /opt/netbox/netbox/netbox/settings.py && \
    echo "TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'" >> /opt/netbox/netbox/netbox/settings.py && \
    echo "DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': lambda _: DEBUG and not TESTING }" >> /opt/netbox/netbox/netbox/settings.py

# -------------------------------------------------------------------------------------
# Install Netbox Plugin
# -------------------------------------------------------------------------------------
RUN mkdir -p /source
WORKDIR /source
COPY . /source
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

WORKDIR /opt/netbox/netbox/
