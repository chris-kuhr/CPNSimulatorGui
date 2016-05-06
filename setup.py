'''
Created on Mar 31, 2016

@author: christoph
'''
from setuptools import find_packages, setup
setup(
      name="pyPetriNets", 
      version="0.0.1",
      description = "PetriNet Simulator Gui",
      author='Christoph Kuhr',
      author_email='info@christophkuhr.de',
      url='http://www.christophkuhr.de',
      classifiers = [
                     "Programming Language :: Python :: 3.4",
                     "Development Status :: 2 - Pre-Alpha",
                     "Environment :: X11 Applications :: Qt",
                     "Framework :: Setuptools Plugin",
                     "Intended Audience :: Education",
                     "Intended Audience :: Science/Research",
                     "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                     "Natural Language :: English",
                     "Operating System :: POSIX :: Linux",
                     "Topic :: Scientific/Engineering :: Visualization"
                     ],
      install_requires=[
                    "SNAKES >= 0.9.17",
                    "lxml >= 3.3.3",
                    "PyQt4 >= 4.10.4"
                    ]
)
