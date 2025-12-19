"""
Setup configuration for the haystack_rag package.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read requirements
def read_requirements(filename: str) -> list[str]:
    """Read requirements from file."""
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read long description
def read_long_description() -> str:
    """Read README.md for long description."""
    with open("README.md", encoding="utf-8") as f:
        return f.read()

# Project metadata
NAME = "haystack_rag"
DESCRIPTION = "Retrieval Augmented Generation implementation using Haystack"
AUTHOR = "Your Organization"
AUTHOR_EMAIL = "your.email@example.com"
URL = "https://github.com/yourusername/haystack-rag"
PYTHON_REQUIRES = ">=3.8"

# Version management
def get_version() -> str:
    """Get package version from VERSION.txt."""
    with open("VERSION.txt") as f:
        return f.read().strip()

# Main setup configuration
setup(
    name=NAME,
    version=get_version(),
    description=DESCRIPTION,
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=PYTHON_REQUIRES,
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.1.0",
            "mkdocstrings>=0.22.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "httpx>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "haystack-rag=haystack_rag.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords=[
        "haystack",
        "rag",
        "retrieval-augmented-generation",
        "nlp",
        "search",
        "ai",
        "machine-learning",
    ],
    project_urls={
        "Documentation": "https://github.com/yourusername/haystack-rag/docs",
        "Source": "https://github.com/yourusername/haystack-rag",
        "Tracker": "https://github.com/yourusername/haystack-rag/issues",
    },
    include_package_data=True,
    zip_safe=False,
)
