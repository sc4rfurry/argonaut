from setuptools import setup, find_packages

setup(
    name="argonaut",
    version="0.3.1",
    packages=find_packages(),
    install_requires=[
        "pyyaml",
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
        ],
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
