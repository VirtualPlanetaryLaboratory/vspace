# -*- coding: utf-8 -*-
from setuptools import setup
import os


# from __future__ import absolute_import, division, print_function, unicode_literals
# import warnings
# import os
# import io
# import re



# try:
#     from setuptools import setup
#     from setuptools.command.install import install
#
#     setup
# except ImportError:
#     from distutils.core import setup
#
#     setup
#
# # Get the long description from the README
# def readme():
#     with open("README.md") as f:
#         return f.read()
#
#
# # Read, version funcs taken from:
# # https://github.com/ellisonbg/altair/blob/master/setup.py
# def read(path, encoding="utf-8"):
#     path = os.path.join(os.path.dirname(__file__), path)
#     with io.open(path, encoding=encoding) as fp:
#         return fp.read()
#
#
# def version(path):
#     """
#     Obtain the packge version from a python file e.g. pkg/__init__.py
#     See <https://packaging.python.org/en/latest/single_source_version.html>.
#     """
#     version_file = read(path)
#     version_match = re.search(
#         r"""^__version__ = ['"]([^'"]*)['"]""", version_file, re.M
#     )
#     if version_match:
#         return version_match.group(1)
#     raise RuntimeError("Unable to find version string.")
#
#
# VERSION = version("vspace/__init__.py")

# Setup!
setup(
    name="vspace",
    version=VERSION,
    description="VPLANET parameter sweep helper",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    url="https://github.com/VirtualPlanetaryLaboratory/vspace",
    author="Caitlyn Wilhelm",
    author_email="cwilhelm@uw.edu",
    license="MIT",
    packages=["vspace"],
    use_scm_version={
        "write_to": os.path.join("vspace", "vspace_version.py"),
        "write_to_template": '__version__ = "{version}"\n',
    },
    entry_points={"console_scripts": ["vspace=vspace.vspace:Argument",],},
    install_requires=["numpy", "matplotlib", "argparse",],
    include_package_data=True,
    zip_safe=False,
)
