from setuptools import setup
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='my-magento',
    packages=['magento'],
    version='1.1.1',
    license='MIT',
    description='Python Magento 2 REST API Client',
    long_description=f"""{long_description}""",
    long_description_content_type='text/markdown',
    author='Adam Korn',
    author_email='hello@dailykitten.net',
    url='https://www.github.com/TDKorn/my-magento',
    download_url="https://github.com/TDKorn/my-magento/tarball/master",
    keywords=["magento", "magento-api", "python-magento", "python", "python3", "magento-python", "pymagento", "py-magento", "magento2", "magento-2", "magento2-api"],
    install_requires=["requests"]
)
