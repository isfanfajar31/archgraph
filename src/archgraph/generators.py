"""Diagram generators for different architecture views."""

from abc import ABC, abstractmethod
from typing import Any

import networkx as nx

from archgraph.analyzer import CodeAnalyzer


class DiagramGenerator(ABC):
    """Abstract base class for diagram generators."""

    def __init__(self, analyzer: CodeAnalyzer):
        """Initialize the generator.

        Args:
            analyzer: CodeAnalyzer instance with parsed code
        """
        self.analyzer = analyzer

    @abstractmethod
    def generate(self, **options: Any) -> nx.DiGraph:
        """Generate the diagram as a NetworkX graph.

        Args:
            **options: Generator-specific options

        Returns:
            NetworkX directed graph representing the diagram
        """
        pass


class ClassDiagramGenerator(DiagramGenerator):
    """Generate UML-style class diagrams."""

    def generate(
        self,
        include_methods: bool = True,
        include_attributes: bool = True,
        include_private: bool = False,
        max_depth: int | None = None,
    ) -> nx.DiGraph:
        """Generate class diagram.

        Args:
            include_methods: Whether to include method details
            include_attributes: Whether to include attribute details
            include_private: Whether to include private members (starting with _)
            max_depth: Maximum inheritance depth to display

        Returns:
            NetworkX graph with class information
        """
        graph = nx.DiGraph()

        for module_name, classes in self.analyzer.classes.items():
            for cls in classes:
                class_info = self.analyzer.get_class_info(module_name, cls.name)
                if not class_info:
                    continue

                full_name = f"{module_name}.{cls.name}"

                # Filter methods and attributes based on options
                methods = class_info["methods"]
                attributes = class_info["attributes"]

                if not include_private:
                    methods = [m for m in methods if not m["name"].startswith("_")]
                    attributes = [a for a in attributes if not a.startswith("_")]

                # Build node label
                node_data = {
                    "type": "class",
                    "name": cls.name,
                    "module": module_name,
                    "methods": methods if include_methods else [],
                    "attributes": attributes if include_attributes else [],
                    "docstring": class_info.get("docstring", ""),
                }

                graph.add_node(full_name, **node_data)

                # Add inheritance relationships
                for base in class_info["bases"]:
                    # Try to resolve base class full name
                    base_full_name = self._resolve_class_name(base, module_name)
                    if base_full_name:
                        graph.add_edge(
                            full_name, base_full_name, relationship="inherits"
                        )

        return graph

    def _resolve_class_name(self, class_name: str, context_module: str) -> str | None:
        """Resolve a class name to its full module path.

        Args:
            class_name: Class name to resolve
            context_module: Module context for resolution

        Returns:
            Full class name or None if not found
        """
        # First check if it's already a full name
        if "." in class_name:
            return class_name

        # Check in the same module
        if context_module in self.analyzer.classes:
            for cls in self.analyzer.classes[context_module]:
                if cls.name == class_name:
                    return f"{context_module}.{class_name}"

        # Check imports
        if context_module in self.analyzer.imports:
            for import_name, alias in self.analyzer.imports[context_module]:
                if alias == class_name or import_name.endswith(f".{class_name}"):
                    return import_name

        return None


class DependencyGraphGenerator(DiagramGenerator):
    """Generate module/package dependency graphs."""

    def generate(
        self,
        group_by_package: bool = True,
        include_external: bool = True,
        max_depth: int | None = None,
    ) -> nx.DiGraph:
        """Generate dependency graph.

        Args:
            group_by_package: Group modules by their parent package
            include_external: Include external (non-project) dependencies
            max_depth: Maximum package depth to display

        Returns:
            NetworkX graph with dependency information
        """
        graph = nx.DiGraph()
        dependencies = self.analyzer.get_dependencies()

        for module_name, deps in dependencies.items():
            # Apply depth filtering
            if max_depth is not None:
                module_parts = module_name.split(".")
                if len(module_parts) > max_depth:
                    continue

            # Add module node
            module_display = (
                self._get_package_name(module_name) if group_by_package else module_name
            )

            if module_display not in graph:
                graph.add_node(
                    module_display,
                    type="module",
                    full_name=module_name,
                    is_package=group_by_package,
                )

            # Add dependency edges
            for dep in deps:
                # Check if dependency is internal or external
                is_internal = any(
                    m.startswith(dep) or dep in m for m in self.analyzer.modules.keys()
                )

                if not include_external and not is_internal:
                    continue

                dep_display = self._get_package_name(dep) if group_by_package else dep

                if dep_display not in graph:
                    graph.add_node(
                        dep_display,
                        type="module",
                        full_name=dep,
                        is_external=not is_internal,
                    )

                # Add edge if not self-reference
                if module_display != dep_display:
                    graph.add_edge(module_display, dep_display, relationship="imports")

        return graph

    def _get_package_name(self, module_name: str) -> str:
        """Get the package name from a module name.

        Args:
            module_name: Full module name

        Returns:
            Package name (first part of module path)
        """
        return module_name.split(".")[0]


class CallGraphGenerator(DiagramGenerator):
    """Generate function/method call graphs."""

    def generate(
        self,
        focus_module: str | None = None,
        include_external: bool = False,
        max_depth: int = 3,
    ) -> nx.DiGraph:
        """Generate call graph.

        Args:
            focus_module: Only show calls from/to this module
            include_external: Include calls to external functions
            max_depth: Maximum call depth to display

        Returns:
            NetworkX graph with call relationships
        """
        graph = nx.DiGraph()

        for caller, callee in self.analyzer.call_relationships:
            # Filter by focus module if specified
            if focus_module and not caller.startswith(focus_module):
                continue

            # Determine if callee is internal
            is_internal = any(
                callee in m or m.endswith(f".{callee}")
                for m in self.analyzer.modules.keys()
            )

            if not include_external and not is_internal:
                continue

            # Add nodes and edges
            if caller not in graph:
                graph.add_node(caller, type="function", is_internal=True)

            if callee not in graph:
                graph.add_node(callee, type="function", is_internal=is_internal)

            graph.add_edge(caller, callee, relationship="calls")

        return graph


class PackageStructureGenerator(DiagramGenerator):
    """Generate hierarchical package structure diagrams."""

    def generate(
        self, max_depth: int | None = None, show_empty: bool = False
    ) -> nx.DiGraph:
        """Generate package structure diagram.

        Args:
            max_depth: Maximum depth of package hierarchy to show
            show_empty: Show packages even if they have no modules

        Returns:
            NetworkX graph representing package hierarchy
        """
        graph = nx.DiGraph()
        structure = self.analyzer.get_package_structure()

        self._build_structure_graph(
            graph,
            structure,
            parent=None,
            depth=0,
            max_depth=max_depth,
            show_empty=show_empty,
        )

        return graph

    def _build_structure_graph(
        self,
        graph: nx.DiGraph,
        structure: dict[str, Any],
        parent: str | None,
        depth: int,
        max_depth: int | None,
        show_empty: bool,
    ) -> None:
        """Recursively build package structure graph.

        Args:
            graph: NetworkX graph to build
            structure: Nested structure dictionary
            parent: Parent node name
            depth: Current depth in hierarchy
            max_depth: Maximum depth to traverse
            show_empty: Whether to show empty packages
        """
        if max_depth is not None and depth > max_depth:
            return

        for name, content in structure.items():
            if name.startswith("_"):
                continue

            # Build full node name
            full_name = f"{parent}.{name}" if parent else name

            # Check if this node has content
            has_content = (
                content.get("_classes")
                or content.get("_functions")
                or any(k for k in content.keys() if not k.startswith("_"))
            )

            if not show_empty and not has_content:
                continue

            # Add node
            graph.add_node(
                full_name,
                type="package",
                name=name,
                classes=content.get("_classes", []),
                functions=content.get("_functions", []),
                depth=depth,
            )

            # Add edge from parent
            if parent:
                graph.add_edge(parent, full_name, relationship="contains")

            # Recursively add children
            self._build_structure_graph(
                graph,
                {k: v for k, v in content.items() if not k.startswith("_")},
                full_name,
                depth + 1,
                max_depth,
                show_empty,
            )
