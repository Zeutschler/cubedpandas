# -*- coding: utf-8 -*-
# setup.py for cubedpandas

from setuptools import setup
from setuptools import find_packages
from cubedpandas import VERSION as CUBEDPANDAS_VERSION


# ...to run the build and deploy process to pypi.org manually:
# 1. delete folder 'build'
# 1. empty folder 'dist'
# 2. python3 setup.py sdist bdist_wheel   # note: Wheel need to be installed: pip install wheel
# 3. twine upload -r  pypi dist/*         # note: Twine need to be installed: pip install twine

# ... via Github actions
# https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/

VERSION = CUBEDPANDAS_VERSION
DESCRIPTION = "CubedPandas - OLAP comfort meets Pandas power!"
LONG_DESCRIPTION = """
CubedPandas offer a new ***easy, fast & fun approach to navigate and analyze Pandas dataframes***. 
CubedPandas is inspired by the powerful concepts of OLAP (Online Analytical Processing) and MDX (Multi-Dimensional
Expressions) and aims to bring the comfort and power of OLAP to Pandas dataframes.

For novice users, CubedPandas can be a great help to get started with Pandas, as it hides some
of the complexity and verbosity of Pandas dataframes. For experienced users, CubedPandas
can be a productivity booster, as it allows you to write more compact, readable and
maintainable code.

Just give it a try...   
"""

setup(

    name="cubedpandas",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Topic :: Utilities",
        "Topic :: Database",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",

        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",

        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
    ],
    author="Thomas Zeutschler",
    keywords=['pandas', 'analysis', 'database', 'olap', 'planning', 'reporting', 'forecasting',
              'multidimensional', 'cube', ],
    author_email="cubedpandas@gmail.com",
    url="https://github.com/Zeutschler/cubedpandas",
    license='MIT',
    platforms=['any'],
    zip_safe=True,
    python_requires='>= 3.10',
    install_requires=[
        'numpy',
        'pandas',
        'python-dateutil',
    ],
    test_suite="cubedpandas.tests",
    packages=['cubedpandas', 'cubedpandas.context', 'cubedpandas.schema', 'tests'],
    project_urls={
        'Homepage': 'https://zeutschler.github.io/cubedpandas/',
        'Documentation': 'https://zeutschler.github.io/cubedpandas/',
        'GitHub': 'https://github.com/Zeutschler/cubedpandas',
    },
)