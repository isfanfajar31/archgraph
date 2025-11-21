"""Code analyzer module for parsing Python source files and extracting structural information."""

import ast
from pathlib import Path
from typing import Any

import astroid
from astroid import nodes


class CodeAnalyzer:
    """Analyzes Python code to extract architectural information."""

    def __init__(self, root_path: str | Path):
        """Initialize the code analyzer.

        Args:
            root_path: Root directory of the Python project to analyze
        """
        self.root_path = Path(root_path).resolve()
        self.modules: dict[str, nodes.Module] = {}
        self.classes: dict[str, list[nodes.ClassDef]] = {}
        self.functions: dict[str, list[nodes.FunctionDef]] = {}
        self.imports: dict[str, list[tuple[str, str | None]]] = {}
        self.call_relationships: list[tuple[str, str]] = []

    def analyze(self, exclude_patterns: list[str] | None = None) -> None:
        """Analyze all Python files in the root path.

        Args:
            exclude_patterns: List of glob patterns to exclude (e.g., ['test_*', '*_test.py'])
        """
        exclude_patterns = exclude_patterns or []
        python_files = self._find_python_files(exclude_patterns)

        for file_path in python_files:
            self._analyze_file(file_path)

    def _find_python_files(self, exclude_patterns: list[str]) -> list[Path]:
        """Find all Python files in the root path.

        Args:
            exclude_patterns: Patterns to exclude

        Returns:
            List of Python file paths
        """
        python_files = []
        for path in self.root_path.rglob("*.py"):
            # Skip if matches any exclude pattern
            if any(path.match(pattern) for pattern in exclude_patterns):
                continue
            # Skip __pycache__ and .venv directories
            if "__pycache__" in path.parts or ".venv" in path.parts:
                continue
            python_files.append(path)
        return python_files

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file.

        Args:
            file_path: Path to the Python file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse with astroid for better semantic analysis
            module = astroid.parse(content, module_name=str(file_path))
            module_name = self._get_module_name(file_path)

            self.modules[module_name] = module
            self.classes[module_name] = []
            self.functions[module_name] = []
            self.imports[module_name] = []

            # Extract classes, functions, and imports
            for node in module.body:
                if isinstance(node, nodes.ClassDef):
                    self.classes[module_name].append(node)
                elif isinstance(node, nodes.FunctionDef):
                    self.functions[module_name].append(node)
                elif isinstance(node, (nodes.Import, nodes.ImportFrom)):
                    self._extract_imports(node, module_name)

            # Extract call relationships
            self._extract_calls(module, module_name)

        except Exception as e:
            # Log error but continue with other files
            print(f"Warning: Could not analyze {file_path}: {e}")

    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name.

        Args:
            file_path: Path to Python file

        Returns:
            Module name (e.g., 'package.subpackage.module')
        """
        relative_path = file_path.relative_to(self.root_path)
        parts = list(relative_path.parts[:-1]) + [relative_path.stem]

        # Remove __init__ from the end
        if parts[-1] == "__init__":
            parts = parts[:-1]

        return ".".join(parts) if parts else "__main__"

    def _extract_imports(
        self, node: nodes.Import | nodes.ImportFrom, module_name: str
    ) -> None:
        """Extract import statements.

        Args:
            node: Import or ImportFrom node
            module_name: Name of the module containing the import
        """
        if isinstance(node, nodes.Import):
            for name, alias in node.names:
                self.imports[module_name].append((name, alias))
        elif isinstance(node, nodes.ImportFrom):
            base_module = node.modname or ""
            for name, alias in node.names:
                full_name = f"{base_module}.{name}" if base_module else name
                self.imports[module_name].append((full_name, alias))

    def _extract_calls(self, node: Any, module_name: str) -> None:
        """Extract function/method call relationships.

        Args:
            node: AST node to traverse
            module_name: Name of the module
        """
        if isinstance(node, nodes.Call):
            if hasattr(node.func, "name"):
                caller = self._get_current_function(node)
                callee = node.func.name
                if caller:
                    self.call_relationships.append((f"{module_name}.{caller}", callee))

        # Recursively traverse child nodes
        for child in node.get_children():
            self._extract_calls(child, module_name)

    def _get_current_function(self, node: Any) -> str | None:
        """Get the name of the function containing the given node.

        Args:
            node: AST node

        Returns:
            Function name or None
        """
        current = node
        while current:
            if isinstance(current, (nodes.FunctionDef, nodes.ClassDef)):
                return current.name
            current = current.parent if hasattr(current, "parent") else None
        return None

    def get_class_info(self, module_name: str, class_name: str) -> dict[str, Any]:
        """Get detailed information about a class.

        Args:
            module_name: Module containing the class
            class_name: Name of the class

        Returns:
            Dictionary with class information
        """
        if module_name not in self.classes:
            return {}

        for cls in self.classes[module_name]:
            if cls.name == class_name:
                methods = []
                attributes = []

                for node in cls.body:
                    if isinstance(node, nodes.FunctionDef):
                        methods.append(
                            {
                                "name": node.name,
                                "args": [arg.name for arg in node.args.args],
                                "returns": self._get_annotation_str(node.returns),
                            }
                        )
                    elif isinstance(node, nodes.Assign):
                        for target in node.targets:
                            if isinstance(target, nodes.AssignName):
                                attributes.append(target.name)

                return {
                    "name": cls.name,
                    "bases": [self._get_name(base) for base in cls.bases],
                    "methods": methods,
                    "attributes": attributes,
                    "docstring": cls.doc_node.value if cls.doc_node else "",
                }

        return {}

    def _get_annotation_str(self, annotation: Any) -> str:
        """Get string representation of type annotation.

        Args:
            annotation: Type annotation node

        Returns:
            String representation
        """
        if annotation is None:
            return ""
        if hasattr(annotation, "as_string"):
            return annotation.as_string()
        return str(annotation)

    def _get_name(self, node: Any) -> str:
        """Get name from a node.

        Args:
            node: AST node

        Returns:
            Name string
        """
        if isinstance(node, nodes.Name):
            return node.name
        if isinstance(node, nodes.Attribute):
            return node.as_string()
        return str(node)

    def get_dependencies(self) -> dict[str, set[str]]:
        """Get module dependency graph.

        Returns:
            Dictionary mapping module names to their dependencies
        """
        dependencies: dict[str, set[str]] = {}

        for module_name, imports in self.imports.items():
            deps = set()
            for import_name, _ in imports:
                # Extract base module name
                base_module = import_name.split(".")[0]
                deps.add(base_module)
            dependencies[module_name] = deps

        return dependencies

    def get_package_structure(self) -> dict[str, Any]:
        """Get hierarchical package structure.

        Returns:
            Nested dictionary representing package structure
        """
        structure: dict[str, Any] = {}

        for module_name in self.modules.keys():
            parts = module_name.split(".")
            current = structure

            for i, part in enumerate(parts):
                if part not in current:
                    current[part] = {
                        "_modules": [],
                        "_classes": [],
                        "_functions": [],
                    }

                if i == len(parts) - 1:
                    # Leaf node - add classes and functions
                    current[part]["_classes"] = [
                        cls.name for cls in self.classes.get(module_name, [])
                    ]
                    current[part]["_functions"] = [
                        func.name for func in self.functions.get(module_name, [])
                    ]
                else:
                    current = current[part]

        return structure
