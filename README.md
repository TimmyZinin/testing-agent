# Testing Agent 🧪

AI-powered test generation using CrewAI framework.

## Overview

Testing Agent automatically generates comprehensive unit tests for your Python code using a team of specialized AI agents:

1. **Code Analyzer** - Analyzes code structure, identifies testable units
2. **QA Test Agent** - Writes comprehensive tests following best practices
3. **Test Validator** - Validates generated tests for quality and correctness

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run on example file
python src/main.py --example

# Run on your file
python src/main.py src/your_module.py

# Specify output location
python src/main.py src/utils.py --output tests/test_utils.py
```

## Requirements

- Python 3.10+
- OpenAI API key (set `OPENAI_API_KEY` environment variable)

## Installation

```bash
# Clone repository
git clone https://github.com/TimmyZinin/testing-agent.git
cd testing-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install
pip install -e ".[dev]"

# Set API key
export OPENAI_API_KEY="your-key-here"
```

## Usage

### Command Line

```bash
# Basic usage
python src/main.py path/to/file.py

# With options
python src/main.py src/calculator.py \
    --type unit \
    --framework pytest \
    --output tests/test_calculator.py

# Run example
python src/main.py --example
```

### As Library

```python
from src.crew import TestingCrew

crew = TestingCrew()

# Generate and save tests
output_path = crew.run_and_save(
    file_path="src/calculator.py",
    test_type="unit",
    test_framework="pytest"
)

print(f"Tests saved to: {output_path}")
```

## Project Structure

```
testing-agent/
├── config/
│   ├── agents.yaml      # Agent definitions (role, goal, backstory)
│   └── tasks.yaml       # Task definitions (what each agent does)
├── src/
│   ├── crew.py          # TestingCrew class - orchestrates agents
│   ├── main.py          # CLI entry point
│   └── tools/
│       └── coverage_tool.py  # Custom tools for coverage analysis
├── tests/
│   └── test_crew.py     # Self-tests for the agent
├── examples/
│   └── calculator.py    # Example file for testing
├── pyproject.toml       # Project configuration
└── README.md
```

## Configuration

### agents.yaml

Defines the AI agents with their roles:

```yaml
qa_test_agent:
  role: "Senior QA Engineer specializing in {test_type} testing"
  goal: "Ensure code quality by writing comprehensive tests..."
  backstory: "You are a battle-tested QA engineer..."
```

### tasks.yaml

Defines what each agent does:

```yaml
write_tests_task:
  description: "Write {test_type} tests for the analyzed code..."
  expected_output: "Complete, runnable test file..."
  agent: qa_test_agent
```

## Principles

This project follows key AI agent design principles:

1. **80/20 Rule** - 80% effort on task design, 20% on agent definition
2. **Narrow Specialization** - Each agent has one clear responsibility
3. **Minimal Tools** - Agents only have access to necessary tools
4. **Sequential Pipeline** - Analyze → Write → Validate
5. **Safe Execution** - Code runs in Docker sandbox

## Testing the Agent

```bash
# Run self-tests
python tests/test_crew.py

# With pytest
pytest tests/ -v
```

## License

MIT
