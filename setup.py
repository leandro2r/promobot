#!/usr/bin/env python

"""
Promobot Setup
"""

from setuptools import find_packages, setup

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
        'bs4<0.1',
        'pymongo<3.11',
        'pyTelegramBotAPI<3.8',
        'docker<4.4',
    ],
    extras_require={
        'dev': dev_requirements
    },
    entry_points={
        'console_scripts': [
            'promobot=promobot.__main__:main',
        ],
    },
    platforms='any',
    classifiers=[
        'Environment :: Console',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
    ],
    keywords=[],
    license='No license',
    author='leandro2r',
    description='Promobot monitor keywords found in BR '
                'promotion sites managed by telegram chatbot.',
)
