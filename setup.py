#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import setuptools

package_name = "add_service"
here = os.path.dirname(os.path.realpath(__file__))

if os.path.isfile("requirements.txt"):
    with open("requirements.txt") as f:
        requirements = [line.strip() for line in f]
else:
    requirements = []

with open("README.md", "rb") as f:
    long_description = f.read().decode("utf-8")

info = {}
with open(os.path.join(here, package_name, "main.py"), "rb") as f:
    exec(f.read(), info)


setuptools.setup(
    name=package_name,
    version=info["__version__"],
    author=info["__author__"],
    author_email=info["__author_email__"],
    description=info["__description__"],
    long_description=info["__description__"],
    long_description_content_type="text/markdown",
    url=info["__url__"],
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=info["__classifiers__"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "add_service=add_service.main:main",
        ],
    },
)
