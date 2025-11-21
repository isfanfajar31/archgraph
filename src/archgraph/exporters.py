"""Exporters for converting NetworkX graphs to various diagram formats."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import networkx as nx
from graphviz import Digraph

# Try to import Structurizr (optional dependency)
try:
    from structurizr import Workspace
    from structurizr.model import Tags
    from structurizr.view import ElementStyle, Shape

    STRUCTURIZR_AVAILABLE = True
except ImportError:
    STRUCTURIZR_AVAILABLE = False
    Workspace = None
    Tags = None


class DiagramExporter(ABC):
    """Abstract base class for diagram exporters."""

    @abstractmethod
    def export(
        self, graph: nx.DiGraph, output_path: str | Path, **options: Any
    ) -> None:
        """Export the graph to a file.

        Args:
            graph: NetworkX graph to export
            output_path: Path where the diagram should be saved
            **options: Exporter-specific options
        """
        pass

    @abstractmethod
    def to_string(self, graph: nx.DiGraph, **options: Any) -> str:
        """Convert graph to string representation.

        Args:
            graph: NetworkX graph to convert
            **options: Exporter-specific options

        Returns:
            String representation of the diagram
        """
        pass


class MermaidExporter(DiagramExporter):
    """Export diagrams to Mermaid format."""

    def export(
        self, graph: nx.DiGraph, output_path: str | Path, **options: Any
    ) -> None:
        """Export graph to Mermaid file.

        Args:
            graph: NetworkX graph to export
            output_path: Path to save the Mermaid diagram
            **options: Additional options (diagram_type, etc.)
        """
        output_path = Path(output_path)
        content = self.to_string(graph, **options)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def to_string(self, graph: nx.DiGraph, **options: Any) -> str:
        """Convert graph to Mermaid string.

        Args:
            graph: NetworkX graph to convert
            **options: Options like diagram_type ('class', 'graph', 'flowchart')

        Returns:
            Mermaid diagram as string
        """
        diagram_type = options.get("diagram_type", "graph")

        if diagram_type == "class":
            return self._to_class_diagram(graph)
        elif diagram_type == "flowchart":
            return self._to_flowchart(graph)
        else:
            return self._to_graph(graph)

    def _to_class_diagram(self, graph: nx.DiGraph) -> str:
        """Convert to Mermaid class diagram.

        Args:
            graph: NetworkX graph with class information

        Returns:
            Mermaid class diagram string
        """
        lines = ["classDiagram"]

        for node in graph.nodes():
            node_data = graph.nodes[node]
            if node_data.get("type") == "class":
                class_name = self._sanitize_id(node)
                lines.append(f"    class {class_name} {{")

                # Add attributes
                for attr in node_data.get("attributes", []):
                    lines.append(f"        +{attr}")

                # Add methods
                for method in node_data.get("methods", []):
                    method_name = method["name"]
                    args = ", ".join(method.get("args", []))
                    returns = method.get("returns", "")
                    return_str = f" {returns}" if returns else ""
                    lines.append(f"        +{method_name}({args}){return_str}")

                lines.append("    }")

        # Add relationships
        for source, target, data in graph.edges(data=True):
            relationship = data.get("relationship", "")
            source_id = self._sanitize_id(source)
            target_id = self._sanitize_id(target)

            if relationship == "inherits":
                lines.append(f"    {source_id} --|> {target_id}")
            elif relationship == "uses":
                lines.append(f"    {source_id} ..> {target_id}")
            else:
                lines.append(f"    {source_id} --> {target_id}")

        return "\n".join(lines)

    def _to_flowchart(self, graph: nx.DiGraph) -> str:
        """Convert to Mermaid flowchart.

        Args:
            graph: NetworkX graph

        Returns:
            Mermaid flowchart string
        """
        lines = ["flowchart TD"]

        # Add nodes
        for node in graph.nodes():
            node_data = graph.nodes[node]
            node_id = self._sanitize_id(node)
            label = node_data.get("name", node)
            lines.append(f'    {node_id}["{label}"]')

        # Add edges
        for source, target, data in graph.edges(data=True):
            source_id = self._sanitize_id(source)
            target_id = self._sanitize_id(target)
            relationship = data.get("relationship", "")
            label = f"|{relationship}|" if relationship else ""
            lines.append(f"    {source_id} -->{label} {target_id}")

        return "\n".join(lines)

    def _to_graph(self, graph: nx.DiGraph) -> str:
        """Convert to Mermaid graph.

        Args:
            graph: NetworkX graph

        Returns:
            Mermaid graph string
        """
        lines = ["graph TD"]

        # Add nodes with labels
        for node in graph.nodes():
            node_data = graph.nodes[node]
            node_id = self._sanitize_id(node)
            label = node_data.get("name", node)
            node_type = node_data.get("type", "")

            # Use different shapes based on type
            if node_type == "package":
                lines.append(f'    {node_id}["{label}"]')
            elif node_type == "module":
                lines.append(f'    {node_id}("{label}")')
            elif node_data.get("is_external", False):
                lines.append(f"    {node_id}{{{label}}}")
            else:
                lines.append(f'    {node_id}["{label}"]')

        # Add edges
        for source, target, data in graph.edges(data=True):
            source_id = self._sanitize_id(source)
            target_id = self._sanitize_id(target)
            relationship = data.get("relationship", "")
            label = f"|{relationship}|" if relationship else ""
            lines.append(f"    {source_id} -->{label} {target_id}")

        return "\n".join(lines)

    def _sanitize_id(self, node_name: str) -> str:
        """Sanitize node name for use as Mermaid ID.

        Args:
            node_name: Original node name

        Returns:
            Sanitized ID
        """
        return node_name.replace(".", "_").replace("-", "_").replace(" ", "_")


class PlantUMLExporter(DiagramExporter):
    """Export diagrams to PlantUML format."""

    def export(
        self, graph: nx.DiGraph, output_path: str | Path, **options: Any
    ) -> None:
        """Export graph to PlantUML file.

        Args:
            graph: NetworkX graph to export
            output_path: Path to save the PlantUML diagram
            **options: Additional options
        """
        output_path = Path(output_path)
        content = self.to_string(graph, **options)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def to_string(self, graph: nx.DiGraph, **options: Any) -> str:
        """Convert graph to PlantUML string.

        Args:
            graph: NetworkX graph to convert
            **options: Options like diagram_type

        Returns:
            PlantUML diagram as string
        """
        diagram_type = options.get("diagram_type", "component")

        if diagram_type == "class":
            return self._to_class_diagram(graph)
        else:
            return self._to_component_diagram(graph)

    def _to_class_diagram(self, graph: nx.DiGraph) -> str:
        """Convert to PlantUML class diagram.

        Args:
            graph: NetworkX graph with class information

        Returns:
            PlantUML class diagram string
        """
        lines = ["@startuml", ""]

        for node in graph.nodes():
            node_data = graph.nodes[node]
            if node_data.get("type") == "class":
                class_name = node_data.get("name", node)
                lines.append(f"class {class_name} {{")

                # Add attributes
                for attr in node_data.get("attributes", []):
                    lines.append(f"  +{attr}")

                if node_data.get("attributes") and node_data.get("methods"):
                    lines.append("  --")

                # Add methods
                for method in node_data.get("methods", []):
                    method_name = method["name"]
                    args = ", ".join(method.get("args", []))
                    returns = method.get("returns", "")
                    return_str = f": {returns}" if returns else ""
                    lines.append(f"  +{method_name}({args}){return_str}")

                lines.append("}")
                lines.append("")

        # Add relationships
        for source, target, data in graph.edges(data=True):
            relationship = data.get("relationship", "")
            source_name = graph.nodes[source].get("name", source)
            target_name = graph.nodes[target].get("name", target)

            if relationship == "inherits":
                lines.append(f"{source_name} --|> {target_name}")
            elif relationship == "uses":
                lines.append(f"{source_name} ..> {target_name}")
            else:
                lines.append(f"{source_name} --> {target_name}")

        lines.append("")
        lines.append("@enduml")
        return "\n".join(lines)

    def _to_component_diagram(self, graph: nx.DiGraph) -> str:
        """Convert to PlantUML component diagram.

        Args:
            graph: NetworkX graph

        Returns:
            PlantUML component diagram string
        """
        lines = ["@startuml", ""]

        # Add components
        for node in graph.nodes():
            node_data = graph.nodes[node]
            node_type = node_data.get("type", "component")
            name = node_data.get("name", node)

            if node_type == "package":
                lines.append(f'package "{name}" {{')
                lines.append("}")
            elif node_type == "module":
                lines.append(f'component "{name}"')
            else:
                lines.append(f"[{name}]")

        lines.append("")

        # Add relationships
        for source, target, data in graph.edges(data=True):
            relationship = data.get("relationship", "")
            label = f" : {relationship}" if relationship else ""
            lines.append(f"{source} --> {target}{label}")

        lines.append("")
        lines.append("@enduml")
        return "\n".join(lines)


class GraphVizExporter(DiagramExporter):
    """Export diagrams using GraphViz."""

    def export(
        self, graph: nx.DiGraph, output_path: str | Path, **options: Any
    ) -> None:
        """Export graph to image file using GraphViz.

        Args:
            graph: NetworkX graph to export
            output_path: Path to save the diagram (extension determines format)
            **options: Additional options (layout, format, etc.)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create GraphViz diagram
        dot = self._create_graphviz(graph, **options)

        # Determine format from extension
        format_name = output_path.suffix.lstrip(".")
        if not format_name:
            format_name = options.get("format", "png")

        # Render to file
        output_base = str(output_path.with_suffix(""))
        dot.render(output_base, format=format_name, cleanup=True)

    def to_string(self, graph: nx.DiGraph, **options: Any) -> str:
        """Convert graph to GraphViz DOT string.

        Args:
            graph: NetworkX graph to convert
            **options: Options like layout, rankdir

        Returns:
            GraphViz DOT source string
        """
        dot = self._create_graphviz(graph, **options)
        return dot.source

    def _create_graphviz(self, graph: nx.DiGraph, **options: Any) -> Digraph:
        """Create a GraphViz Digraph from NetworkX graph.

        Args:
            graph: NetworkX graph
            **options: Options like layout, rankdir, node_shape

        Returns:
            GraphViz Digraph object
        """
        layout = options.get("layout", "dot")
        rankdir = options.get("rankdir", "TB")

        dot = Digraph(engine=layout)
        dot.attr(rankdir=rankdir)
        dot.attr("node", shape="box", style="rounded,filled", fillcolor="lightblue")

        # Add nodes
        for node in graph.nodes():
            node_data = graph.nodes[node]
            label = self._create_node_label(node, node_data, options)
            node_type = node_data.get("type", "")

            # Customize appearance based on type
            attrs = {}
            if node_type == "class":
                attrs = {"shape": "record", "fillcolor": "lightgreen"}
            elif node_type == "package":
                attrs = {"shape": "folder", "fillcolor": "lightyellow"}
            elif node_type == "module":
                attrs = {"shape": "component", "fillcolor": "lightblue"}
            elif node_data.get("is_external", False):
                attrs = {"fillcolor": "lightgray", "style": "dashed,filled"}

            dot.node(node, label=label, **attrs)

        # Add edges
        for source, target, data in graph.edges(data=True):
            relationship = data.get("relationship", "")
            label = relationship if relationship else ""

            # Customize edge style based on relationship
            attrs = {"label": label}
            if relationship == "inherits":
                attrs["arrowhead"] = "empty"
            elif relationship == "imports":
                attrs["style"] = "dashed"

            dot.edge(source, target, **attrs)

        return dot

    def _create_node_label(
        self, node: str, node_data: dict[str, Any], options: dict[str, Any]
    ) -> str:
        """Create label for a node.

        Args:
            node: Node identifier
            node_data: Node data dictionary
            options: Display options

        Returns:
            Formatted label string
        """
        node_type = node_data.get("type", "")
        name = node_data.get("name", node)

        if node_type == "class" and options.get("show_details", True):
            # Create record-style label for classes
            parts = [f"{name}"]

            attributes = node_data.get("attributes", [])
            if attributes:
                parts.append(
                    "|" + "\\l".join(f"+ {attr}" for attr in attributes) + "\\l"
                )

            methods = node_data.get("methods", [])
            if methods:
                method_strs = []
                for method in methods:
                    method_name = method["name"]
                    args = ", ".join(method.get("args", []))
                    method_strs.append(f"+ {method_name}({args})")
                parts.append("|" + "\\l".join(method_strs) + "\\l")

            return "{" + "".join(parts) + "}"

        return name


class StructurizrExporter(DiagramExporter):
    """Export diagrams to Structurizr C4 model format.

    Note: Requires structurizr-python package to be installed.
    Currently disabled due to Pydantic v2 compatibility issues.
    """

    def export(
        self, graph: nx.DiGraph, output_path: str | Path, **options: Any
    ) -> None:
        """Export graph to Structurizr workspace file.

        Args:
            graph: NetworkX graph to export
            output_path: Path to save the Structurizr workspace JSON
            **options: Additional options (workspace_name, description, etc.)

        Raises:
            ImportError: If structurizr-python is not installed
        """
        if not STRUCTURIZR_AVAILABLE:
            raise ImportError(
                "Structurizr export requires structurizr-python package. "
                "Currently disabled due to Pydantic v2 compatibility issues. "
                "Please use mermaid, plantuml, or graphviz formats instead."
            )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create workspace
        workspace_name = options.get("workspace_name", "Software Architecture")
        description = options.get("description", "Generated by ArchGraph")
        workspace = Workspace(name=workspace_name, description=description)

        # Build C4 model from graph
        self._build_c4_model(workspace, graph, **options)

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(workspace.to_json())

    def to_string(self, graph: nx.DiGraph, **options: Any) -> str:
        """Convert graph to Structurizr JSON string.

        Args:
            graph: NetworkX graph to convert
            **options: Options like workspace_name, description

        Returns:
            Structurizr workspace JSON string

        Raises:
            ImportError: If structurizr-python is not installed
        """
        if not STRUCTURIZR_AVAILABLE:
            raise ImportError(
                "Structurizr export requires structurizr-python package. "
                "Currently disabled due to Pydantic v2 compatibility issues."
            )

        workspace_name = options.get("workspace_name", "Software Architecture")
        description = options.get("description", "Generated by ArchGraph")
        workspace = Workspace(name=workspace_name, description=description)

        self._build_c4_model(workspace, graph, **options)
        return workspace.to_json()

    def _build_c4_model(
        self, workspace: Workspace, graph: nx.DiGraph, **options: Any
    ) -> None:
        """Build C4 model from NetworkX graph.

        Args:
            workspace: Structurizr workspace
            graph: NetworkX graph
            **options: Additional options
        """
        model = workspace.model
        views = workspace.views

        # Map node types to C4 elements
        node_to_element = {}

        # Create software systems and containers
        for node in graph.nodes():
            node_data = graph.nodes[node]
            node_type = node_data.get("type", "component")
            name = node_data.get("name", node)
            description = node_data.get("docstring", "")

            if node_type == "package":
                # Packages become software systems
                system = model.add_software_system(name=name, description=description)
                node_to_element[node] = system

            elif node_type == "module":
                # Modules become containers
                # Try to find parent system
                parent_system = None
                for pred in graph.predecessors(node):
                    if graph.nodes[pred].get("type") == "package":
                        parent_system = node_to_element.get(pred)
                        break

                if not parent_system:
                    # Create a default system
                    parent_system = model.add_software_system(
                        name="Application", description="Main application"
                    )

                container = parent_system.add_container(
                    name=name, description=description, technology="Python"
                )
                node_to_element[node] = container

            elif node_type == "class":
                # Classes become components
                # Find parent container
                parent_container = None
                module_name = node_data.get("module", "")
                if module_name and module_name in node_to_element:
                    parent_elem = node_to_element[module_name]
                    if hasattr(parent_elem, "add_component"):
                        parent_container = parent_elem

                if not parent_container:
                    # Create default container
                    default_system = model.add_software_system(
                        name="Application", description="Main application"
                    )
                    parent_container = default_system.add_container(
                        name="Core", description="Core components", technology="Python"
                    )

                component = parent_container.add_component(
                    name=name,
                    description=description,
                    technology="Python Class",
                )
                node_to_element[node] = component

        # Add relationships
        for source, target, data in graph.edges(data=True):
            relationship_type = data.get("relationship", "uses")

            source_elem = node_to_element.get(source)
            target_elem = node_to_element.get(target)

            if source_elem and target_elem:
                source_elem.uses(target_elem, description=relationship_type)

        # Create views
        diagram_type = options.get("diagram_type", "system_context")

        if diagram_type == "system_context":
            # System Context view
            systems = [
                elem
                for elem in node_to_element.values()
                if hasattr(elem, "add_container")
            ]
            if systems:
                system = systems[0]
                view = views.create_system_context_view(
                    software_system=system,
                    key="SystemContext",
                    description="System Context diagram",
                )
                view.add_all_software_systems()
                view.add_all_people()

        elif diagram_type == "container":
            # Container view
            systems = [
                elem
                for elem in node_to_element.values()
                if hasattr(elem, "add_container")
            ]
            if systems:
                system = systems[0]
                view = views.create_container_view(
                    software_system=system,
                    key="Containers",
                    description="Container diagram",
                )
                view.add_all_containers()
                view.add_all_people()

        elif diagram_type == "component":
            # Component view
            containers = [
                elem
                for elem in node_to_element.values()
                if hasattr(elem, "add_component")
            ]
            if containers:
                container = containers[0]
                view = views.create_component_view(
                    container=container,
                    key="Components",
                    description="Component diagram",
                )
                view.add_all_components()

        # Apply styles
        styles = views.configuration.styles
        styles.add_element_style(tag=Tags.SOFTWARE_SYSTEM).background = "#1168bd"
        styles.add_element_style(tag=Tags.SOFTWARE_SYSTEM).color = "#ffffff"
        styles.add_element_style(tag=Tags.CONTAINER).background = "#438dd5"
        styles.add_element_style(tag=Tags.CONTAINER).color = "#ffffff"
        styles.add_element_style(tag=Tags.COMPONENT).background = "#85bbf0"
        styles.add_element_style(tag=Tags.COMPONENT).color = "#000000"
