"""Exporters for converting NetworkX graphs to various diagram formats."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import networkx as nx
from graphviz import Digraph


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
