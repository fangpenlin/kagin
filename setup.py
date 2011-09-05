from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

extra = {}

version = '0.3'

setup(
    name='kagin',
    version=version,
    packages=find_packages(),
    install_requires=[
    ], **extra
)
