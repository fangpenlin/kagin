from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

extra = {}

setup(name='kagin',
    packages=find_packages(),
    install_requires=[
    ], **extra
)
