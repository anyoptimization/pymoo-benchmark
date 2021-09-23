import setuptools
from setuptools import setup

from pyrecorder.version import __version__

# ---------------------------------------------------------------------------------------------------------
# GENERAL
# ---------------------------------------------------------------------------------------------------------


__name__ = "pymoo"
__author__ = "Julian Blank"
__url__ = "https://pymoo.org"

data = dict(
    name=__name__,
    version=__version__,
    author=__author__,
    url=__url__,
    python_requires='>=3.7',
    author_email="blankjul@egr.msu.edu",
    description="pymoo: Benchmarking",
    license='Apache License 2.0',
    keywords="optimization, multi-objective",
    install_requires=['pymoo'],
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Mathematics'
    ]
)


# ---------------------------------------------------------------------------------------------------------
# OTHER METADATA
# ---------------------------------------------------------------------------------------------------------


# update the readme.rst to be part of setup
def readme():
    with open('README.rst') as f:
        return f.read()


def packages():
    return ["pymoo"] + ["pymoo." + e for e in setuptools.find_packages(where='pymoo')]


data['long_description'] = readme()
data['packages'] = packages()

# ---------------------------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------------------------

setup(**data)





