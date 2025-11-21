# ArchGraph

**Architecture Diagram Generator with GPT-5 AI** - Generate software architecture diagrams from Python code with GPT-5-powered insights.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Server](https://img.shields.io/badge/MCP-Server-blue.svg)](https://modelcontextprotocol.io/)

ArchGraph analyzes Python codebases and automatically generates various types of architecture diagrams to help you understand and document your project's structure. Enhanced with Azure OpenAI GPT-5-mini integration for intelligent code analysis and recommendations. Includes Model Context Protocol (MCP) server for seamless integration with AI assistants.

## Features

### Core Features

- 🏗️ **Multiple Diagram Types**
  - Class diagrams (UML-style with inheritance, methods, and attributes)
  - Dependency graphs (module and package relationships)
  - Call graphs (function/method call relationships)
  - Package structure diagrams (hierarchical project organization)

- 📊 **Multiple Output Formats**
  - **Mermaid** - Markdown-compatible, GitHub-friendly
  - **PlantUML** - Standard UML format
  - **GraphViz** - Direct image output (PNG, SVG, PDF, JPG)

- 🔧 **Highly Configurable**
  - Filter by depth, visibility (public/private)
  - Include/exclude external dependencies
  - Customizable layout engines (GraphViz)
  - Exclude patterns for test files and more

- 💻 **Rich CLI Experience**
  - Beautiful terminal output with progress indicators
  - Detailed code analysis and statistics
  - Batch generation of multiple diagram types

- 🤖 **GPT-5-Mini AI Analysis** (Required)
  - Comprehensive architecture analysis with reasoning effort control
  - Design pattern detection
  - Architectural issue identification
  - Actionable improvement recommendations
  - Natural language dependency explanations
  - AI-powered diagram suggestions

- 🔌 **MCP Server Integration**
  - FastMCP-based Model Context Protocol server
  - 7 tools for AI assistants (Claude Desktop, Cline, etc.)
  - Seamless integration with LLM workflows
  - Automatic code analysis and diagram generation

## Installation

### Using uv (recommended)

```bash
uv pip install archgraph
```

### Using pip

```bash
pip install archgraph
```

### From source

```bash
git clone https://github.com/tsoernes/archgraph.git
cd archgraph
uv sync
```

### Configure AI Features (Required)

AI features are **required** in ArchGraph. Create a `.env` file:

```bash
# Azure OpenAI GPT-5 credentials (REQUIRED)
AZURE_OPENAI_API_KEY=your_api_key
AZURE_ENDPOINT=https://your-resource.openai.azure.com
AZURE_API_VERSION=2025-03-01-preview
AZURE_CHAT_DEPLOYMENT=gpt-5-mini
```

### MCP Server Setup

To use ArchGraph with AI assistants (Claude Desktop, Cline, Zed, etc.), add to your MCP configuration:

```json
{
  "mcpServers": {
    "archgraph": {
      "enabled": true,
      "source": "custom",
      "command": "uv",
      "args": [
        "run",
        "--project",
        "/home/torstein.sornes/code/archgraph",
        "python",
        "-m",
        "archgraph.mcp_server"
      ],
      "env": {
        "AZURE_OPENAI_API_KEY": "your_api_key",
        "AZURE_ENDPOINT": "https://your-resource.openai.azure.com",
        "AZURE_API_VERSION": "2025-03-01-preview",
        "AZURE_CHAT_DEPLOYMENT": "gpt-5-mini"
      }
    }
  }
}
```

See [docs/MCP_SETUP.md](docs/MCP_SETUP.md) for detailed MCP server configuration and usage.
```

<old_text line=75>
Get AI-powered architecture analysis:

```bash
archgraph llm-analyze ./my_project
```

## Quick Start

Generate all diagram types for your project:

```bash
archgraph generate ./my_project --output ./diagrams
```

Get AI-powered architecture analysis:

```bash
archgraph llm-analyze ./my_project
```

This will create:
- `diagrams/class_diagram.mmd`
- `diagrams/dependency_graph.mmd`
- `diagrams/call_graph.mmd`
- `diagrams/package_structure.mmd`

## Usage

### Generate Diagrams

**Basic usage:**
```bash
archgraph generate /path/to/project
```

**Specify output directory and format:**
```bash
archgraph generate ./src --output ./docs/diagrams --format plantuml
```

**Generate specific diagram types:**
```bash
archgraph generate ./src --class-diagram --dependency-graph
```

**Generate all formats:**
```bash
archgraph generate ./src --format all
```

**Exclude test files:**
```bash
archgraph generate ./src --exclude "test_*" --exclude "*_test.py"
```

**Configure class diagrams:**
```bash
# Include private members and limit depth
archgraph generate ./src --class-diagram --include-private --max-depth 2

# Exclude methods and attributes for high-level overview
archgraph generate ./src --class-diagram --no-methods --no-attributes
```

**GraphViz options:**
```bash
# Use different layout engine and output format
archgraph generate ./src --format graphviz \
  --graphviz-layout neato \
  --graphviz-format svg
```

### Analyze Code

Get statistics and insights about your codebase:

```bash
archgraph analyze ./src
```

### GPT-5 AI-Powered Analysis

**Architecture Analysis with Reasoning Effort:**
```bash
# Get comprehensive AI analysis of your architecture
archgraph llm-analyze ./src --reasoning-effort medium

# Deep analysis with high reasoning (slower, more detailed)
archgraph llm-analyze ./src --reasoning-effort high

# Save analysis to file
archgraph llm-analyze ./src --save analysis.md --reasoning-effort high
```

**Diagram Suggestions:**
```bash
# Get AI suggestions on which diagrams to generate
archgraph llm-suggest ./src --reasoning-effort medium
```

**Dependency Explanation:**
```bash
# Get natural language explanation of dependencies
archgraph llm-explain ./src --reasoning-effort medium
```

### MCP Server Tools

When connected via MCP, AI assistants can use these tools:

- `analyze_codebase` - Get project structure information
- `generate_class_diagram` - Create class diagrams
- `generate_dependency_graph` - Create dependency graphs
- `generate_all_diagrams` - Generate all diagram types
- `ai_analyze_architecture` - GPT-5 architecture analysis
- `ai_suggest_diagrams` - AI recommendations for diagrams
- `ai_explain_dependencies` - Natural language explanations

**Example usage with Claude Desktop:**
```
Analyze the codebase at /path/to/project and suggest which diagrams to generate
```

See [docs/MCP_SETUP.md](docs/MCP_SETUP.md) for complete MCP server documentation.
```

<old_text line=444>
## AI Features

ArchGraph includes optional AI-powered features using Azure OpenAI:

- **Architecture Analysis** - Get comprehensive insights about your codebase design
- **Design Pattern Detection** - Automatically identify patterns in your code
- **Recommendations** - Receive actionable suggestions for improvements
- **Diagram Suggestions** - AI recommends which diagrams would be most valuable
- **Natural Language Explanations** - Understand complex dependencies in plain English

To enable AI features, set up Azure OpenAI credentials in a `.env` file.

This displays:
- Number of modules, classes, and functions
- Import relationships
- External dependencies
- Detailed module breakdown

### View Supported Formats

```bash
archgraph formats
```

## Examples

### Example 1: Django Project

```bash
# Generate dependency graph excluding migrations and tests
archgraph generate ./myapp \
  --dependency-graph \
  --exclude "migrations/*" \
  --exclude "*/tests/*" \
  --include-external \
  --format mermaid
```

### Example 2: Package Documentation

```bash
# Generate class diagrams with full details for documentation
archgraph generate ./src/mypackage \
  --class-diagram \
  --include-private \
  --format all \
  --output ./docs/architecture
```

### Example 3: High-Level Overview

```bash
# Generate simplified package structure for presentations
archgraph generate ./src \
  --package-structure \
  --max-depth 2 \
  --format graphviz \
  --graphviz-format pdf
```

### Example 4: AI-Powered Analysis

```bash
# Get comprehensive architecture analysis with AI
archgraph llm-analyze ./src --save ai-analysis.md

# Get suggestions for what diagrams would be most valuable
archgraph llm-suggest ./src
```

## Output Format Details

### Mermaid (.mmd)

Markdown-compatible diagrams that can be rendered directly in:
- GitHub/GitLab README files
- Markdown editors (Obsidian, Typora, VS Code with extensions)
- Documentation sites (MkDocs, Docusaurus)

**Example:**
```mermaid
classDiagram
    class MyClass {
        +attribute1
        +attribute2
        +method1(arg1, arg2)
        +method2() str
    }
```

### PlantUML (.puml)

Standard UML format that can be rendered using:
- PlantUML online server
- IDE plugins (IntelliJ, VS Code)
- Documentation generators

**Example:**
```plantuml
@startuml
class MyClass {
  +attribute1
  +attribute2
  --
  +method1(arg1, arg2)
  +method2(): str
}
@enduml
```

### GraphViz (PNG, SVG, PDF, JPG)

Direct image output, ready for:
- Presentations
- Documentation
- Reports
- Embedding in websites

## Advanced Usage

### Python API

Use ArchGraph programmatically in your Python code:

```python
from archgraph import (
    CodeAnalyzer,
    ClassDiagramGenerator,
    DependencyGraphGenerator,
    MermaidExporter,
    LLMAnalyzer,
)

# Analyze code
analyzer = CodeAnalyzer("./my_project")
analyzer.analyze(exclude_patterns=["test_*"])

# Generate class diagram
generator = ClassDiagramGenerator(analyzer)
graph = generator.generate(
    include_methods=True,
    include_attributes=True,
    include_private=False
)

# Export to Mermaid
exporter = MermaidExporter()
exporter.export(graph, "class_diagram.mmd", diagram_type="class")

# Or get as string
mermaid_code = exporter.to_string(graph, diagram_type="class")
print(mermaid_code)

# Use AI analysis (requires Azure OpenAI credentials)
llm_analyzer = LLMAnalyzer(analyzer)
results = llm_analyzer.analyze_architecture()
print(results["summary"])
```

### Custom Filtering

```python
from archgraph import CodeAnalyzer, DependencyGraphGenerator, LLMAnalyzer

analyzer = CodeAnalyzer("./src")
analyzer.analyze()

# Generate dependency graph with custom options
generator = DependencyGraphGenerator(analyzer)
graph = generator.generate(
    group_by_package=True,
    include_external=False,
    max_depth=3
)

# Get AI explanation of dependencies
llm = LLMAnalyzer(analyzer)
explanation = llm.explain_dependency_graph()
print(explanation)
```

## Configuration Options

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output, -o` | Output directory | `diagrams` |
| `--format, -f` | Output format (mermaid/plantuml/graphviz/all) | `mermaid` |
| `--exclude, -e` | Patterns to exclude (can be used multiple times) | None |
| `--all-diagrams, -a` | Generate all diagram types | False |
| `--class-diagram` | Generate class diagram | False |
| `--dependency-graph` | Generate dependency graph | False |
| `--call-graph` | Generate call graph | False |
| `--package-structure` | Generate package structure | False |
| `--include-private` | Include private members (starting with _) | False |
| `--no-methods` | Exclude methods from class diagrams | False |
| `--no-attributes` | Exclude attributes from class diagrams | False |
| `--max-depth` | Maximum depth for hierarchical diagrams | None |
| `--include-external` | Include external dependencies | False |
| `--graphviz-layout` | GraphViz layout engine (dot/neato/fdp/sfdp/circo/twopi) | `dot` |
| `--graphviz-format` | GraphViz output format (png/svg/pdf/jpg) | `png` |

### GraphViz Layout Engines

- **dot** - Hierarchical layouts (default, best for trees and DAGs)
- **neato** - Spring model layouts (good for small graphs)
- **fdp** - Force-directed placement (good for large graphs)
- **sfdp** - Scalable force-directed placement (best for very large graphs)
- **circo** - Circular layouts
- **twopi** - Radial layouts

## Requirements

- Python 3.13+
- Dependencies (automatically installed):
  - click - CLI framework
  - rich - Terminal formatting
  - networkx - Graph operations
  - astroid - Python AST analysis
  - graphviz - Diagram generation
  - Pillow - Image processing
  - openai - Azure OpenAI integration (for AI features)
  - python-dotenv - Environment variable management

For GraphViz output, you also need GraphViz installed on your system:

**Linux (Fedora):**
```bash
sudo dnf install graphviz
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install graphviz
```

**macOS:**
```bash
brew install graphviz
```

**Windows:**
Download from https://graphviz.org/download/

## Future Features (Nice-to-Have)

These features are planned for future releases:

### 🤖 Enhanced AI Features
- **More AI providers** - Support for other LLM providers (OpenAI, Anthropic, local models)
- **Fine-tuned analysis** - Domain-specific architecture analysis
- **AI-generated diagrams** - Let AI decide optimal diagram layouts
- **Code generation** - Generate boilerplate from architecture descriptions

### 📈 Advanced Analysis
- **Complexity metrics visualization** - Cyclomatic complexity, coupling, cohesion
- **Code smell detection** - Highlight potential issues in architecture (partially implemented with AI)
- **Change impact analysis** - Show what would be affected by changes

### 🎨 Enhanced Visualization
- **Interactive HTML diagrams** - Clickable, zoomable diagrams
- **Syntax highlighting** - Code snippets in diagrams
- **Custom themes** - Configurable color schemes and styles
- **3D diagrams** - For complex dependency graphs

### 🔄 Dynamic Features
- **Watch mode** - Auto-regenerate diagrams on code changes
- **Live server** - View diagrams in browser with hot reload
- **Diff mode** - Compare diagrams between git commits

### 🚀 Integration & Automation
- **GitHub Action** - Automatic diagram updates in CI/CD
- **Pre-commit hook** - Generate diagrams before commit
- **Documentation generators** - Integration with Sphinx, MkDocs
- **IDE plugins** - VS Code, PyCharm extensions

### 🌐 Multi-Language Support
- **JavaScript/TypeScript** - Analyze JS/TS projects
- **Java** - Support for Java codebases
- **Go** - Analyze Go projects
- **Multi-language projects** - Handle polyglot repositories

### 📊 Additional Diagram Types
- **Sequence diagrams** - Show method call sequences
- **State diagrams** - Visualize state machines
- **Entity-relationship diagrams** - For ORM models
- **Architecture decision records (ADRs)** - Link diagrams to decisions

### 🎯 Smart Analysis
- **AI-powered insights** - Suggestions for improvements
- **Pattern detection** - Identify design patterns in code
- **Refactoring suggestions** - Based on architecture analysis

## AI Features

ArchGraph includes optional AI-powered features using Azure OpenAI:

- **Architecture Analysis** - Get comprehensive insights about your codebase design
- **Design Pattern Detection** - Automatically identify patterns in your code
- **Recommendations** - Receive actionable suggestions for improvements
- **Diagram Suggestions** - AI recommends which diagrams would be most valuable
- **Natural Language Explanations** - Understand complex dependencies in plain English

To enable AI features, set up Azure OpenAI credentials in a `.env` file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Torstein Sørnes** - [t.soernes@gmail.com](mailto:t.soernes@gmail.com)

## Acknowledgments

- Built with [astroid](https://github.com/pylint-dev/astroid) for Python AST analysis
- Uses [NetworkX](https://networkx.org/) for graph operations
- CLI powered by [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)
- Diagram generation with [GraphViz](https://graphviz.org/)
- AI features powered by [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)

## Links

- **Repository**: https://github.com/tsoernes/archgraph
- **Issues**: https://github.com/tsoernes/archgraph/issues
- **PyPI**: https://pypi.org/project/archgraph/ (coming soon)

---

**Star ⭐ this project if you find it useful!**