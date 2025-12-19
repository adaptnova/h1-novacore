from setuptools import setup, find_packages

setup(
    name="nova",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "openai>=1.3.0",
        "anthropic>=0.3.0",
        "langchain>=0.1.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.8.0",
        "redis>=5.0.0",
        "pymongo>=4.4.0",
        "prometheus-client>=0.17.0",
        "opentelemetry-api>=1.18.0",
        "opentelemetry-sdk>=1.18.0",
        "structlog>=23.1.0",
        "PyYAML>=6.0.0",
        "requests>=2.28.0",
        "rich>=13.4.0",
        "typer>=0.9.0",
    ],
    python_requires=">=3.11",
)
