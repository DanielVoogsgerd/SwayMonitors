from setuptools import setup

url = "https://github.com/DanielVoogsgerd/SwayMonitors"
version = "0.0.1-devel"
readme = open('README.md').read()

setup(
    name="SwayMonitors",
    packages=["sway_monitors"],
    version=version,
    description="Provides a clear interface to interact with monitors and setups in sway",
    long_description=readme,
    include_package_data=True,
    author="Daniel Voogsgerd",
    author_email="daniel@voogsgerd.nl",
    url=url,
    install_requires=[],
    # download_url="{}/tarball/{}".format(url, version),
    license="ISC"
)
