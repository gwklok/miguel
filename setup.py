import os
import codecs

from setuptools import setup

import miguel


def read(filename):
    """Read and return `filename` in root dir of project and return string"""
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, filename), 'r').read()


install_requires = read("requirements.txt").split()
long_description = read('README.md')


setup(
    name="miguel",
    version=miguel.__version__,
    url='https://github.com/mesos-magellan/miguel',
    license='MIT License',
    author='Hamza Faran',
    description=('CLI for Faleiro Scheduler'),
    long_description=long_description,
    packages=[],
    install_requires = install_requires,
    entry_points={'console_scripts': [
        'miguel = miguel:main'
    ]}
)
