from setuptools import setup

setup(
    name='MyMagento',
    packages=['magento'],
    version='1.1',
    license='MIT',
    description='Python Magento 2 REST API Client',
    author='Adam Korn',
    author_email='hello@dailykitten.net',
    url='https://www.github.com/TDKorn/my-magento',
    download_url="https://github.com/TDKorn/my-magento/tarball/master",
    keywords=["magento", "magento-api", "python-magento", "python", "python3", "magento-python", "pymagento", "py-magento", "magento2", "magento-2", "magento2-api"],
    install_requires=["requests", "beautifulsoup4"]
)
