from setuptools import setup, find_packages

VERSION = '2.5.2+Zeus'

setup(
   name="herbga",
   version=VERSION,
   author="Tim Weigand & Jonas Brockmöller",
   description="Implementation of the PyGAD algorithm for Herbalife",
   packages=find_packages(),
   include_package_data=True,
   classifiers=[
        "Development Status :: 1 - Alpha",
        "Environment :: Machine Learning",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent"
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9"
   ],
   install_requires=[
                     "pygad >= 3.2.0",
                     "numpy >= 1.26.0",
                     "jproperties >= 2.1.1",
                     "sqlalchemy >= 1.4.50",
                     "psycopg2-binary >= 2.9.9"
                     ],
   python_requires='>=3.9',
)
