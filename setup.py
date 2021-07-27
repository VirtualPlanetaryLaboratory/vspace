# -*- coding: utf-8 -*-
from setuptools import setup
import os


# Setup!
setup(
    name="vspace",
    description="VPLANET parameter sweep helper",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VirtualPlanetaryLaboratory/vspace",
    author="Caitlyn Wilhelm",
    author_email="cwilhelm@uw.edu",
    license="MIT",
    packages=["vspace"],
    include_package_data=True,
    use_scm_version={
        "write_to": os.path.join("vspace", "vspace_version.py"),
        "write_to_template": '__version__ = "{version}"\n',
    },
    install_requires=["numpy", "matplotlib", "argparse",],
    entry_points={"console_scripts": ["vspace=vspace.vspace:main",],},
    setup_requires=["setuptools_scm"],
    zip_safe=False,
)
