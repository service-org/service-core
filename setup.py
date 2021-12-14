#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from pathlib import Path
from setuptools import setup, find_packages

readme = Path.cwd().joinpath('LETSGO.md').open().read()

setup(
    version='0.0.1',
    name='service-core',
    author='forcemain@163.com',
    url='https://github.com/service-org/',
    license='Apache License, Version 2.0',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=[
        'eventlet==0.33.0', 'PyYAML==5.4.1',
        'typing-extensions==3.10.0.0', 'pydantic==1.8.2'
    ],
    classifiers=[
        'Typing :: Typed',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': ['core=service_core.cli.main:main']
    }
)
