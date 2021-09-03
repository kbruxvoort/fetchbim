from setuptools import setup

# Package metadata
NAME = "fetchbim"
DESCRIPTION = "This package is for integrating various databases for Southwest Solutions Group BIM department"
URL = "https://github.com/kbruxvoort/fetchbim.git"
EMAIL = "kbruxvoort@southwestsolutions.com"
AUTHOR = "Kyle Bruxvoort"
VERSION = "0.0.2"
REQUIRED = ["requests", "pymsteams", "aiohttp", "tqdm"]


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
