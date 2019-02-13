import os

from setuptools import setup, find_packages

pkginfo = {}
exec(open("src/hdfviewer/__pkginfo__.py","r").read(),{},pkginfo)

# Add additional information to pkginfo
pkginfo["__classifiers__"] = ["Programming Language :: Python :: 3","License :: OSI Approved :: MIT License","Operating System :: OS Independent"]

pkginfo["__long_description_content_type__"] ="text/markdown"

with open("README.md","r") as f:
    pkginfo["__long_description__"] = f.read()

packages = find_packages("src")

setup(name                          = "hdfviewer",
      version                       = pkginfo["__version__"],
      description                   = pkginfo["__description__"],
      long_description              = pkginfo["__long_description__"],
      long_description_content_type = pkginfo["__long_description_content_type__"],
      author                        = pkginfo["__author__"],
      author_email                  = pkginfo["__author_email__"],
      maintainer                    = pkginfo["__maintainer__"],
      maintainer_email              = pkginfo["__maintainer_email__"],
      url                           = pkginfo["__url__"],
      license                       = pkginfo["__license__"],
      classifiers                   = pkginfo["__classifiers__"],
      packages                      = packages,
      package_dir                   = {"" : "src"},
      platforms                     = ['Unix','Windows'],
      install_requires              = ["numpy","matplotlib","h5py","jupyterlab","ipywidgets","ipympl"]
)
