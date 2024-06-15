# -*- coding: utf-8 -*-
# setup.py for cubedpandas

from setuptools import setup
from cubedpandas import *
from cubedpandas import VERSION as CUBEDPANDAS_VERSION


# ...to run the build and deploy process to pypi.org manually:
# 1. delete folder 'build'
# 2. python3 setup.py sdist bdist_wheel   # note: Wheel need to be installed: pip install wheel
# 3. twine upload -r  pypi dist/*         # note: Twine need to be installed: pip install twine

# ... via Github actions
# https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/

VERSION = CUBEDPANDAS_VERSION
DESCRIPTION = "CubedPandas: Multi-dimensional data analysis for Pandas dataframes."
LONG_DESCRIPTION = """
CubedPandas provides an easy, intuitive, fast and fun approach to perform multi-dimensional 
numerical data analysis & processing on Pandas dataframes. CubedPandas wraps almost any
dataframe into a multi-dimensional cube, which can be aggregated, sliced, diced, filtered, 
updated and much more. 

CubedPandas is inspired by OLAP cubes (online analytical processing), which are typically used
for reporting, business intelligence, data warehousing and financial analysis purposes.
 
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
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",

        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
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
    license='BSD 3-clause',
    platforms=['any'],
    zip_safe=True,
    python_requires='>=3.11',
    install_requires=[
        'numpy',
        'pandas',
        'pyarrow',
        'python-dateutil',
    ],
    test_suite="cubedpandas.tests",
    packages=['cubedpandas', 'tests'],
    project_urls={
        'Homepage': 'https://github.com/Zeutschler/cubedpandas',
        'Documentation': 'https://github.com/Zeutschler/cubedpandas',
        'GitHub': 'https://github.com/Zeutschler/cubedpandas',
    },
)