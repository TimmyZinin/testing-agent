"""
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
