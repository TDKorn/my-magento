import os
from setuptools import setup


def get_description():
    file = os.path.abspath('README.md')
    with open(file, 'r', encoding='utf-8') as f:
        long_description = u'{}'.format(f.read())
        return long_description


long_description = get_description()


setup(
    name='my-magento',
    packages=['magento'],
    version='1.1.3',
    license='MIT',
    description='Python Magento 2 REST API Client and Wrapper',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Adam Korn',
    author_email='hello@dailykitten.net',
    url='https://www.github.com/TDKorn/my-magento',
    download_url="https://github.com/TDKorn/my-magento/tarball/master",
    keywords=["magento", "magento-api", "python-magento", "python", "python3", "magento-python", "pymagento", "py-magento", "magento2", "magento-2", "magento2-api"],
    install_requires=["requests"]
)
