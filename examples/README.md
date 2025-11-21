# PyArchViz Examples

This directory contains example projects to demonstrate PyArchViz capabilities.

## Sample Project

The `sample_project` directory contains a simple e-commerce application with:

- **Models** (`models.py`) - Data classes for User, Product, Order, etc.
- **Services** (`services.py`) - Business logic for user management, orders, and payments
- **Utilities** (`utils.py`) - Helper classes for logging, configuration, validation
- **Main** (`main.py`) - Application entry point

### Generate Diagrams

From the `pyarchviz` root directory, run:

```bash
# Generate all diagram types in Mermaid format
pyarchviz generate examples/sample_project --output output/sample_diagrams

# Generate class diagram only with private members
pyarchviz generate examples/sample_project \
  --class-diagram \
  --include-private \
  --output output/class_only

# Generate in all formats
pyarchviz generate examples/sample_project \
  --format all \
  --output output/all_formats

# Generate dependency graph with external dependencies
pyarchviz generate examples/sample_project \
  --dependency-graph \
  --include-external \
  --output output/deps
```

### Analyze the Project

```bash
pyarchviz analyze examples/sample_project
```

Expected output:
- 4 modules (main, models, services, utils)
- 13 classes total
- Multiple external dependencies (pathlib, datetime, enum, etc.)

## Creating Your Own Examples

To test PyArchViz on your own projects:

1. Create a new directory with Python files
2. Run `pyarchviz generate <directory> --output <output_dir>`
3. View the generated diagrams in the output directory

## Tips

- Use `--exclude` to skip test files: `--exclude "test_*" --exclude "*_test.py"`
- Use `--max-depth` to limit diagram complexity for large projects
- Use `--no-methods --no-attributes` for high-level class overviews
- Try different GraphViz layouts: `--graphviz-layout neato` for force-directed graphs