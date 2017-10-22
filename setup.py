"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='webwhatsapi',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.0.3',

    description='A python interface for Whatsapp Web',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/mukulhase/WhatsAPI',
    download_url='https://github.com/mukulhase/WhatsAPI/archive/0.1.2.tar.gz',  # I'll explain this in a second

    # Author details
    author='Mukul Hase',
    author_email='mukulhase@gmail.com',
    include_package_data=True,

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Communications :: Chat',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='Whatsapp Chat Bot Chatbot Selenium Web Whatsapp API',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'beautifulsoup4>=4.6.0',
        'bs4>=0.0.1',
        'python-dateutil>=2.6.0',
        'selenium>=3.4.3',
        'six>=1.10.0',
    ],
    extras_require={
    },
)
