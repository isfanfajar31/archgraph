"""LLM-powered code analysis using Azure OpenAI."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import AzureOpenAI

from archgraph.analyzer import CodeAnalyzer

# Load environment variables
load_dotenv()


class LLMAnalyzer:
    """Analyzes code using LLM to provide insights and recommendations."""

    def __init__(self, analyzer: CodeAnalyzer):
        """Initialize the LLM analyzer.

        Args:
            analyzer: CodeAnalyzer instance with parsed code
        """
        self.analyzer = analyzer
        self.client = self._initialize_client()

    def _initialize_client(self) -> AzureOpenAI | None:
        """Initialize Azure OpenAI client.

        Returns:
            AzureOpenAI client

        Raises:
            ValueError: If credentials not configured
        """
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_ENDPOINT")
        api_version = os.getenv("AZURE_API_VERSION", "2025-03-01-preview")

        if not api_key or not endpoint:
            raise ValueError(
                "Azure OpenAI credentials required. Set AZURE_OPENAI_API_KEY, "
                "AZURE_ENDPOINT, and optionally AZURE_API_VERSION in .env file"
            )

        return AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )

    def analyze_architecture(
        self,
        max_completion_tokens: int = 8000,
        reasoning_effort: str = "medium",
    ) -> dict[str, Any]:
        """Analyze the overall architecture using LLM.

        Args:
            max_completion_tokens: Maximum tokens for response
            reasoning_effort: Reasoning effort level ("low", "medium", "high")

        Returns:
            Dictionary with analysis results including:
            - summary: High-level architecture summary
            - patterns: Detected design patterns
            - issues: Potential architectural issues
            - recommendations: Suggested improvements
        """

        # Gather code structure information
        structure_info = self._gather_structure_info()

        # Create prompt
        prompt = self._create_architecture_prompt(structure_info)

        try:
            deployment = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-5-mini")
            response = self.client.chat.completions.create(
                model=deployment,
                messages=[
                    {
                        "role": "developer",
                        "content": "Formatting re-enabled. You are an expert software architect analyzing Python codebases. Provide insightful, actionable analysis.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=max_completion_tokens,
                reasoning_effort=reasoning_effort,
            )

            message = response.choices[0].message

            # GPT-5 may put content in reasoning_content or content
            content = message.content
            if not content and hasattr(message, "reasoning_content"):
                content = message.reasoning_content

            if not content:
                return {
                    "error": "Empty response from GPT-5",
                    "summary": "",
                    "patterns": [],
                    "issues": [],
                    "recommendations": [],
                }

            return self._parse_architecture_response(content)

        except Exception as e:
            return {
                "error": f"LLM analysis failed: {str(e)}",
                "summary": "",
                "patterns": [],
                "issues": [],
                "recommendations": [],
            }

    def analyze_class_design(
        self,
        module_name: str,
        class_name: str,
        reasoning_effort: str = "medium",
    ) -> dict[str, Any]:
        """Analyze a specific class design using LLM.

        Args:
            module_name: Module containing the class
            class_name: Name of the class to analyze
            reasoning_effort: Reasoning effort level ("low", "medium", "high")

        Returns:
            Dictionary with class analysis including design feedback
        """

        class_info = self.analyzer.get_class_info(module_name, class_name)
        if not class_info:
            return {"error": f"Class {class_name} not found in {module_name}"}

        prompt = f"""Analyze this Python class design:

Class: {class_name}
Module: {module_name}

Base Classes: {", ".join(class_info.get("bases", [])) or "None"}

Methods:
{self._format_methods(class_info.get("methods", []))}

Attributes:
{", ".join(class_info.get("attributes", [])) or "None"}

Docstring:
{class_info.get("docstring", "No docstring")}

Provide:
1. Design pattern(s) used (if any)
2. SOLID principles adherence
3. Potential issues or code smells
4. Specific recommendations for improvement
"""

        try:
            deployment = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-5-mini")
            response = self.client.chat.completions.create(
                model=deployment,
                messages=[
                    {
                        "role": "developer",
                        "content": "Formatting re-enabled. You are an expert in object-oriented design and Python best practices.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=3000,
                reasoning_effort=reasoning_effort,
            )

            message = response.choices[0].message
            content = message.content
            if not content and hasattr(message, "reasoning_content"):
                content = message.reasoning_content

            return {"analysis": content or "No analysis generated"}

        except Exception as e:
            return {"error": f"LLM analysis failed: {str(e)}"}

    def suggest_diagram_focus(self, reasoning_effort: str = "medium") -> dict[str, Any]:
        """Use LLM to suggest what to focus on in diagrams.

        Args:
            reasoning_effort: Reasoning effort level ("low", "medium", "high")

        Returns:
            Dictionary with suggestions for diagram generation
        """

        structure_info = self._gather_structure_info()
        dependencies = self.analyzer.get_dependencies()

        prompt = f"""Given this Python codebase structure:

Modules: {len(self.analyzer.modules)}
Classes: {sum(len(classes) for classes in self.analyzer.classes.values())}
Functions: {sum(len(funcs) for funcs in self.analyzer.functions.values())}

Module breakdown:
{self._format_module_breakdown()}

Key dependencies:
{self._format_dependencies(dependencies)}

Suggest:
1. Which diagram types would be most valuable (class, dependency, call graph, package structure)?
2. What depth/detail level to use?
3. Which modules/classes to focus on?
4. What architectural aspects to highlight?

Be specific and actionable.
"""

        try:
            deployment = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-5-mini")
            response = self.client.chat.completions.create(
                model=deployment,
                messages=[
                    {
                        "role": "developer",
                        "content": "Formatting re-enabled. You are an expert at software documentation and architecture visualization.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=3000,
                reasoning_effort=reasoning_effort,
            )

            message = response.choices[0].message

            content = message.content
            if not content and hasattr(message, "reasoning_content"):
                content = message.reasoning_content

            # Check for text attribute
            if not content and hasattr(message, "text"):
                content = message.text

            return {"suggestions": content or "No suggestions generated"}

        except Exception as e:
            return {"error": f"LLM analysis failed: {str(e)}"}

    def explain_dependency_graph(self, reasoning_effort: str = "medium") -> str:
        """Generate natural language explanation of dependency relationships.

        Args:
            reasoning_effort: Reasoning effort level ("low", "medium", "high")

        Returns:
            Human-readable explanation of dependencies
        """

        dependencies = self.analyzer.get_dependencies()

        prompt = f"""Explain the dependency structure of this Python codebase in natural language:

{self._format_dependencies(dependencies)}

Provide:
1. Overview of module organization
2. Key dependency patterns
3. Potential coupling issues
4. Suggestions for better modularity

Write in clear, accessible language.
"""

        try:
            deployment = os.getenv("AZURE_CHAT_DEPLOYMENT", "gpt-5-mini")
            response = self.client.chat.completions.create(
                model=deployment,
                messages=[
                    {
                        "role": "developer",
                        "content": "Formatting re-enabled. You are a technical writer explaining software architecture to developers.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_completion_tokens=3000,
                reasoning_effort=reasoning_effort,
            )

            message = response.choices[0].message

            content = message.content
            if not content and hasattr(message, "reasoning_content"):
                content = message.reasoning_content

            # Check for text attribute
            if not content and hasattr(message, "text"):
                content = message.text

            return content or "No explanation generated"

        except Exception as e:
            return f"LLM analysis failed: {str(e)}"

    def _gather_structure_info(self) -> dict[str, Any]:
        """Gather structural information about the codebase.

        Returns:
            Dictionary with structure information
        """
        return {
            "total_modules": len(self.analyzer.modules),
            "total_classes": sum(
                len(classes) for classes in self.analyzer.classes.values()
            ),
            "total_functions": sum(
                len(funcs) for funcs in self.analyzer.functions.values()
            ),
            "module_breakdown": {
                module: {
                    "classes": len(self.analyzer.classes.get(module, [])),
                    "functions": len(self.analyzer.functions.get(module, [])),
                }
                for module in self.analyzer.modules.keys()
            },
        }

    def _create_architecture_prompt(self, structure_info: dict[str, Any]) -> str:
        """Create prompt for architecture analysis.

        Args:
            structure_info: Structure information dictionary

        Returns:
            Formatted prompt string
        """
        dependencies = self.analyzer.get_dependencies()

        return f"""Analyze this Python codebase architecture:

## Structure
- Total Modules: {structure_info["total_modules"]}
- Total Classes: {structure_info["total_classes"]}
- Total Functions: {structure_info["total_functions"]}

## Module Breakdown
{self._format_module_breakdown()}

## Dependencies
{self._format_dependencies(dependencies)}

## Package Structure
{self._format_package_structure()}

Provide a comprehensive analysis covering:
1. **Architecture Summary**: Overall design and organization
2. **Design Patterns**: Patterns identified in the codebase
3. **Potential Issues**: Architectural concerns, code smells, or anti-patterns
4. **Recommendations**: Specific, actionable improvements

Format your response clearly with these four sections.
"""

    def _format_module_breakdown(self) -> str:
        """Format module breakdown for prompts.

        Returns:
            Formatted string
        """
        lines = []
        for module_name in sorted(self.analyzer.modules.keys())[:20]:  # Limit to 20
            class_count = len(self.analyzer.classes.get(module_name, []))
            func_count = len(self.analyzer.functions.get(module_name, []))
            lines.append(
                f"- {module_name}: {class_count} classes, {func_count} functions"
            )
        return "\n".join(lines) if lines else "No modules"

    def _format_dependencies(self, dependencies: dict[str, set[str]]) -> str:
        """Format dependencies for prompts.

        Args:
            dependencies: Dependency dictionary

        Returns:
            Formatted string
        """
        lines = []
        for module, deps in sorted(dependencies.items())[:20]:  # Limit to 20
            if deps:
                lines.append(f"- {module} → {', '.join(sorted(deps)[:5])}")
        return "\n".join(lines) if lines else "No dependencies"

    def _format_package_structure(self) -> str:
        """Format package structure for prompts.

        Returns:
            Formatted string
        """
        structure = self.analyzer.get_package_structure()
        return self._format_structure_recursive(structure, indent=0, max_depth=3)

    def _format_structure_recursive(
        self, structure: dict[str, Any], indent: int, max_depth: int
    ) -> str:
        """Recursively format package structure.

        Args:
            structure: Structure dictionary
            indent: Current indentation level
            max_depth: Maximum depth to traverse

        Returns:
            Formatted string
        """
        if indent > max_depth:
            return ""

        lines = []
        for name, content in sorted(structure.items()):
            if name.startswith("_"):
                continue

            prefix = "  " * indent
            lines.append(f"{prefix}- {name}")

            if isinstance(content, dict):
                lines.append(
                    self._format_structure_recursive(content, indent + 1, max_depth)
                )

        return "\n".join(lines)

    def _format_methods(self, methods: list[dict[str, Any]]) -> str:
        """Format method list for prompts.

        Args:
            methods: List of method dictionaries

        Returns:
            Formatted string
        """
        lines = []
        for method in methods[:15]:  # Limit to 15 methods
            name = method.get("name", "unknown")
            args = ", ".join(method.get("args", []))
            returns = method.get("returns", "")
            return_str = f" -> {returns}" if returns else ""
            lines.append(f"- {name}({args}){return_str}")
        return "\n".join(lines) if lines else "No methods"

    def _parse_architecture_response(self, content: str) -> dict[str, Any]:
        """Parse LLM response into structured format.

        Args:
            content: LLM response content

        Returns:
            Structured dictionary
        """
        # If content is empty or None, return empty structure
        if not content or not content.strip():
            return {
                "summary": "",
                "patterns": [],
                "issues": [],
                "recommendations": [],
            }

        # Simple parsing - split by bullet points
        sections = {
            "summary": "",
            "patterns": [],
            "issues": [],
            "recommendations": [],
        }

        lines = content.split("\n")
        summary_lines = []
        pattern_lines = []
        issue_lines = []
        recommendation_lines = []

        current_section = None

        for line in lines:
            stripped = line.strip()

            # Detect section headers (case insensitive)
            lower_line = stripped.lower()

            # Check if this is a header line
            if "design pattern" in lower_line and ":" in stripped:
                current_section = "patterns"
                continue
            elif "potential issue" in lower_line and ":" in stripped:
                current_section = "issues"
                continue
            elif "recommendation" in lower_line and ":" in stripped:
                current_section = "recommendations"
                continue
            elif stripped.startswith(("Summary:", "Architecture Summary:")):
                current_section = "summary"
                continue

            # Add content to appropriate section
            if not stripped:
                continue

            if current_section == "patterns":
                if stripped.startswith(("•", "-", "*", "✓", "⚠")):
                    pattern_lines.append(stripped.lstrip("•-*✓⚠ "))
            elif current_section == "issues":
                if stripped.startswith(("•", "-", "*", "✓", "⚠")):
                    issue_lines.append(stripped.lstrip("•-*✓⚠ "))
            elif current_section == "recommendations":
                if stripped.startswith(("•", "-", "*", "✓", "⚠")):
                    recommendation_lines.append(stripped.lstrip("•-*✓⚠ "))
            elif current_section == "summary":
                summary_lines.append(stripped)
            else:
                # Before any section header, assume it's summary
                summary_lines.append(stripped)

        # Build result
        sections["summary"] = "\n".join(summary_lines).strip()
        sections["patterns"] = pattern_lines if pattern_lines else []
        sections["issues"] = issue_lines if issue_lines else []
        sections["recommendations"] = (
            recommendation_lines if recommendation_lines else []
        )

        # If we have content but no structured sections, put everything in summary
        if content.strip() and not any(
            [pattern_lines, issue_lines, recommendation_lines]
        ):
            sections["summary"] = content.strip()

        return sections
