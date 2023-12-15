from setuptools import setup, find_packages

VERSION = '0.1'
DESCRIPTION = 'ga fitness implementation package'
LONG_DESCRIPTION = 'implementation of the fitness function using helper classes and single responsibility principle'

setup(
    name="fitness",
    version=VERSION,
    author="Jonas Brockmöller, Tim Weigand",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'fitness', 'pygad'],
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Environment :: Machine Learning",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent"
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9"
    ],
)