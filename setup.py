from setuptools import setup, find_packages

__version__ = "1.0.3"

with open("README.md") as f:
    long_description = f.read()

setup(
    name="BitFieldArray",
    version=__version__,
    author="Jonathan",
    author_email="pybots.il@gmail.com",
    description="TA module to convert arrays into bit field array. "
                "Usually useful for transmitting arrays and structures over the network.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonatan1609/BitFieldArray",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5"
)