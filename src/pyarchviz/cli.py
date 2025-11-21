"""Command-line interface for PyArchViz."""

import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from pyarchviz.analyzer import CodeAnalyzer
from pyarchviz.exporters import GraphVizExporter, MermaidExporter, PlantUMLExporter
from pyarchviz.generators import (
    CallGraphGenerator,
    ClassDiagramGenerator,
    DependencyGraphGenerator,
    PackageStructureGenerator,
)

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="pyarchviz")
def main() -> None:
    """PyArchViz - Python Architecture Visualizer.

    Generate software architecture diagrams from Python code.
    """
    pass


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default="diagrams",
    help="Output directory for diagrams",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["mermaid", "plantuml", "graphviz", "all"], case_sensitive=False),
    default="mermaid",
    help="Output format for diagrams",
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    help="Patterns to exclude (e.g., test_*, *_test.py)",
)
@click.option(
    "--all-diagrams",
    "-a",
    is_flag=True,
    help="Generate all diagram types",
)
@click.option(
    "--class-diagram",
    is_flag=True,
    help="Generate class diagram",
)
@click.option(
    "--dependency-graph",
    is_flag=True,
    help="Generate dependency graph",
)
@click.option(
    "--call-graph",
    is_flag=True,
    help="Generate call graph",
)
@click.option(
    "--package-structure",
    is_flag=True,
    help="Generate package structure diagram",
)
@click.option(
    "--include-private",
    is_flag=True,
    help="Include private members (starting with _) in class diagrams",
)
@click.option(
    "--no-methods",
    is_flag=True,
    help="Exclude methods from class diagrams",
)
@click.option(
    "--no-attributes",
    is_flag=True,
    help="Exclude attributes from class diagrams",
)
@click.option(
    "--max-depth",
    type=int,
    help="Maximum depth for hierarchical diagrams",
)
@click.option(
    "--include-external",
    is_flag=True,
    help="Include external dependencies",
)
@click.option(
    "--graphviz-layout",
    type=click.Choice(["dot", "neato", "fdp", "sfdp", "circo", "twopi"]),
    default="dot",
    help="GraphViz layout engine",
)
@click.option(
    "--graphviz-format",
    type=click.Choice(["png", "svg", "pdf", "jpg"]),
    default="png",
    help="GraphViz output format",
)
def generate(
    path: Path,
    output: Path,
    format: str,
    exclude: tuple[str, ...],
    all_diagrams: bool,
    class_diagram: bool,
    dependency_graph: bool,
    call_graph: bool,
    package_structure: bool,
    include_private: bool,
    no_methods: bool,
    no_attributes: bool,
    max_depth: int | None,
    include_external: bool,
    graphviz_layout: str,
    graphviz_format: str,
) -> None:
    """Generate architecture diagrams from Python code.

    PATH: Directory containing Python code to analyze
    """
    # If no specific diagram type is selected, generate all
    if not any([class_diagram, dependency_graph, call_graph, package_structure]):
        all_diagrams = True

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Analyze code
            task = progress.add_task("[cyan]Analyzing Python code...", total=None)
            analyzer = CodeAnalyzer(path)
            analyzer.analyze(exclude_patterns=list(exclude))
            progress.update(task, completed=True)

            # Create output directory
            output.mkdir(parents=True, exist_ok=True)

            # Determine which exporters to use
            exporters = _get_exporters(format, graphviz_layout, graphviz_format)

            # Generate diagrams
            diagram_count = 0

            if all_diagrams or class_diagram:
                task = progress.add_task(
                    "[cyan]Generating class diagram...", total=None
                )
                _generate_class_diagram(
                    analyzer,
                    exporters,
                    output,
                    include_methods=not no_methods,
                    include_attributes=not no_attributes,
                    include_private=include_private,
                    max_depth=max_depth,
                )
                progress.update(task, completed=True)
                diagram_count += 1

            if all_diagrams or dependency_graph:
                task = progress.add_task(
                    "[cyan]Generating dependency graph...", total=None
                )
                _generate_dependency_graph(
                    analyzer,
                    exporters,
                    output,
                    include_external=include_external,
                    max_depth=max_depth,
                )
                progress.update(task, completed=True)
                diagram_count += 1

            if all_diagrams or call_graph:
                task = progress.add_task("[cyan]Generating call graph...", total=None)
                _generate_call_graph(
                    analyzer,
                    exporters,
                    output,
                    include_external=include_external,
                    max_depth=max_depth or 3,
                )
                progress.update(task, completed=True)
                diagram_count += 1

            if all_diagrams or package_structure:
                task = progress.add_task(
                    "[cyan]Generating package structure...", total=None
                )
                _generate_package_structure(
                    analyzer, exporters, output, max_depth=max_depth
                )
                progress.update(task, completed=True)
                diagram_count += 1

        # Print summary
        console.print(f"\n[green]✓[/green] Generated {diagram_count} diagram(s)")
        console.print(f"[blue]→[/blue] Output directory: {output.resolve()}")

    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    help="Patterns to exclude",
)
def analyze(path: Path, exclude: tuple[str, ...]) -> None:
    """Analyze Python code and display statistics.

    PATH: Directory containing Python code to analyze
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Analyzing Python code...", total=None)
            analyzer = CodeAnalyzer(path)
            analyzer.analyze(exclude_patterns=list(exclude))
            progress.update(task, completed=True)

        # Display statistics
        console.print("\n[bold cyan]Analysis Results[/bold cyan]\n")

        # Module statistics
        table = Table(title="Modules", show_header=True, header_style="bold magenta")
        table.add_column("Module", style="cyan")
        table.add_column("Classes", justify="right")
        table.add_column("Functions", justify="right")
        table.add_column("Imports", justify="right")

        for module_name in sorted(analyzer.modules.keys()):
            class_count = len(analyzer.classes.get(module_name, []))
            func_count = len(analyzer.functions.get(module_name, []))
            import_count = len(analyzer.imports.get(module_name, []))

            table.add_row(
                module_name,
                str(class_count),
                str(func_count),
                str(import_count),
            )

        console.print(table)

        # Summary statistics
        total_modules = len(analyzer.modules)
        total_classes = sum(len(classes) for classes in analyzer.classes.values())
        total_functions = sum(len(funcs) for funcs in analyzer.functions.values())
        total_imports = sum(len(imps) for imps in analyzer.imports.values())

        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Total Modules: {total_modules}")
        console.print(f"  Total Classes: {total_classes}")
        console.print(f"  Total Functions: {total_functions}")
        console.print(f"  Total Imports: {total_imports}")

        # Dependency information
        dependencies = analyzer.get_dependencies()
        external_deps = set()
        for deps in dependencies.values():
            for dep in deps:
                if not any(dep in m or m.startswith(dep) for m in analyzer.modules):
                    external_deps.add(dep)

        if external_deps:
            console.print(f"\n[bold]External Dependencies:[/bold]")
            for dep in sorted(external_deps):
                console.print(f"  • {dep}")

    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


@main.command()
def formats() -> None:
    """Display information about supported output formats."""
    console.print("\n[bold cyan]Supported Output Formats[/bold cyan]\n")

    # Mermaid
    console.print("[bold]Mermaid[/bold] (.mmd, .md)")
    console.print("  • Markdown-compatible diagram format")
    console.print("  • Can be rendered in GitHub, GitLab, and many editors")
    console.print("  • Supports class diagrams, flowcharts, and graphs")
    console.print("  • Recommended for documentation\n")

    # PlantUML
    console.print("[bold]PlantUML[/bold] (.puml, .plantuml)")
    console.print("  • Popular UML diagram format")
    console.print("  • Requires PlantUML or online renderer to view")
    console.print("  • Supports class and component diagrams")
    console.print("  • Good for detailed UML documentation\n")

    # GraphViz
    console.print("[bold]GraphViz[/bold] (.png, .svg, .pdf, .jpg)")
    console.print("  • Direct image output using GraphViz")
    console.print("  • Multiple layout engines available")
    console.print("  • Best for presentations and reports")
    console.print("  • Requires GraphViz to be installed\n")

    console.print("[dim]Use --format option to select output format[/dim]")


def _get_exporters(
    format_name: str, graphviz_layout: str, graphviz_format: str
) -> list[tuple[Any, str, dict[str, Any]]]:
    """Get list of exporters based on format selection.

    Args:
        format_name: Format name or 'all'
        graphviz_layout: GraphViz layout engine
        graphviz_format: GraphViz output format

    Returns:
        List of tuples (exporter, extension, options)
    """
    exporters = []

    if format_name in ["mermaid", "all"]:
        exporters.append((MermaidExporter(), ".mmd", {}))

    if format_name in ["plantuml", "all"]:
        exporters.append((PlantUMLExporter(), ".puml", {}))

    if format_name in ["graphviz", "all"]:
        exporters.append(
            (
                GraphVizExporter(),
                f".{graphviz_format}",
                {"layout": graphviz_layout, "format": graphviz_format},
            )
        )

    return exporters


def _generate_class_diagram(
    analyzer: CodeAnalyzer,
    exporters: list[tuple[Any, str, dict[str, Any]]],
    output_dir: Path,
    **options: Any,
) -> None:
    """Generate class diagram with all exporters."""
    generator = ClassDiagramGenerator(analyzer)
    graph = generator.generate(**options)

    for exporter, ext, exporter_options in exporters:
        output_path = output_dir / f"class_diagram{ext}"
        if isinstance(exporter, MermaidExporter):
            exporter_options["diagram_type"] = "class"
        elif isinstance(exporter, PlantUMLExporter):
            exporter_options["diagram_type"] = "class"
        exporter.export(graph, output_path, **exporter_options)


def _generate_dependency_graph(
    analyzer: CodeAnalyzer,
    exporters: list[tuple[Any, str, dict[str, Any]]],
    output_dir: Path,
    **options: Any,
) -> None:
    """Generate dependency graph with all exporters."""
    generator = DependencyGraphGenerator(analyzer)
    graph = generator.generate(**options)

    for exporter, ext, exporter_options in exporters:
        output_path = output_dir / f"dependency_graph{ext}"
        if isinstance(exporter, MermaidExporter):
            exporter_options["diagram_type"] = "graph"
        exporter.export(graph, output_path, **exporter_options)


def _generate_call_graph(
    analyzer: CodeAnalyzer,
    exporters: list[tuple[Any, str, dict[str, Any]]],
    output_dir: Path,
    **options: Any,
) -> None:
    """Generate call graph with all exporters."""
    generator = CallGraphGenerator(analyzer)
    graph = generator.generate(**options)

    for exporter, ext, exporter_options in exporters:
        output_path = output_dir / f"call_graph{ext}"
        if isinstance(exporter, MermaidExporter):
            exporter_options["diagram_type"] = "flowchart"
        exporter.export(graph, output_path, **exporter_options)


def _generate_package_structure(
    analyzer: CodeAnalyzer,
    exporters: list[tuple[Any, str, dict[str, Any]]],
    output_dir: Path,
    **options: Any,
) -> None:
    """Generate package structure with all exporters."""
    generator = PackageStructureGenerator(analyzer)
    graph = generator.generate(**options)

    for exporter, ext, exporter_options in exporters:
        output_path = output_dir / f"package_structure{ext}"
        if isinstance(exporter, MermaidExporter):
            exporter_options["diagram_type"] = "graph"
        exporter.export(graph, output_path, **exporter_options)


if __name__ == "__main__":
    main()
