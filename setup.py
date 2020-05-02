from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='py_aurum',
    version='0.1.4',
    description='Aurum API to use in conjunction with Home Assistant Core.',
    long_description='Aurum Meetstekker API to use in conjunction with Home Assistant Core.',
    keywords='Home Assistant HA Core Aurum',
    url='https://github.com/bouwew/py_aurum',
    author='@bouwew',
    author_email='bouwe.s.westerdijk@gmail.com',
    license='MIT',
    packages=['py_aurum'],
    install_requires=[
        "asyncio",
        "aiohttp",
        "async_timeout",
        "requests",
        "lxml",
    ],
    zip_safe=False
)
