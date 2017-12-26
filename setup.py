from setuptools import setup, find_packages

from vk_raid_defender import __author__, __version__, __description__
from os.path import abspath, dirname, join

with open(join(abspath(dirname(__file__)), 'README.md')) as file:
    long_description = file.read()


setup(
    name='vk-raid-defender',
    version=__version__,
    description=__description__,
    long_description=long_description,
    url='https://github.com/r4rdsn/vk-raid-defender',
    author=__author__,
    author_email='rchrdsn@protonmail.ch',
    license='MIT',
    keywords='vk bot',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    install_requires=['vk_api', 'requests'],
    extras_require={'socks': ['PySocks']},
    python_requires='==3.6.*',
    entry_points={
        'console_scripts': [
            'vk-raid-defender=vk_raid_defender.cli.cli:main',
        ],
    }
)
