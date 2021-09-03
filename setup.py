from setuptools import setup

# Package metadata
NAME = "fetchbim"
DESCRIPTION = "This package is for integrating various databases for Southwest Solutions Group BIM department"
URL = "https://github.com/kbruxvoort/fetchbim.git"
EMAIL = "kbruxvoort@southwestsolutions.com"
AUTHOR = "Kyle Bruxvoort"
VERSION = "0.0.2"
REQUIRED = ["requests==2.26.0", "aiohttp==3.7.4.post0", "pymsteams==0.1.15"]


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    py_modules=["fetchbim"],
    install_requires=REQUIRED,
    include_package_data=True,
    license="MIT",
)
