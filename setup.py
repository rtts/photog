#!/usr/bin/env python3
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'photog',
    version = '2.0.1',
    author = 'Jaap Joris Vens',
    author_email = 'jj@rtts.eu',
    description = 'Static photography website generator',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/rtts/photog',
    license = 'AGPL3',
    scripts = ['bin/photog'],
    include_package_data = True,
    packages = setuptools.find_packages(),
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ],
    install_requires = [
        'Pillow',
        'Jinja2',
        'natsort',
    ],
)
