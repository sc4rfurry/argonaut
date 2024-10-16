# /usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys

# Define optional dependencies
extras_require = {
    "windows": ["pyreadline3"],
}

# Define conditional dependencies
install_requires = [
    "pyyaml", "asyncio", 
]

if sys.platform == "win32":
    install_requires.append("pyreadline3")

setup(
    name="argonautCli",
    version="1.2.0",
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
        ],
        **extras_require,
    },
    author="sc4rfurry",
    author_email="akalucifr@protonmail.ch",
    description="A custom argument parsing library for CLI applications with a focus on simplicity and ease of use. ArgøNaut is designed to make it easy to create powerful and flexible command-line interfaces.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sc4rfurry/argon4ut",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
