from os import path
from codecs import open
from setuptools import setup, find_packages


_NAME = "frangitrondmx"
_VERSION = "0.15.3"
_DESCRIPTION = "Frangitron - DMX Controller"

_here = path.abspath(path.dirname(__file__))
_readme_filepath = path.join(_here, 'README.md')
_requirements_filepath = path.join(_here, 'requirements.txt')


if path.isfile(_readme_filepath):
    with open(_readme_filepath, encoding='utf-8') as readme_file:
        _long_description = readme_file.read()
else:
    _long_description = 'Unable to load README.md'


if path.isfile(_requirements_filepath):
    with open(_requirements_filepath) as requirements_file:
        _requirements = requirements_file.readlines()
else:
    _requirements = list()

dependency_links = []
install_requires = []

for item in _requirements:
    if item.startswith('git+'):
        dependency_links.append(str(item))
        install_requires.append(item.split("/")[-1].split(".git")[0])
    else:
        install_requires.append(str(item))

setup(
    name=_NAME,
    version=_VERSION,
    description=_DESCRIPTION,
    author="Mr Frangipane",
    author_email="mr@frangipane.me",
    packages=find_packages(exclude=['tests']),
    install_requires=install_requires,
    dependency_links=dependency_links,
    include_package_data=True
)
