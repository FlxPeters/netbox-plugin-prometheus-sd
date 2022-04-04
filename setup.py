from setuptools import find_packages, setup

setup(
    name="netbox_prometheus_sd",
    version="0.1",
    description="Netbox plugin which provide API for prometheus HTTP Service Discovery",
    url="https://github.com/netbox-community/netbox-animal-sounds",
    author="Andrei Protsenko",
    author_email="andrei.protsenko@adyen.com",
    license="MIT",
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
