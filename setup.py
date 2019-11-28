from setuptools import find_packages, setup
from distutils.core import setup
from Cython.Build import cythonize

# Package meta-data.
NAME = 'PoECraft'
DESCRIPTION = 'Package for simulating PoE Crafting'
URL = 'https://github.com/NickRyder/PoECraft'
EMAIL = ''
AUTHOR = 'Nick Ryder'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '1.0.0'

# What packages are required for this module to be executed?
REQUIRED = [
   'RePoE'
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    py_modules=find_packages(),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='proprietary',
    ext_modules=cythonize("PoECraft/performance/prng.pyx")
)