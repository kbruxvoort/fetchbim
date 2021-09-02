from setuptools import setup, find_packages

setup(
    name='fetchbim', 
    version='0.0.1',
    description='This package is for integrating various databases for Southwest Solutions Group BIM department',
    author='Kyle Bruxvoort',
    author_email='kbruxvoort@southwestsolutions.com',
    url='https://github.com/kbruxvoort/fetchbim.git', 
    packages=find_packages(exclude=('samples*', 'tests*')),
)