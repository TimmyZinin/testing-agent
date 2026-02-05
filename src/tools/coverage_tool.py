"""
Custom Coverage Tool for CrewAI
Analyzes test coverage and suggests improvements
"""

from typing import Any, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class CoverageInput(BaseModel):
    """Input schema for CoverageTool"""
    source_file: str = Field(
        description="Path to the source file to analyze coverage for"
    )
    test_file: str = Field(
        description="Path to the test file"
    )


class CoverageTool(BaseTool):
    """
    Tool for analyzing test coverage.

    Uses coverage.py to measure which lines of code are executed
    during test runs and provides detailed coverage reports.
    """

    name: str = "coverage_analyzer"
    description: str = (
        "Analyzes test coverage for a source file. "
        "Returns percentage covered, uncovered lines, and suggestions. "
        "Input: source_file path and test_file path."
    )
    args_schema: Type[BaseModel] = CoverageInput

    def _run(self, source_file: str, test_file: str) -> str:
        """
        Run coverage analysis.

        Args:
            source_file: Path to source file
            test_file: Path to test file

        Returns:
            Coverage report as string
        """
        try:
            import coverage
            import subprocess
            import json
            from pathlib import Path

            # Создаём coverage объект
            cov = coverage.Coverage(
                source=[str(Path(source_file).parent)],
                omit=["*test*", "*__pycache__*"]
            )

            # Запускаем тесты под coverage
            cov.start()

            result = subprocess.run(
                ["python", "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )

            cov.stop()
            cov.save()

            # Получаем данные
            analysis = cov.analysis(source_file)

            # analysis = (filename, statements, excluded, missing, formatted_missing)
            total_lines = len(analysis[1])
            missing_lines = len(analysis[3])
            covered_lines = total_lines - missing_lines

            coverage_percent = (covered_lines / total_lines * 100) if total_lines > 0 else 0

            report = {
                "source_file": source_file,
                "test_file": test_file,
                "coverage_percent": round(coverage_percent, 2),
                "total_lines": total_lines,
                "covered_lines": covered_lines,
                "missing_lines": list(analysis[3]),
                "test_output": result.stdout[-500:] if result.stdout else "",
                "test_errors": result.stderr[-500:] if result.stderr else "",
                "test_passed": result.returncode == 0
            }

            # Suggestions
            if coverage_percent < 80:
                report["suggestions"] = [
                    f"Coverage is {coverage_percent}%, target is 80%",
                    f"Add tests for lines: {', '.join(map(str, analysis[3][:10]))}",
                    "Focus on error handling paths and edge cases"
                ]
            else:
                report["suggestions"] = ["Coverage target met! Consider adding edge case tests."]

            return json.dumps(report, indent=2)

        except ImportError:
            return json.dumps({
                "error": "coverage package not installed",
                "fix": "pip install coverage pytest"
            })
        except subprocess.TimeoutExpired:
            return json.dumps({
                "error": "Test execution timed out",
                "fix": "Check for infinite loops or long-running tests"
            })
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "type": type(e).__name__
            })


class SyntaxCheckerInput(BaseModel):
    """Input schema for SyntaxCheckerTool"""
    code: str = Field(description="Python code to check for syntax errors")
    language: str = Field(default="python", description="Programming language")


class SyntaxCheckerTool(BaseTool):
    """
    Tool for checking code syntax without executing it.
    """

    name: str = "syntax_checker"
    description: str = (
        "Checks if code has valid syntax. "
        "Returns syntax errors if any, or confirms code is valid. "
        "Input: code string and language."
    )
    args_schema: Type[BaseModel] = SyntaxCheckerInput

    def _run(self, code: str, language: str = "python") -> str:
        """
        Check code syntax.

        Args:
            code: Code to check
            language: Programming language

        Returns:
            Syntax check result
        """
        import json

        if language != "python":
            return json.dumps({
                "valid": None,
                "message": f"Syntax checking for {language} not implemented"
            })

        try:
            compile(code, "<string>", "exec")
            return json.dumps({
                "valid": True,
                "message": "Code syntax is valid"
            })
        except SyntaxError as e:
            return json.dumps({
                "valid": False,
                "error": str(e),
                "line": e.lineno,
                "offset": e.offset,
                "text": e.text
            })


# Export tools
__all__ = ["CoverageTool", "SyntaxCheckerTool"]
