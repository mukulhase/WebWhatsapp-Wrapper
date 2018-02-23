"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import ast

# To use a consistent encoding
from codecs import open
import os
# Always prefer setuptools over distutils
from setuptools import setup

PACKAGE_NAME = 'webwhatsapi'

path = os.path.join(os.path.dirname(__file__), PACKAGE_NAME, '__init__.py')

with open(path, 'r') as file:
    t = compile(file.read(), path, 'exec', ast.PyCF_ONLY_AST)
    for node in (n for n in t.body if isinstance(n, ast.Assign)):
        if len(node.targets) != 1:
            continue

        name = node.targets[0]
        if not isinstance(name, ast.Name) or \
                name.id not in ('__version__', '__version_info__', 'VERSION'):
            continue

        v = node.value
        if isinstance(v, ast.Str):
            version = v.s
            break
        if isinstance(v, ast.Tuple):
            r = []
            for e in v.elts:
                if isinstance(e, ast.Str):
                    r.append(e.s)
                elif isinstance(e, ast.Num):
                    r.append(str(e.n))
            version = '.'.join(r)
            break

# Get the long description from the README file
with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='webwhatsapi',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,

    description='A python interface for Whatsapp Web',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/mukulhase/WhatsAPI',
    download_url='https://github.com/mukulhase/WhatsAPI/archive/{}.tar.gz'.format(version),

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
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Communications :: Chat',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='Whatsapp Chat Bot Chatbot Selenium Web Whatsapp API',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=[PACKAGE_NAME, ],
    install_requires=[
        'python-dateutil>=2.6.0',
        'selenium>=3.4.3',
        'six>=1.10.0',
        'python-axolotl',
        'pycrypto'
    ],
    extras_require={
    },
)
