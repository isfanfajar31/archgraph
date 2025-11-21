# Contributing to PyArchViz

Thank you for your interest in contributing to PyArchViz! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone. Please be considerate and constructive in your communications.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pyarchviz.git
   cd pyarchviz
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/torsteinsornes/pyarchviz.git
   ```

## Development Setup

PyArchViz uses `uv` for dependency management. Here's how to set up your development environment:

### Prerequisites

- Python 3.13 or higher
- `uv` package manager
- GraphViz (for testing GraphViz export functionality)

### Installation

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Install GraphViz** (if not already installed):
   - **Fedora**: `sudo dnf install graphviz`
   - **Ubuntu/Debian**: `sudo apt-get install graphviz`
   - **macOS**: `brew install graphviz`
   - **Windows**: Download from https://graphviz.org/download/

3. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate  # Windows
   ```

4. **Verify installation**:
   ```bash
   pyarchviz --version
   ```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes** - Fix issues in existing functionality
- **New features** - Add new diagram types, exporters, or analysis capabilities
- **Documentation** - Improve README, docstrings, or add examples
- **Tests** - Add or improve test coverage
- **Performance** - Optimize code for speed or memory usage
- **Refactoring** - Improve code structure and maintainability

### Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes** following the coding standards below

3. **Test your changes** thoroughly

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

5. **Keep your branch updated**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## Coding Standards

### Python Style

- Follow **PEP 8** style guide
- Use **type hints** for all function parameters and return values
- Use **new-style type annotations** (e.g., `list[int]` instead of `List[int]`)
- Maximum line length: **88 characters** (Black default)
- Use **descriptive variable names**

### Type Annotations

Always use modern type annotations:

```python
# Good ✓
def process_modules(modules: list[str], depth: int | None = None) -> dict[str, list[str]]:
    pass

# Bad ✗
from typing import List, Dict, Optional
def process_modules(modules: List[str], depth: Optional[int] = None) -> Dict[str, List[str]]:
    pass
```

### Documentation

- **Docstrings**: Use Google-style docstrings for all public functions, classes, and methods
- **Comments**: Write clear comments for complex logic
- **README**: Update README.md if adding new features

Example docstring:

```python
def generate_diagram(self, include_private: bool = False) -> nx.DiGraph:
    """Generate a class diagram from analyzed code.

    Args:
        include_private: Whether to include private members (starting with _)

    Returns:
        NetworkX directed graph representing the class structure

    Raises:
        ValueError: If no classes were found in the analyzed code
    """
    pass
```

### Code Organization

- **One class per file** for large classes
- **Group related functions** together
- **Imports**: Organize imports in three groups:
  1. Standard library
  2. Third-party packages
  3. Local imports
  
  Each group should be separated by a blank line and sorted alphabetically.

```python
import sys
from pathlib import Path

import click
import networkx as nx
from rich.console import Console

from pyarchviz.analyzer import CodeAnalyzer
from pyarchviz.generators import ClassDiagramGenerator
```

### Error Handling

- Use **specific exceptions** rather than generic ones
- Provide **helpful error messages**
- **Log warnings** for non-critical issues rather than failing silently

```python
# Good ✓
try:
    module = astroid.parse(content)
except astroid.AstroidSyntaxError as e:
    console.print(f"[yellow]Warning:[/yellow] Could not parse {file_path}: {e}")
    return None

# Bad ✗
try:
    module = astroid.parse(content)
except Exception:
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pyarchviz --cov-report=html

# Run specific test file
uv run pytest tests/test_analyzer.py

# Run specific test
uv run pytest tests/test_analyzer.py::test_analyze_simple_module
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files as `test_<module_name>.py`
- Name test functions as `test_<what_is_being_tested>`
- Use **pytest** fixtures for setup and teardown
- Aim for **>80% code coverage**

Example test:

```python
import pytest
from pathlib import Path
from pyarchviz.analyzer import CodeAnalyzer


def test_analyzer_finds_classes(tmp_path):
    """Test that analyzer correctly identifies classes in Python files."""
    # Create a temporary Python file
    test_file = tmp_path / "test_module.py"
    test_file.write_text("""
class MyClass:
    def method(self):
        pass
""")
    
    # Analyze the file
    analyzer = CodeAnalyzer(tmp_path)
    analyzer.analyze()
    
    # Assert results
    assert len(analyzer.classes) == 1
    assert "test_module" in analyzer.classes
    assert len(analyzer.classes["test_module"]) == 1
    assert analyzer.classes["test_module"][0].name == "MyClass"
```

## Pull Request Process

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated (README, docstrings)
- [ ] Commit messages are clear and descriptive
- [ ] Branch is rebased on latest main

### PR Description

Include in your pull request description:

1. **Summary** - What does this PR do?
2. **Motivation** - Why is this change needed?
3. **Changes** - List of specific changes made
4. **Testing** - How was this tested?
5. **Screenshots** - If applicable (especially for diagram output changes)
6. **Breaking changes** - Any backwards-incompatible changes?

### Review Process

1. A maintainer will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. Your contribution will be credited in the changelog

## Reporting Bugs

When reporting bugs, please include:

- **Python version** and OS
- **PyArchViz version**
- **Minimal code example** that reproduces the issue
- **Expected behavior** vs actual behavior
- **Error messages** or stack traces
- **Screenshots** if applicable

Use the GitHub issue template and label your issue as `bug`.

## Suggesting Features

For feature requests:

- **Check existing issues** to avoid duplicates
- **Describe the feature** clearly
- **Explain the use case** - why is this valuable?
- **Propose implementation** if you have ideas
- **Consider breaking it down** into smaller features

Label your issue as `enhancement` or `feature request`.

## Development Tips

### Testing Your Changes Locally

Test PyArchViz on a real project:

```bash
# Use the development version on a sample project
uv run pyarchviz generate ../some-project --output ./test-output
```

### Debugging

Add print statements or use Python debugger:

```python
import pdb; pdb.set_trace()
```

Or use Rich's console for debugging:

```python
from rich.console import Console
console = Console()
console.print(some_variable)
```

### Performance Testing

For performance-critical changes:

```python
import time

start = time.time()
# Your code here
elapsed = time.time() - start
print(f"Execution time: {elapsed:.2f}s")
```

## Questions?

If you have questions about contributing:

1. Check existing issues and discussions
2. Open a GitHub Discussion
3. Reach out to the maintainer at t.soernes@gmail.com

## Recognition

All contributors will be:

- Listed in the project's contributors page
- Credited in release notes
- Thanked in the README

Thank you for contributing to PyArchViz! 🎉