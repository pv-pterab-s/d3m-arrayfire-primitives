import os
import re
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call

PACKAGE_NAME = 'af_primitives'

def read_package_variable(key):
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join(PACKAGE_NAME, '__init__.py')
    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(' ')
            if parts and parts[0] == key:
                return parts[-1].strip("'")
    raise KeyError("'{0}' not found in '{1}'".format(key, module_path))


def install_arrayfire():
    arrayfire_version = '3.6.2'
    arrayfire_filename = f'ArrayFire-v{arrayfire_version}_Linux_x86_64.sh'

    check_call('mkdir -p /opt/arrayfire'.split())

    arrayfire_predownloaded_filename = os.path.join('/mnt', 'd3m', arrayfire_filename)
    if os.path.exists(arrayfire_predownloaded_filename):
        arrayfire_downloaded_filename = arrayfire_predownloaded_filename
    else:
        arrayfire_downloaded_filename = os.path.join('/tmp', arrayfire_filename)
        check_call((f'wget -P /tmp https://arrayfire.s3.amazonaws.com/{arrayfire_version}/ArrayFire-v{arrayfire_version}_Linux_x86_64.sh').split())
    check_call((f'bash {arrayfire_downloaded_filename} --skip-license --prefix=/opt/arrayfire').split())

    check_call(['bash', '-c', 'echo \'export LD_LIBRARY_PATH=/opt/arrayfire/lib64:$LD_LIBRARY_PATH\' >> ~/.bashrc'])
    check_call(['bash', '-c', 'echo \'export LD_PRELOAD=/usr/local/lib/libmkl_core.so:/usr/local/lib/libmkl_sequential.so\' >> ~/.bashrc'])


class PostDevelopStep(develop):
    def run(self):
        install_arrayfire()
        develop.run(self)


class PostInstallStep(install):
    def run(self):
        install_arrayfire()
        install.run(self)


setup(
    name=PACKAGE_NAME,
    version=read_package_variable('__version__'),
    description='ArrayFire Primitives',
    author=read_package_variable('__author__'),
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'arrayfire==3.6.20181017',
        'd3m==2019.11.10',
        'mkl==2021.1.1'
    ],
    url='https://github.com/arrayfire/d3m-arrayfire-primitives',
    keywords='d3m_primitive',
    entry_points={
        'd3m.primitives': [
            'classification.logistic_regression.ArrayFire = af_primitives.af_LogisticRegression:af_LogisticRegression',
            'classification.k_neighbors.ArrayFire = af_primitives.af_KNeigborsClassifier:af_KNeighborsClassifier'
        ],
    },
    cmdclass={
        'develop': PostDevelopStep,
        'install': PostInstallStep,
    },
)
