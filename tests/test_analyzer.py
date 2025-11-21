"""Tests for the code analyzer module."""

import tempfile
from pathlib import Path

import pytest

from pyarchviz.analyzer import CodeAnalyzer


@pytest.fixture
def temp_project():
    """Create a temporary Python project for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create a simple module with a class
        (project_path / "simple.py").write_text("""
class SimpleClass:
    '''A simple class for testing.'''

    def __init__(self):
        self.value = 0

    def method(self, arg: int) -> int:
        '''A simple method.'''
        return arg * 2
""")

        # Create a module with imports
        (project_path / "with_imports.py").write_text("""
import os
from pathlib import Path
from typing import Any

def process_path(p: Path) -> str:
    '''Process a path.'''
    return str(p)
""")

        # Create a package structure
        pkg_dir = project_path / "mypackage"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module_a.py").write_text("""
class ClassA:
    def method_a(self):
        pass
""")
        (pkg_dir / "module_b.py").write_text("""
from mypackage.module_a import ClassA

class ClassB(ClassA):
    def method_b(self):
        pass
""")

        yield project_path


def test_analyzer_initialization(temp_project):
    """Test that analyzer initializes correctly."""
    analyzer = CodeAnalyzer(temp_project)
    assert analyzer.root_path == temp_project.resolve()
    assert analyzer.modules == {}
    assert analyzer.classes == {}
    assert analyzer.functions == {}
    assert analyzer.imports == {}


def test_analyze_finds_modules(temp_project):
    """Test that analyzer finds all Python modules."""
    analyzer = CodeAnalyzer(temp_project)
    analyzer.analyze()

    # Should find at least the modules we created
    assert len(analyzer.modules) >= 3
    assert any("simple" in name for name in analyzer.modules.keys())
    assert any("with_imports" in name for name in analyzer.modules.keys())


def test_analyze_finds_classes(temp_project):
    """Test that analyzer correctly identifies classes."""
    analyzer = CodeAnalyzer(temp_project)
    analyzer.analyze()

    # Check that SimpleClass was found
    simple_module = next(name for name in analyzer.modules.keys() if "simple" in name)
    assert simple_module in analyzer.classes
    assert len(analyzer.classes[simple_module]) == 1
    assert analyzer.classes[simple_module][0].name == "SimpleClass"


def test_analyze_finds_functions(temp_project):
    """Test that analyzer correctly identifies functions."""
    analyzer = CodeAnalyzer(temp_project)
    analyzer.analyze()

    # Check that process_path function was found
    imports_module = next(
        name for name in analyzer.modules.keys() if "with_imports" in name
    )
    assert imports_module in analyzer.functions
    assert len(analyzer.functions[imports_module]) == 1
    assert analyzer.functions[imports_module][0].name == "process_path"


def test_analyze_finds_imports(temp_project):
    """Test that analyzer correctly identifies imports."""
    analyzer = CodeAnalyzer(temp_project)
    analyzer.analyze()

    # Check that imports were found
    imports_module = next(
        name for name in analyzer.modules.keys() if "with_imports" in name
    )
    assert imports_module in analyzer.imports
    assert len(analyzer.imports[imports_module]) > 0

    # Check for specific imports
    import_names = [imp[0] for imp in analyzer.imports[imports_module]]
    assert "os" in import_names
    assert any("Path" in name for name in import_names)


def test_analyze_excludes_patterns(temp_project):
    """Test that analyzer respects exclude patterns."""
    # Create a test file
    (temp_project / "test_something.py").write_text("""
def test_function():
    pass
""")

    analyzer = CodeAnalyzer(temp_project)
    analyzer.analyze(exclude_patterns=["test_*"])

    # Test file should not be in modules
    assert not any("test_something" in name for name in analyzer.modules.keys())


def test_get_class_info(temp_project):
    """Test getting detailed class information."""
    analyzer = CodeAnalyzer(temp_project)
    analyzer.analyze()

    simple_module = next(name for name in analyzer.modules.keys() if "simple" in name)
    class_info = analyzer.get_class_info(simple_module, "SimpleClass")

    assert class_info["name"] == "SimpleClass"
    assert len(class_info["methods"]) >= 2  # __init__ and method
    assert any(m["name"] == "method" for m in class_info["methods"])
    assert "value" in class_info["attributes"]


def test_get_dependencies(temp_project):
    """Test getting module dependencies."""
    analyzer = CodeAnalyzer(temp_project)
    analyzer.analyze()

    dependencies = analyzer.get_dependencies()

    # Check that modules have dependencies
    assert len(dependencies) > 0

    # Module with imports should have dependencies
    imports_module = next(
        name for name in analyzer.modules.keys() if "with_imports" in name
    )
    assert imports_module in dependencies
    assert len(dependencies[imports_module]) > 0


def test_get_package_structure(temp_project):
    """Test getting hierarchical package structure."""
    analyzer = CodeAnalyzer(temp_project)
    analyzer.analyze()

    structure = analyzer.get_package_structure()

    # Should have a structure
    assert len(structure) > 0

    # Check for mypackage
    assert "mypackage" in structure or any(
        "mypackage" in str(k) for k in structure.keys()
    )


def test_analyzer_handles_syntax_errors():
    """Test that analyzer handles files with syntax errors gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create a file with syntax error
        (project_path / "broken.py").write_text("""
def broken_function(
    # Missing closing parenthesis
""")

        # Should not crash
        analyzer = CodeAnalyzer(project_path)
        analyzer.analyze()  # Should complete without raising exception


def test_module_name_conversion(temp_project):
    """Test that file paths are correctly converted to module names."""
    analyzer = CodeAnalyzer(temp_project)
    analyzer.analyze()

    # Check that module names don't include file extensions
    for module_name in analyzer.modules.keys():
        assert not module_name.endswith(".py")
        assert "__pycache__" not in module_name


def test_inheritance_detection(temp_project):
    """Test that class inheritance is detected."""
    analyzer = CodeAnalyzer(temp_project)
    analyzer.analyze()

    # Find ClassB which inherits from ClassA
    module_b = next(
        (name for name in analyzer.modules.keys() if "module_b" in name), None
    )
    if module_b:
        class_b_info = analyzer.get_class_info(module_b, "ClassB")
        assert "ClassA" in class_b_info["bases"]


def test_empty_directory():
    """Test analyzer on empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        analyzer = CodeAnalyzer(project_path)
        analyzer.analyze()

        assert len(analyzer.modules) == 0
        assert len(analyzer.classes) == 0
        assert len(analyzer.functions) == 0
