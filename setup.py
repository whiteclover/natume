from setuptools import setup
import sys

from natume import __version__


setup(
    name = 'Natume',
    version = __version__,
    author = "Thomas Huang",
    description = "Web Blog Application",
    license = "GPL 2",
    keywords = "WSGI",
    url='https://github.com/thomashuang/natume',
    long_description=open('README.rst').read(),
    packages = ['natume'],
    classifiers=(
        "HTTP DSL SMOKER  TOOL",
        "License :: MIT",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: HTTP Tester"
        )
    )