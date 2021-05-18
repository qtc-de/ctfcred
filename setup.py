#!/usr/bin/env python3

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    url='https://github.com/qtc-de/ctfcred',
    name='ctfcred',
    author='Tobias Neitzel (@qtc_de)',
    version='1.0.0',
    author_email='',

    description='CTF Credential Manager',
    long_description=long_description,
    long_description_content_type='text/markdown',

    packages=['ctfcred'],
    install_requires=[
                        'PyYAML',
                        'pyotp',
                        'pyperclip'
                     ],
    scripts=[
                'bin/ctfcred',
            ],
    classifiers=[
                    'Programming Language :: Python :: 3',
                    'Operating System :: Unix',
                    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                ],
)
