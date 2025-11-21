"""MCP server for ArchGraph - expose architecture analysis tools via Model Context Protocol."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP

from archgraph.analyzer import CodeAnalyzer
from archgraph.exporters import (
    GraphVizExporter,
    MermaidExporter,
    PlantUMLExporter,
)
from archgraph.generators import (
    CallGraphGenerator,
    ClassDiagramGenerator,
    DependencyGraphGenerator,
    PackageStructureGenerator,
)
from archgraph.llm_analyzer import LLMAnalyzer

# Load environment variables
load_dotenv()

# Create MCP server
mcp = FastMCP("ArchGraph", dependencies=["archgraph"])


@mcp.tool()
def analyze_codebase(
    path: str,
    exclude_patterns: list[str] | None = None,
) -> dict[str, Any]:
    """Analyze a Python codebase and return structural information.

    Args:
        path: Path to the Python project directory
        exclude_patterns: Optional list of glob patterns to exclude (e.g., ["test_*", "*_test.py"])

    Returns:
        Dictionary with analysis results including module count, class count, etc.
    """
    project_path = Path(path).resolve()

    if not project_path.exists():
        return {"error": f"Path does not exist: {path}"}

    analyzer = CodeAnalyzer(project_path)
    analyzer.analyze(exclude_patterns=exclude_patterns or [])

    return {
        "total_modules": len(analyzer.modules),
        "total_classes": sum(len(classes) for classes in analyzer.classes.values()),
        "total_functions": sum(len(funcs) for funcs in analyzer.functions.values()),
        "total_imports": sum(len(imps) for imps in analyzer.imports.values()),
        "modules": list(analyzer.modules.keys()),
        "dependencies": {
            mod: list(deps) for mod, deps in analyzer.get_dependencies().items()
        },
    }


@mcp.tool()
def generate_class_diagram(
    path: str,
    output_path: str,
    format: str = "mermaid",  # Options: mermaid, plantuml, graphviz
    include_methods: bool = True,
    include_attributes: bool = True,
    include_private: bool = False,
    exclude_patterns: list[str] | None = None,
) -> dict[str, str]:
    """Generate a class diagram from Python code.

    Args:
        path: Path to the Python project directory
        output_path: Path where the diagram should be saved
        format: Output format ("mermaid", "plantuml", "graphviz")
        include_methods: Whether to include method details
        include_attributes: Whether to include attribute details
        include_private: Whether to include private members (starting with _)
        exclude_patterns: Optional list of glob patterns to exclude

    Returns:
        Dictionary with status and output path
    """
    try:
        project_path = Path(path).resolve()

        if not project_path.exists():
            return {"error": f"Path does not exist: {path}"}

        # Analyze code
        analyzer = CodeAnalyzer(project_path)
        analyzer.analyze(exclude_patterns=exclude_patterns or [])

        # Generate diagram
        generator = ClassDiagramGenerator(analyzer)
        graph = generator.generate(
            include_methods=include_methods,
            include_attributes=include_attributes,
            include_private=include_private,
        )

        # Export
        exporter = _get_exporter(format)
        output_file = Path(output_path)

        if format == "mermaid":
            exporter.export(graph, output_file, diagram_type="class")
        elif format == "plantuml":
            exporter.export(graph, output_file, diagram_type="class")
        else:
            exporter.export(graph, output_file)

        return {
            "status": "success",
            "output_path": str(output_file.resolve()),
            "format": format,
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def generate_dependency_graph(
    path: str,
    output_path: str,
    format: str = "mermaid",
    include_external: bool = True,
    group_by_package: bool = True,
    exclude_patterns: list[str] | None = None,
) -> dict[str, str]:
    """Generate a dependency graph showing module relationships.

    Args:
        path: Path to the Python project directory
        output_path: Path where the diagram should be saved
        format: Output format ("mermaid", "plantuml", "graphviz")
        include_external: Whether to include external dependencies
        group_by_package: Whether to group modules by parent package
        exclude_patterns: Optional list of glob patterns to exclude

    Returns:
        Dictionary with status and output path
    """
    try:
        project_path = Path(path).resolve()

        if not project_path.exists():
            return {"error": f"Path does not exist: {path}"}

        # Analyze code
        analyzer = CodeAnalyzer(project_path)
        analyzer.analyze(exclude_patterns=exclude_patterns or [])

        # Generate diagram
        generator = DependencyGraphGenerator(analyzer)
        graph = generator.generate(
            group_by_package=group_by_package,
            include_external=include_external,
        )

        # Export
        exporter = _get_exporter(format)
        output_file = Path(output_path)

        if format == "mermaid":
            exporter.export(graph, output_file, diagram_type="graph")
        else:
            exporter.export(graph, output_file)

        return {
            "status": "success",
            "output_path": str(output_file.resolve()),
            "format": format,
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def ai_analyze_architecture(
    path: str,
    reasoning_effort: str = "medium",
    exclude_patterns: list[str] | None = None,
) -> dict[str, Any]:
    """Use AI to analyze code architecture and provide insights.

    Args:
        path: Path to the Python project directory
        reasoning_effort: AI reasoning effort level ("low", "medium", "high")
        exclude_patterns: Optional list of glob patterns to exclude

    Returns:
        Dictionary with AI analysis including summary, patterns, issues, and recommendations
    """
    try:
        project_path = Path(path).resolve()

        if not project_path.exists():
            return {"error": f"Path does not exist: {path}"}

        # Analyze code
        analyzer = CodeAnalyzer(project_path)
        analyzer.analyze(exclude_patterns=exclude_patterns or [])

        # Run AI analysis
        llm_analyzer = LLMAnalyzer(analyzer)
        results = llm_analyzer.analyze_architecture(
            reasoning_effort=reasoning_effort,
        )

        return results

    except ValueError as e:
        return {
            "error": str(e),
            "hint": "Set AZURE_OPENAI_API_KEY and AZURE_ENDPOINT in .env file",
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def ai_suggest_diagrams(
    path: str,
    reasoning_effort: str = "medium",
    exclude_patterns: list[str] | None = None,
) -> dict[str, str]:
    """Get AI suggestions for which diagrams to generate.

    Args:
        path: Path to the Python project directory
        reasoning_effort: AI reasoning effort level ("low", "medium", "high")
        exclude_patterns: Optional list of glob patterns to exclude

    Returns:
        Dictionary with AI suggestions for diagram generation
    """
    try:
        project_path = Path(path).resolve()

        if not project_path.exists():
            return {"error": f"Path does not exist: {path}"}

        # Analyze code
        analyzer = CodeAnalyzer(project_path)
        analyzer.analyze(exclude_patterns=exclude_patterns or [])

        # Get AI suggestions
        llm_analyzer = LLMAnalyzer(analyzer)
        results = llm_analyzer.suggest_diagram_focus(
            reasoning_effort=reasoning_effort,
        )

        return results

    except ValueError as e:
        return {
            "error": str(e),
            "hint": "Set AZURE_OPENAI_API_KEY and AZURE_ENDPOINT in .env file",
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def ai_explain_dependencies(
    path: str,
    reasoning_effort: str = "medium",
    exclude_patterns: list[str] | None = None,
) -> str:
    """Get natural language explanation of code dependencies.

    Args:
        path: Path to the Python project directory
        reasoning_effort: AI reasoning effort level ("low", "medium", "high")
        exclude_patterns: Optional list of glob patterns to exclude

    Returns:
        Natural language explanation of the dependency structure
    """
    try:
        project_path = Path(path).resolve()

        if not project_path.exists():
            return f"Error: Path does not exist: {path}"

        # Analyze code
        analyzer = CodeAnalyzer(project_path)
        analyzer.analyze(exclude_patterns=exclude_patterns or [])

        # Get AI explanation
        llm_analyzer = LLMAnalyzer(analyzer)
        explanation = llm_analyzer.explain_dependency_graph(
            reasoning_effort=reasoning_effort,
        )

        return explanation

    except ValueError as e:
        return f"Error: {e}\nHint: Set AZURE_OPENAI_API_KEY and AZURE_ENDPOINT in .env file"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def generate_all_diagrams(
    path: str,
    output_dir: str,
    format: str = "mermaid",
    include_external: bool = False,
    exclude_patterns: list[str] | None = None,
) -> dict[str, Any]:
    """Generate all diagram types (class, dependency, call graph, package structure).

    Args:
        path: Path to the Python project directory
        output_dir: Directory where diagrams should be saved
        format: Output format ("mermaid", "plantuml", "graphviz")
        include_external: Whether to include external dependencies
        exclude_patterns: Optional list of glob patterns to exclude

    Returns:
        Dictionary with status and list of generated diagrams
    """
    try:
        project_path = Path(path).resolve()
        output_path = Path(output_dir)

        if not project_path.exists():
            return {"error": f"Path does not exist: {path}"}

        output_path.mkdir(parents=True, exist_ok=True)

        # Analyze code
        analyzer = CodeAnalyzer(project_path)
        analyzer.analyze(exclude_patterns=exclude_patterns or [])

        generated = []
        exporter = _get_exporter(format)
        ext = _get_extension(format)

        # Class diagram
        generator = ClassDiagramGenerator(analyzer)
        graph = generator.generate()
        output_file = output_path / f"class_diagram{ext}"
        if format == "mermaid":
            exporter.export(graph, output_file, diagram_type="class")
        else:
            exporter.export(graph, output_file)
        generated.append(str(output_file))

        # Dependency graph
        generator = DependencyGraphGenerator(analyzer)
        graph = generator.generate(include_external=include_external)
        output_file = output_path / f"dependency_graph{ext}"
        if format == "mermaid":
            exporter.export(graph, output_file, diagram_type="graph")
        else:
            exporter.export(graph, output_file)
        generated.append(str(output_file))

        # Call graph
        generator = CallGraphGenerator(analyzer)
        graph = generator.generate(include_external=include_external)
        output_file = output_path / f"call_graph{ext}"
        if format == "mermaid":
            exporter.export(graph, output_file, diagram_type="flowchart")
        else:
            exporter.export(graph, output_file)
        generated.append(str(output_file))

        # Package structure
        generator = PackageStructureGenerator(analyzer)
        graph = generator.generate()
        output_file = output_path / f"package_structure{ext}"
        if format == "mermaid":
            exporter.export(graph, output_file, diagram_type="graph")
        else:
            exporter.export(graph, output_file)
        generated.append(str(output_file))

        return {
            "status": "success",
            "generated_diagrams": generated,
            "output_directory": str(output_path.resolve()),
            "format": format,
        }

    except Exception as e:
        return {"error": str(e)}


def _get_exporter(format: str) -> Any:
    """Get exporter instance for format.

    Args:
        format: Format name

    Returns:
        Exporter instance
    """
    if format == "mermaid":
        return MermaidExporter()
    elif format == "plantuml":
        return PlantUMLExporter()
    elif format == "graphviz":
        return GraphVizExporter()
    else:
        return MermaidExporter()


def _get_extension(format: str) -> str:
    """Get file extension for format.

    Args:
        format: Format name

    Returns:
        File extension with dot
    """
    extensions = {
        "mermaid": ".mmd",
        "plantuml": ".puml",
        "graphviz": ".png",
    }
    return extensions.get(format, ".mmd")


# Run server
if __name__ == "__main__":
    mcp.run()
