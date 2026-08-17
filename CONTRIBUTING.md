# Contributing to Unmark

Thank you for your interest in contributing to **Unmark**! We welcome contributions from researchers, engineers, and community developers.

## How to Contribute

### 1. Reporting Bugs
- Search the [GitHub Issues](https://github.com/xuange520/unmark/issues) to verify if the issue has already been reported.
- If not, create a new issue with detailed reproduction steps, environment details (Python version, PyTorch version, OS), and sample text.

### 2. Suggesting Enhancements
- Open a feature request issue explaining the motivation, use case, and proposed interface.

### 3. Submitting Pull Requests (PRs)
1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/unmark.git
   cd unmark
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
5. Ensure all tests pass:
   ```bash
   pytest tests/
   ```
6. Commit your changes following standard commit conventions:
   ```bash
   git commit -m "feat: add support for back-translation scrubbing strategy"
   ```
7. Push to your branch and submit a Pull Request to `main`.

## Code Style
- Follow PEP 8 guidelines.
- Add clear type hints and docstrings where appropriate.

## License
By contributing to `Unmark`, you agree that your contributions will be licensed under the **Apache License 2.0**.
