#!/usr/bin/env python

"""
Promobot Setup
"""

from setuptools import find_packages, setup
from setuptools.command.install import install

dev_requirements = [
    'flake8',
]

setup(
    name='promobot',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'notify2<0.4',
        'bs4<0.1',
        'dbus-python<1.3',
        'pymongo<3.11',
        'pyTelegramBotAPI<3.8',
    ],
    extras_require={
        'dev': dev_requirements
    },
    entry_points={
        'console_scripts': [
            'promobot=promobot.__main__:manage',
        ],
    },
    platforms='any',
    classifiers=[
        'Environment :: Console',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    keywords=[],
    license='No license',
    author='leandro2r',
    description='Promobot monitor keywords found in BR '
                'promotion sites managed by telegram chatbot.',
)