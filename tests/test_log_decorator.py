import importlib

import pytest

debug_logging_utils_module = importlib.import_module("src.2025.August.debug_logging_utils")
log = debug_logging_utils_module.log


@log
def add(a, b):
    return a + b


@log(prefix="MATH", print_return_value=False)
def multiply(a, b):
    return a * b


@log(propagate_exceptions=True)
def fail():
    raise ValueError("fail test")


@log(propagate_exceptions=False)
def soft_fail():
    raise RuntimeError("should not propagate")


def test_basic_logging(capsys):
    result = add(2, 3)
    captured = capsys.readouterr().out
    assert result == 5
    assert "\nadd(2, 3)" in captured
    assert f"Returned value:\n\t{result}" in captured


def test_with_prefix(capsys):
    result = multiply(4, 5)
    captured = capsys.readouterr().out
    assert result == 20
    assert "[MATH]: multiply(4, 5)" in captured
    assert f"Returned value:\n\t{result}" not in captured  # Because print_return_value=False


def test_exception_propagation():
    with pytest.raises(ValueError, match="fail test"):
        fail()


def test_exception_suppressed(capsys):
    result = soft_fail()
    captured = capsys.readouterr().out
    assert "Exception raised" in captured
    assert result is None


def test_parentheses():
    @log
    def greet(name):
        return f"Hello, {name}!"

    greet("Ioannis")

    @log()
    def greet(name):
        return f"Hello, {name}!"

    greet("Ioannis")
