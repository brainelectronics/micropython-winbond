#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from setuptools import setup
import pathlib
import sdist_upip

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# load elements of version.py
exec(open(here / 'winbond' / 'version.py').read())

setup(
    name='micropython-winbond',
    version=__version__,
    description="Simple MicroPython Winbond library",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/brainelectronics/micropython-winbond',
    author='brainelectronics',
    author_email='info@brainelectronics.de',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],
    keywords='micropython, winbond, library',
    project_urls={
        'Bug Reports': 'https://github.com/brainelectronics/micropython-winbond/issues',
        'Source': 'https://github.com/brainelectronics/micropython-winbond',
    },
    license='MIT',
    cmdclass={'sdist': sdist_upip.sdist},
    packages=['winbond'],
    install_requires=[]
)
