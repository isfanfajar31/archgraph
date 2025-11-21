# Changelog

All notable changes to PyArchViz will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Interactive HTML diagrams with zoom and navigation
- Watch mode for automatic diagram regeneration
- Complexity metrics visualization
- Multi-language support (JavaScript, TypeScript, Java)
- GitHub Action for CI/CD integration
- Sequence diagram generation
- State diagram generation
- IDE plugins (VS Code, PyCharm)

## [0.1.0] - 2024-11-21

### Added
- Initial release of PyArchViz
- Core code analyzer using astroid for Python AST parsing
- Four diagram types:
  - Class diagrams (UML-style with inheritance, methods, attributes)
  - Dependency graphs (module/package relationships)
  - Call graphs (function/method call relationships)
  - Package structure diagrams (hierarchical organization)
- Three output formats:
  - Mermaid (.mmd) - Markdown-compatible diagrams
  - PlantUML (.puml) - Standard UML format
  - GraphViz - Direct image output (PNG, SVG, PDF, JPG)
- Rich CLI interface with:
  - `generate` command for creating diagrams
  - `analyze` command for code statistics
  - `formats` command for format information
  - Progress indicators and beautiful output
- Configuration options:
  - Include/exclude patterns for files
  - Depth limiting for hierarchical diagrams
  - Private member visibility control
  - External dependency inclusion
  - GraphViz layout engine selection
- Comprehensive documentation:
  - README with usage examples
  - CONTRIBUTING guidelines
  - Example project demonstrating features
  - API documentation in docstrings
- Testing infrastructure:
  - pytest test suite
  - GitHub Actions CI/CD workflow
- MIT License
- Python 3.13+ support
- uv-based dependency management

### Technical Details
- Uses astroid for robust Python code parsing
- NetworkX for graph data structures
- Click for CLI framework
- Rich for terminal formatting
- GraphViz Python bindings for image generation

[Unreleased]: https://github.com/tsoernes/pyarchviz/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tsoernes/pyarchviz/releases/tag/v0.1.0