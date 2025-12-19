# Contributing to NOVA

We love your input! We want to make contributing to NOVA as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## We Develop with Github
We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## We Use [Github Flow](https://guides.github.com/introduction/flow/index.html)
Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Process

1. Clone the repository:
```bash
git clone https://github.com/TeamADAPT/ax_novas.git
cd ax_novas
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a branch:
```bash
git checkout -b feature/amazing-feature
```

5. Make your changes and commit:
```bash
git add .
git commit -m "Add amazing feature"
```

6. Push to your fork:
```bash
git push origin feature/amazing-feature
```

## Code Style

We use several tools to maintain code quality:

- `black` for code formatting
- `isort` for import sorting
- `mypy` for type checking
- `pylint` for linting

Run these tools before committing:

```bash
black .
isort .
mypy nova/
pylint nova/
```

## Testing

We use `pytest` for testing. Write tests for new code in the `tests/` directory:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=nova/ --cov-report=html
```

## Documentation

- Use docstrings for all public modules, functions, classes, and methods
- Follow Google style for docstrings
- Keep documentation up to date with code changes
- Add examples where appropriate

## Any contributions you make will be under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issue tracker](https://github.com/TeamADAPT/ax_novas/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/TeamADAPT/ax_novas/issues/new).

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## License
By contributing, you agree that your contributions will be licensed under its MIT License.

## References
This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md).
