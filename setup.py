from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
VERSION = "0.0.1"

setup(
    name="scihub",
    version=VERSION,
    description="A tool to download papers from sci-hub using selenium",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="sci-hub selenium",
    author="RhythmLian",
    url="https://github.com/Rhythmicc/scihub",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=["Qpro", "selenium", "QuickStart_Rhy"],
    entry_points={
        "console_scripts": [
            "scihub = scihub.main:main",
        ]
    },
)
