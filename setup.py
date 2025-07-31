#!/usr/bin/env python

"""
Promobot Setup
"""

from setuptools import find_packages, setup

dev_requirements = [
    'flake8',
    'pylint',
]

setup(
    name='promobot',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'bs4<0.1',
        'pymongo<4.1',
        'pyTelegramBotAPI<4.7',
        'requests<2.33',
        'kubernetes<19.16',
        'selenium<4.2',
        'selenium-stealth<1.1',
        'psutil<6.1',
        'pymongo[srv]',
        'PyYAML<6.1',
        'swiftshadow<2.3',
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
        'Programming Language :: Python :: 3.9',
    ],
    keywords=[],
    license='No license',
    author='Leandro Rodrigues',
    author_email='leandro.l2r@gmail.com',
    description='Promobot monitors promotion sites by searching keyword'
                ' occurrences and reporting them to a Telegram channel.',
    url='https://github.com/leandro2r/promobot',
)
