from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='python_class_obfuscator',
    version='0.0.1',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    description='Python 3 class obfuscator'
)