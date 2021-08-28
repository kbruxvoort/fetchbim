from setuptools import setup, find_packages

# with open(file='README.md', 'r') as readme_handle:
#     long_description = readme_handle.read()

setup(
    name='fetchbim', 
    version='0.0.1',
    description='This package is for integrating various databases for Southwest Solutions Group BIM department',
    author='Kyle Bruxvoort',
    author_email='kbruxvoort@southwestsolutions.com',
    url='https://github.com/kbruxvoort/fetchbim', 
    packages=find_packages(exclude=('samples*', 'tests*')),
    # long_description=long_description,
    # long_description_content_type="text/markdown",
)