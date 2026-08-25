from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="databunkerpro",
    version="0.1.8",
    author="Databunker team",
    author_email="hello@databunker.org",
    description="Python client library for DatabunkerPro API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/securitybunker/databunkerpro-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.34.2",
    ],
    extras_require={
        "dev": [
            "pytest>=9.1.1",
            "pytest-cov>=7.1.0",
            "black>=26.5.1",
            "isort>=8.0.1",
            "mypy>=2.3.1",
            "types-requests>=2.33.0.20260712",
        ],
    },
)
