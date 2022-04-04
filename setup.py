from setuptools import find_packages, setup

setup(
    name="netbox_prometheus_sd",
    version="0.2",
    description="Netbox plugin which provide API for prometheus HTTP Service Discovery",
    url="https://github.com/zelfix/netbox-prometheus-sd",
    author="Andrei Protsenko",
    author_email="prondy@gmail.com",
    license="MIT",
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
