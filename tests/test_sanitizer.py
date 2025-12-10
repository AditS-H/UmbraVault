import pytest
from src.sanitizer import InputSanitizer


def test_sanitize_valid_ip():
    assert InputSanitizer.sanitize_task({"target": "127.0.0.1"}) == {"target": "127.0.0.1"}


def test_sanitize_invalid_injection():
    with pytest.raises(ValueError):
        InputSanitizer.sanitize_task({"target": "127.0.0.1; rm -rf /"})
