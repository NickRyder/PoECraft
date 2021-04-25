REQUIRED = ["RePoE"]

from setuptools import setup
from setuptools_rust import RustExtension

setup(
    name="PoECraft",
    author="Nick Ryder",
    author_email="nick.ryder@berkeley.edu",
    url="https://github.com/NickRyder/PoECraft",
    download_url="https://github.com/NickRyder/PoECraft",
    description="Package for simulating PoE Crafting",
    version="0.1.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    packages=["PoECraft"],
    rust_extensions=[
        RustExtension("poe_craft.poe_craft", "Cargo.toml", debug=False),
    ],
    include_package_data=True,
    zip_safe=False,
)
