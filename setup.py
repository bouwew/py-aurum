import codecs
import os.path
from setuptools import setup

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='py_aurum',
    version=get_version("py_aurum/__init__.py"),
    description='Aurum API to use in conjunction with Home Assistant Core.',
    long_description='Aurum Meetstekker API to use in conjunction with Home Assistant Core.',
    keywords='Home Assistant HA Core Aurum',
    url='https://github.com/bouwew/py_aurum',
    download_url='https://github.com/bouwew/py-aurum/archive/v1.0.1.tar.gz',
    author='@bouwew',
    author_email='bouwe.s.westerdijk@gmail.com',
    license='MIT',
    packages=['py_aurum'],
    install_requires=[
        "asyncio",
        "aiohttp",
        "async_timeout",
        "defusedxml",
    ],
    zip_safe=False
)
