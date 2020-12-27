from setuptools import setup, find_packages
from os import path

setup(
    name="dreamcatcher",
    version="0.0.1",
    author="Kodey Converse",
    author_email="kodey@conve.rs",
    packages=find_packages(exclude=["tests"]),
    entry_points={"console_scripts": ["dreamcatcher=dreamcatcher.cli:cli"]},
    install_requires=["attrs", "requests"],
)
