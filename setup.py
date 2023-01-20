import os
from setuptools import setup, find_packages


LONG_DESCRIPTION_SRC = 'README_PyPi.rst'


def read(file):
    with open(os.path.abspath(file), 'r', encoding='utf-8') as f:
        return f.read()


setup(
    name='my-magento',
    packages=find_packages(),
    version='2.0.1',
    license='MIT',
    description='Python Magento 2 REST API Wrapper',
    long_description=read(LONG_DESCRIPTION_SRC),
    long_description_content_type="text/x-rst; charset=UTF-8",
    author='Adam Korn',
    author_email='hello@dailykitten.net',
    url='https://www.github.com/TDKorn/my-magento',
    download_url="https://github.com/TDKorn/my-magento/tarball/master",
    keywords=["magento", "magento-api", "python-magento", "python", "python3", "magento-python", "pymagento", "py-magento", "magento2", "magento-2", "magento2-api"],
    install_requires=["requests"]
)
