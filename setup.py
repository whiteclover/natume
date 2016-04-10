from setuptools import setup
import os
import sys


readme = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

from natume import __version__


setup(
    name = 'Natume',
    version = __version__,
    author = "Thomas Huang",
    author_email='lyanghwy@gmail.com',
    description = "HTTP DSL Test Tool",
    license = "GPL 2",
    keywords = "http,test",
    url='https://github.com/whiteclover/natume',
    long_description=open('README.rst').read(),
    packages = ['natume'],
    classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
    )