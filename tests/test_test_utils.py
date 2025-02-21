from .test_utils import simple_celsius_to_fahrenheit


def test_simple_celsius_to_fahrenheit():
    assert simple_celsius_to_fahrenheit(0) == 32
    assert simple_celsius_to_fahrenheit(22.5) == 72.5
    assert simple_celsius_to_fahrenheit(19.7) == 67.46
