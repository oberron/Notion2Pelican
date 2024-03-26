#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Created on 2024-Mar-26

@author: Oberron
"""
import re
from os.path import abspath, join, pardir
from setuptools import setup

fp_readme = abspath(join(__file__, pardir, "README.md"))
with open(fp_readme, "r", encoding="utf-8") as fi:
    long_description = fi.read()

with open("Notion2Pelican/__init__.py", "r") as fi:
    package_version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fi.read(), re.MULTILINE
    ).group(1)

setup(
    name='Notion2Pelican',
    version=package_version,
    author='oberron',
    author_email="one.annum@gmail.com",
    description='Import notion pages in pelican blogging format',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/oberron/Notion2Pelican',
    project_urls={
        "Bug Tracker": "https://github.com/oberron/Notion2Pelican/issues",
    },
    license='LICENSE',
    keywords='Notion Pelican',
    packages=['Notion2Pelican'],
    package_dir={'Notion2Pelican': abspath(join(__file__, pardir, "Notion2Pelican"))},
    python_requires='>=3.8',
    classifiers=[
                "Development Status :: 3 - Alpha",
                "Topic :: Utilities",
                "License :: OSI Approved :: MIT License",
                'Environment :: Console',
                'Intended Audience :: End Users/Desktop',
                'Intended Audience :: Developers',
                "Operating System :: OS Independent",
                "Programming Language :: Python :: 3.8",
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3.10",
                "Programming Language :: Python :: 3.11",
                "Topic :: Utilities",
    ],
    install_requires=["requests"],
    extras_require={
        "dev": [
            "coverage",
            "darglint",
            "python-dotenv",
            "flake8",
            "pyroma",
            "pelican",
            "pytest",
            "recommonmark",
            "sphinx",
            "sphinx_markdown_builder",
            "sphinx-rtd-theme",
            "tox",
            "twine",
            "wheel"]}
)
