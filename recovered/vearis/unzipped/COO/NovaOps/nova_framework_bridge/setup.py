from setuptools import setup, find_packages

setup(
    name="nova_framework_bridge",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.5",
        "asyncio>=3.4.3",
        "cryptography>=40.0.2",
        "pyyaml>=6.0",
        "python-dateutil>=2.8.2"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "launch-nova-bridge=src.launch:main"
        ]
    }
)