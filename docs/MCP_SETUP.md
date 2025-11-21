# ArchGraph MCP Server Setup Guide

This guide explains how to set up and use the ArchGraph MCP (Model Context Protocol) server with various MCP clients.

## Overview

ArchGraph provides an MCP server that exposes its architecture analysis and diagram generation capabilities through the Model Context Protocol. This allows AI assistants like Claude Desktop, Cline, and other MCP clients to analyze codebases and generate diagrams.

## Prerequisites

- Python 3.13+
- `uv` package manager installed
- Azure OpenAI credentials (required for AI features)
- ArchGraph installed at: `/home/torstein.sornes/code/archgraph`

## Configuration

### Environment Variables

Create a `.env` file in the ArchGraph directory with your Azure OpenAI credentials:

```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_ENDPOINT=https://your-resource.openai.azure.com
AZURE_API_VERSION=2025-03-01-preview
AZURE_CHAT_DEPLOYMENT=gpt-5-mini
```

### MCP Server Configuration

Add the following configuration to your MCP client's settings:

#### For Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or equivalent on other platforms:

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
        "AZURE_OPENAI_API_KEY": "your_api_key_here",
        "AZURE_ENDPOINT": "https://your-resource.openai.azure.com",
        "AZURE_API_VERSION": "2025-03-01-preview",
        "AZURE_CHAT_DEPLOYMENT": "gpt-5-mini"
      }
    }
  }
}
```

**Note:** You can either set the environment variables in the config or rely on the `.env` file in the ArchGraph directory.

#### For Cline (VS Code Extension)

Add to your Cline MCP settings:

```json
{
  "archgraph": {
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
      "AZURE_OPENAI_API_KEY": "your_api_key_here",
      "AZURE_ENDPOINT": "https://your-resource.openai.azure.com"
    }
  }
}
```

#### For Zed Editor

Add to your Zed MCP configuration:

```json
{
  "context_servers": {
    "archgraph": {
      "command": {
        "program": "uv",
        "args": [
          "run",
          "--project",
          "/home/torstein.sornes/code/archgraph",
          "python",
          "-m",
          "archgraph.mcp_server"
        ]
      },
      "settings": {
        "env": {
          "AZURE_OPENAI_API_KEY": "your_api_key_here",
          "AZURE_ENDPOINT": "https://your-resource.openai.azure.com"
        }
      }
    }
  }
}
```

## Available Tools

The ArchGraph MCP server exposes the following tools:

### 1. analyze_codebase

Analyze a Python codebase and return structural information.

**Parameters:**
- `path` (string, required): Path to the Python project directory
- `exclude_patterns` (list of strings, optional): Glob patterns to exclude (e.g., `["test_*", "*_test.py"]`)

**Returns:**
- `total_modules`: Number of Python modules
- `total_classes`: Number of classes
- `total_functions`: Number of functions
- `total_imports`: Number of import statements
- `modules`: List of module names
- `dependencies`: Dictionary of module dependencies

**Example usage in Claude:**
```
Can you analyze the codebase at /path/to/my/project?
```

### 2. generate_class_diagram

Generate a class diagram from Python code.

**Parameters:**
- `path` (string, required): Path to the Python project directory
- `output_path` (string, required): Path where the diagram should be saved
- `format` (string, optional): Output format - "mermaid" (default), "plantuml", or "graphviz"
- `include_methods` (boolean, optional): Include method details (default: true)
- `include_attributes` (boolean, optional): Include attribute details (default: true)
- `include_private` (boolean, optional): Include private members (default: false)
- `exclude_patterns` (list of strings, optional): Patterns to exclude

**Returns:**
- `status`: "success" or error information
- `output_path`: Full path to the generated diagram
- `format`: Format used

**Example usage in Claude:**
```
Generate a class diagram for /path/to/project and save it to /tmp/class_diagram.mmd
```

### 3. generate_dependency_graph

Generate a dependency graph showing module relationships.

**Parameters:**
- `path` (string, required): Path to the Python project directory
- `output_path` (string, required): Path where the diagram should be saved
- `format` (string, optional): Output format - "mermaid", "plantuml", or "graphviz"
- `include_external` (boolean, optional): Include external dependencies (default: true)
- `group_by_package` (boolean, optional): Group modules by package (default: true)
- `exclude_patterns` (list of strings, optional): Patterns to exclude

**Returns:**
- `status`: "success" or error information
- `output_path`: Full path to the generated diagram
- `format`: Format used

**Example usage in Claude:**
```
Create a dependency graph for /path/to/project showing only internal dependencies
```

### 4. ai_analyze_architecture

Use AI (GPT-5-mini) to analyze code architecture and provide insights.

**Parameters:**
- `path` (string, required): Path to the Python project directory
- `reasoning_effort` (string, optional): AI reasoning level - "low", "medium" (default), or "high"
- `exclude_patterns` (list of strings, optional): Patterns to exclude

**Returns:**
- `summary`: High-level architecture overview
- `patterns`: List of detected design patterns
- `issues`: List of potential architectural issues
- `recommendations`: List of improvement suggestions

**Example usage in Claude:**
```
Analyze the architecture of /path/to/project with high reasoning effort
```

### 5. ai_suggest_diagrams

Get AI suggestions for which diagrams to generate.

**Parameters:**
- `path` (string, required): Path to the Python project directory
- `reasoning_effort` (string, optional): "low", "medium" (default), or "high"
- `exclude_patterns` (list of strings, optional): Patterns to exclude

**Returns:**
- `suggestions`: AI-generated suggestions for diagram generation

**Example usage in Claude:**
```
What diagrams should I generate for /path/to/project?
```

### 6. ai_explain_dependencies

Get natural language explanation of code dependencies.

**Parameters:**
- `path` (string, required): Path to the Python project directory
- `reasoning_effort` (string, optional): "low", "medium" (default), or "high"
- `exclude_patterns` (list of strings, optional): Patterns to exclude

**Returns:**
- String with natural language explanation

**Example usage in Claude:**
```
Explain the dependencies in /path/to/project
```

### 7. generate_all_diagrams

Generate all diagram types (class, dependency, call graph, package structure) at once.

**Parameters:**
- `path` (string, required): Path to the Python project directory
- `output_dir` (string, required): Directory where diagrams should be saved
- `format` (string, optional): Output format - "mermaid", "plantuml", or "graphviz"
- `include_external` (boolean, optional): Include external dependencies (default: false)
- `exclude_patterns` (list of strings, optional): Patterns to exclude

**Returns:**
- `status`: "success" or error information
- `generated_diagrams`: List of paths to generated diagrams
- `output_directory`: Full path to output directory
- `format`: Format used

**Example usage in Claude:**
```
Generate all diagrams for /path/to/project in the /tmp/diagrams directory
```

## Testing the MCP Server

### Manual Testing

You can run the MCP server directly for testing:

```bash
cd /home/torstein.sornes/code/archgraph
uv run python -m archgraph.mcp_server
```

The server will start and wait for MCP client connections via stdio.

### Testing with MCP Inspector

Use the MCP Inspector tool to test the server:

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector
mcp-inspector uv run --project /home/torstein.sornes/code/archgraph python -m archgraph.mcp_server
```

## Troubleshooting

### Server Not Starting

1. **Check uv installation:**
   ```bash
   uv --version
   ```

2. **Verify Python version:**
   ```bash
   python --version  # Should be 3.13+
   ```

3. **Check ArchGraph installation:**
   ```bash
   cd /home/torstein.sornes/code/archgraph
   uv run python -c "import archgraph; print(archgraph.__version__)"
   ```

### Azure OpenAI Errors

If you see "Azure OpenAI credentials required" errors:

1. Check your `.env` file exists and contains correct credentials
2. Verify the credentials in your MCP client configuration
3. Test credentials directly:
   ```bash
   cd /home/torstein.sornes/code/archgraph
   uv run archgraph llm-analyze examples/sample_project
   ```

### Permission Errors

Ensure the MCP server has read access to the directories you want to analyze:

```bash
# Check permissions
ls -la /path/to/project

# Make directories readable if needed
chmod -R u+r /path/to/project
```

### Import Errors

If you see "Module not found" errors:

```bash
# Reinstall dependencies
cd /home/torstein.sornes/code/archgraph
uv sync
```

## Best Practices

### Security

1. **Never commit credentials** - Use environment variables or `.env` files
2. **Limit analysis scope** - Use `exclude_patterns` to skip sensitive files
3. **Review generated diagrams** - Check output before sharing

### Performance

1. **Use reasoning effort wisely:**
   - `low`: Quick analysis, basic insights (~2-5s)
   - `medium`: Balanced analysis (default, ~5-10s)
   - `high`: Deep analysis, detailed recommendations (~10-20s)

2. **Exclude unnecessary files:**
   ```json
   {
     "exclude_patterns": ["test_*", "*_test.py", "migrations/*", "*.pyc"]
   }
   ```

3. **Cache results** - AI analysis can be saved to files and reused

### Usage Tips

1. **Start with analyze_codebase** to understand project structure
2. **Use ai_suggest_diagrams** to get AI recommendations first
3. **Generate specific diagrams** based on suggestions
4. **Use ai_explain_dependencies** for documentation

## Example Workflows

### Workflow 1: New Project Analysis

```
User: Analyze the codebase at /path/to/new/project
Claude: [uses analyze_codebase tool]

User: What diagrams should I generate?
Claude: [uses ai_suggest_diagrams tool]

User: Generate those diagrams
Claude: [uses generate_all_diagrams tool]
```

### Workflow 2: Architecture Review

```
User: Review the architecture of /path/to/project
Claude: [uses ai_analyze_architecture with high reasoning]

User: Show me the dependency structure
Claude: [uses ai_explain_dependencies]

User: Create a dependency graph
Claude: [uses generate_dependency_graph]
```

### Workflow 3: Documentation Generation

```
User: I need to document /path/to/project's architecture
Claude: [uses analyze_codebase, ai_analyze_architecture, generate_all_diagrams]
Claude: Creates comprehensive documentation with diagrams and AI insights
```

## Advanced Configuration

### Custom Deployment Names

If your Azure OpenAI deployment has a custom name:

```json
{
  "env": {
    "AZURE_CHAT_DEPLOYMENT": "my-custom-gpt-5-deployment"
  }
}
```

### Multiple Projects

You can configure multiple ArchGraph instances for different projects:

```json
{
  "mcpServers": {
    "archgraph-project1": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/archgraph", "python", "-m", "archgraph.mcp_server"],
      "env": {"PROJECT_ROOT": "/path/to/project1"}
    },
    "archgraph-project2": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/archgraph", "python", "-m", "archgraph.mcp_server"],
      "env": {"PROJECT_ROOT": "/path/to/project2"}
    }
  }
}
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/tsoernes/archgraph/issues
- Documentation: https://github.com/tsoernes/archgraph

## Version

This guide is for ArchGraph v0.3.0+

Last updated: 2024-11-21