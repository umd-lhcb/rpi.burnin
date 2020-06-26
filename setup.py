#!/usr/bin/env python3

# Always prefer setuptools over distutils
from setuptools import setup
from os import path

# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

from rpi.burnin import name, version

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name=name,
    version=version,
    description="Rasberry Pi Python modules for burn-in.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/umd-lhcb/rpi.burnin",
    author="UMD LHCb group",
    author_email="lhcb@physics.umd.edu",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
    ],
    packages=["rpi", "rpi.burnin"],
    python_requires=">=3, <4",
    install_requires=["hidapi"],
)
