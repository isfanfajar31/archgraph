"""Command-line interface for ArchGraph."""

import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from archgraph.analyzer import CodeAnalyzer
from archgraph.exporters import (
    GraphVizExporter,
    MermaidExporter,
    PlantUMLExporter,
    StructurizrExporter,
)
from archgraph.generators import (
    CallGraphGenerator,
    ClassDiagramGenerator,
    DependencyGraphGenerator,
    PackageStructureGenerator,
)
from archgraph.llm_analyzer import LLMAnalyzer

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="archgraph")
def main() -> None:
    """ArchGraph - Architecture Diagram Generator with AI.

    Generate software architecture diagrams from Python code with AI-powered insights.
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

    # Structurizr disabled due to Pydantic v2 compatibility issues
    # if format_name in ["structurizr", "all"]:
    #     exporters.append((StructurizrExporter(), ".json", {}))

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
        # elif isinstance(exporter, StructurizrExporter):
        #     exporter_options["diagram_type"] = "component"
        #     exporter_options["workspace_name"] = "Class Diagram"
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
        # elif isinstance(exporter, StructurizrExporter):
        #     exporter_options["diagram_type"] = "system_context"
        #     exporter_options["workspace_name"] = "Dependency Graph"
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


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    help="Patterns to exclude",
)
@click.option(
    "--save",
    "-s",
    type=click.Path(path_type=Path),
    help="Save analysis to file",
)
@click.option(
    "--reasoning-effort",
    "-r",
    type=click.Choice(["low", "medium", "high"], case_sensitive=False),
    default="medium",
    help="AI reasoning effort level (default: medium)",
)
def llm_analyze(
    path: Path, exclude: tuple[str, ...], save: Path | None, reasoning_effort: str
) -> None:
    """Analyze code architecture using AI (requires Azure OpenAI credentials).

    PATH: Directory containing Python code to analyze
    """
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

            # Run LLM analysis
            task = progress.add_task("[cyan]Running AI-powered analysis...", total=None)
            llm_analyzer = LLMAnalyzer(analyzer)
            results = llm_analyzer.analyze_architecture(
                reasoning_effort=reasoning_effort.lower()
            )
            progress.update(task, completed=True)

        # Display results
        if "error" in results:
            console.print(f"[red]✗[/red] {results['error']}", style="bold red")
            sys.exit(1)

        console.print("\n[bold cyan]AI Architecture Analysis[/bold cyan]\n")

        # Summary
        if results.get("summary"):
            console.print("[bold]Summary:[/bold]")
            console.print(results["summary"])
            console.print()

        # Patterns
        if results.get("patterns"):
            console.print("[bold]Design Patterns Detected:[/bold]")
            for pattern in results["patterns"]:
                console.print(f"  • {pattern}")
            console.print()

        # Issues
        if results.get("issues"):
            console.print("[bold yellow]Potential Issues:[/bold yellow]")
            for issue in results["issues"]:
                console.print(f"  ⚠ {issue}")
            console.print()

        # Recommendations
        if results.get("recommendations"):
            console.print("[bold green]Recommendations:[/bold green]")
            for rec in results["recommendations"]:
                console.print(f"  ✓ {rec}")
            console.print()

        # Save to file if requested
        if save:
            save.parent.mkdir(parents=True, exist_ok=True)
            with open(save, "w", encoding="utf-8") as f:
                f.write("# AI Architecture Analysis\n\n")
                f.write(f"## Summary\n{results.get('summary', 'N/A')}\n\n")
                f.write("## Design Patterns\n")
                for p in results.get("patterns", []):
                    f.write(f"- {p}\n")
                f.write("\n## Issues\n")
                for i in results.get("issues", []):
                    f.write(f"- {i}\n")
                f.write("\n## Recommendations\n")
                for r in results.get("recommendations", []):
                    f.write(f"- {r}\n")
            console.print(f"[blue]→[/blue] Analysis saved to: {save.resolve()}")

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}", style="bold red")
        console.print(
            "\n[yellow]Required:[/yellow] Set Azure OpenAI credentials in .env file:"
        )
        console.print("  AZURE_OPENAI_API_KEY=your_key")
        console.print("  AZURE_ENDPOINT=https://your-resource.openai.azure.com")
        console.print("  AZURE_API_VERSION=2025-03-01-preview")
        console.print("  AZURE_CHAT_DEPLOYMENT=gpt-5-mini")
        sys.exit(1)
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
@click.option(
    "--reasoning-effort",
    "-r",
    type=click.Choice(["low", "medium", "high"], case_sensitive=False),
    default="medium",
    help="AI reasoning effort level (default: medium)",
)
def llm_suggest(path: Path, exclude: tuple[str, ...], reasoning_effort: str) -> None:
    """Get AI suggestions for which diagrams to generate.

    PATH: Directory containing Python code to analyze
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Analyzing code structure...", total=None)
            analyzer = CodeAnalyzer(path)
            analyzer.analyze(exclude_patterns=list(exclude))
            progress.update(task, completed=True)

            task = progress.add_task("[cyan]Getting AI suggestions...", total=None)
            llm_analyzer = LLMAnalyzer(analyzer)
            result = llm_analyzer.suggest_diagram_focus(
                reasoning_effort=reasoning_effort.lower()
            )
            progress.update(task, completed=True)

        if "error" in result:
            console.print(f"[red]✗[/red] {result['error']}", style="bold red")
            sys.exit(1)

        console.print("\n[bold cyan]AI Diagram Suggestions[/bold cyan]\n")
        console.print(result.get("suggestions", "No suggestions available"))

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}", style="bold red")
        console.print(
            "\n[yellow]Required:[/yellow] Set Azure OpenAI credentials in .env file"
        )
        sys.exit(1)
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
@click.option(
    "--reasoning-effort",
    "-r",
    type=click.Choice(["low", "medium", "high"], case_sensitive=False),
    default="medium",
    help="AI reasoning effort level (default: medium)",
)
def llm_explain(path: Path, exclude: tuple[str, ...], reasoning_effort: str) -> None:
    """Get natural language explanation of code dependencies.

    PATH: Directory containing Python code to analyze
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Analyzing dependencies...", total=None)
            analyzer = CodeAnalyzer(path)
            analyzer.analyze(exclude_patterns=list(exclude))
            progress.update(task, completed=True)

            task = progress.add_task("[cyan]Generating explanation...", total=None)
            llm_analyzer = LLMAnalyzer(analyzer)
            explanation = llm_analyzer.explain_dependency_graph(
                reasoning_effort=reasoning_effort.lower()
            )
            progress.update(task, completed=True)

        console.print("\n[bold cyan]Dependency Structure Explanation[/bold cyan]\n")
        console.print(explanation)

    except ValueError as e:
        console.print(f"[red]✗[/red] {e}", style="bold red")
        console.print(
            "\n[yellow]Required:[/yellow] Set Azure OpenAI credentials in .env file"
        )
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


if __name__ == "__main__":
    main()
