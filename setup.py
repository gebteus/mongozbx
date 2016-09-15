import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('mongozbx.py', 'r') as fd:
    version = re.search(
        r'^_SCRIPT_VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(), re.MULTILINE).group(1)

setup(
    name='mongozbx',
    version=version,
    py_modules=['mongozbx'],
    entry_points={
        'console_scripts': 'mongozbx=mongozbx:main',
    },
    install_requires=[
        'pymongo',
        'bson'
    ]
)