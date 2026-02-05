#!/usr/bin/env python3
"""
Testing Agent - Entry Point

Запуск:
    python main.py <file_path>                    # Тестировать файл
    python main.py <file_path> --output tests/    # С указанием выхода
    python main.py --example                      # Запустить на примере

Примеры:
    python main.py src/calculator.py
    python main.py src/utils.py --framework pytest --type unit
"""

import argparse
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent))


def parse_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description="AI-powered test generation using CrewAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s src/calculator.py
  %(prog)s src/utils.py --output tests/test_utils.py
  %(prog)s src/api.py --type integration --framework pytest
  %(prog)s --example
        """
    )

    parser.add_argument(
        "file_path",
        nargs="?",
        help="Path to the file to generate tests for"
    )

    parser.add_argument(
        "--output", "-o",
        help="Output path for generated tests (default: tests/test_<filename>.py)"
    )

    parser.add_argument(
        "--type", "-t",
        choices=["unit", "integration", "e2e"],
        default="unit",
        help="Type of tests to generate (default: unit)"
    )

    parser.add_argument(
        "--framework", "-f",
        choices=["pytest", "unittest", "jest", "mocha"],
        default="pytest",
        help="Test framework to use (default: pytest)"
    )

    parser.add_argument(
        "--language", "-l",
        choices=["python", "javascript", "typescript"],
        default="python",
        help="Programming language (default: python)"
    )

    parser.add_argument(
        "--example",
        action="store_true",
        help="Run with example calculator file"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    return parser.parse_args()


def create_example_file() -> str:
    """Создать пример файла для тестирования"""
    example_dir = Path(__file__).parent.parent / "examples"
    example_dir.mkdir(exist_ok=True)

    example_path = example_dir / "calculator.py"

    example_code = '''"""
Simple Calculator Module
Example file for testing the Testing Agent
"""

from typing import Union

Number = Union[int, float]


class Calculator:
    """Basic calculator with history"""

    def __init__(self):
        self.history: list[str] = []

    def add(self, a: Number, b: Number) -> Number:
        """Add two numbers"""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a: Number, b: Number) -> Number:
        """Subtract b from a"""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def multiply(self, a: Number, b: Number) -> Number:
        """Multiply two numbers"""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

    def divide(self, a: Number, b: Number) -> float:
        """
        Divide a by b.

        Raises:
            ZeroDivisionError: If b is zero
        """
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result

    def power(self, base: Number, exponent: int) -> Number:
        """Raise base to the power of exponent"""
        if exponent < 0:
            raise ValueError("Exponent must be non-negative")
        result = base ** exponent
        self.history.append(f"{base} ^ {exponent} = {result}")
        return result

    def get_history(self) -> list[str]:
        """Return calculation history"""
        return self.history.copy()

    def clear_history(self) -> None:
        """Clear calculation history"""
        self.history = []


def factorial(n: int) -> int:
    """
    Calculate factorial of n.

    Args:
        n: Non-negative integer

    Returns:
        n! (n factorial)

    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def fibonacci(n: int) -> int:
    """
    Calculate nth Fibonacci number.

    Args:
        n: Position in Fibonacci sequence (0-indexed)

    Returns:
        nth Fibonacci number

    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative indices")
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def is_prime(n: int) -> bool:
    """
    Check if a number is prime.

    Args:
        n: Integer to check

    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True
'''

    with open(example_path, 'w', encoding='utf-8') as f:
        f.write(example_code)

    print(f"📁 Created example file: {example_path}")
    return str(example_path)


def main():
    """Main entry point"""
    args = parse_args()

    # Если запрос примера
    if args.example:
        file_path = create_example_file()
    elif args.file_path:
        file_path = args.file_path
    else:
        print("❌ Error: Please provide a file path or use --example")
        print("   Run with --help for usage information")
        sys.exit(1)

    # Проверяем существование файла
    if not Path(file_path).exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)

    print("=" * 60)
    print("🧪 Testing Agent - AI-Powered Test Generation")
    print("=" * 60)
    print(f"📄 File: {file_path}")
    print(f"🔧 Type: {args.type}")
    print(f"📦 Framework: {args.framework}")
    print(f"💻 Language: {args.language}")
    print("=" * 60)

    try:
        from crew import TestingCrew

        crew = TestingCrew()

        print("\n🚀 Starting test generation...\n")

        output_path = crew.run_and_save(
            file_path=file_path,
            output_path=args.output,
            test_type=args.type,
            test_framework=args.framework,
            language=args.language
        )

        print("\n" + "=" * 60)
        print("✅ Test generation completed!")
        print(f"📁 Tests saved to: {output_path}")
        print("=" * 60)

        # Показываем команду для запуска тестов
        if args.framework == "pytest":
            print(f"\n💡 Run tests with: pytest {output_path} -v")
        elif args.framework == "unittest":
            print(f"\n💡 Run tests with: python -m unittest {output_path}")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Install dependencies:")
        print("   pip install crewai crewai-tools pyyaml")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
