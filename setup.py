#!/usr/bin/env python3
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="photog",
    version="3.0.0",
    author="Jaap Joris Vens",
    author_email="photog@jj.rtts.eu",
    description="Static photography website generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rtts/photog",
    license="AGPL3",
    entry_points={
        "console_scripts": [
            "photog=photog.__main__:main",
        ],
    },
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",  # noqa
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "Pillow",
        "Jinja2",
    ],
)
