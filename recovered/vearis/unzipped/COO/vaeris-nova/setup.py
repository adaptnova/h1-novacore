from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="vaeris-nova",
    version="0.1.0",
    author="NovaOps",
    author_email="info@novaops.ai",
    description="Advanced autonomous AI super agent using LangChain and LangGraph",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/novaops/vaeris-nova",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "vaeris-nova=vaeris_nova.cli:main",
        ],
    },
)