import os

from distutils.core import setup

pkginfo = {}
exec(open("src/__pkginfo__.py","r").read(),{},pkginfo)


def is_package(path):
    return (os.path.isdir(path) and os.path.isfile(os.path.join(path, '__init__.py')))

def find_packages(path, base=None, exclude=None):

    packages = []

    for root,dirs,files in os.walk(path):
        if "__init__.py" in files:
            if base is not None:
                root = root.replace(path,base)
            package = root.replace(os.sep,".")
            packages.append(package)

    return packages

packages = find_packages(path="src",base="hdf5viewer")

setup(name             = "hdf5viewer",
      version          = pkginfo["__version__"],
      description      = pkginfo["__description__"],
      long_description = pkginfo["__long_description__"],
      author           = pkginfo["__author__"],
      author_email     = pkginfo["__author_email__"],
      maintainer       = pkginfo["__maintainer__"],
      maintainer_email = pkginfo["__maintainer_email__"],
      url              = pkginfo["__url__"],
      license          = pkginfo["__license__"],
      packages         = packages,
      package_dir      = {"hdf5viewer" : "src"},
      platforms        = ['Unix','Windows'])
