#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pyWeb3 : setup data
# Copyright (C) 2021  BitLogiK

from setuptools import setup, find_packages

VERSION = "0.1.0"

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    name="pyweb3",
    version=VERSION,
    description="Web3 RPC client for Python wallets",
    long_description=readme + "\n\n",
    long_description_content_type="text/markdown",
    keywords="web3 blockchain wallet cryptography",
    author="BitLogiK",
    author_email="contact@bitlogik.fr",
    url="https://github.com/bitlogik/pyWeb3",
    license="GPLv3",
    python_requires=">=3.6.1",
    install_requires=[
        "wsproto>=1.0.0",
        "h11>=0.9.0,<1",
    ],
    package_data={},
    include_package_data=False,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    zip_safe=False,
)
