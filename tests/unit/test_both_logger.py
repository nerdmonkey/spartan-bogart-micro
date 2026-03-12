"""Unit tests for app/services/logging/both.py"""

import pytest
from unittest.mock import MagicMock, patch


def test_both_logger_initialization():
    """Test BothLogger initialization."""
    from app.services.logging.both import BothLogger

    logger = BothLogger(service_name="test-service", level="INFO", sample_rate=0.5)

    assert logger.service_name == "test-service"
    assert logger.level == "INFO"
    assert logger.file_logger is not None
    assert logger.stream_logger is not None


def test_both_logger_log_method():
    """Test BothLogger.log() delegates to both loggers."""
    from app.services.logging.both import BothLogger

    logger = BothLogger(service_name="test", level="DEBUG")

    # Mock the underlying loggers
    logger.file_logger.log = MagicMock()
    logger.stream_logger.log = MagicMock()

    logger.log("test message", level="INFO")

    logger.file_logger.log.assert_called_once_with("test message", "INFO")
    logger.stream_logger.log.assert_called_once_with("test message", "INFO")


def test_both_logger_info_with_extra():
    """Test BothLogger.info() with extra data."""
    from app.services.logging.both import BothLogger

    logger = BothLogger(service_name="test")

    # Mock the underlying loggers
    logger.file_logger.info = MagicMock()
    logger.stream_logger.info = MagicMock()

    extra_data = {"key": "value", "password": "secret"}
    logger.info("test message", extra=extra_data)

    # file_logger should get the full call
    logger.file_logger.info.assert_called_once()
    # stream_logger should get prettified message
    logger.stream_logger.info.assert_called_once()


def test_both_logger_warning_with_extra():
    """Test BothLogger.warning() with extra data."""
    from app.services.logging.both import BothLogger

    logger = BothLogger(service_name="test")

    logger.file_logger.warning = MagicMock()
    logger.stream_logger.warning = MagicMock()

    logger.warning("warning message", extra={"token": "secret123"})

    logger.file_logger.warning.assert_called_once()
    logger.stream_logger.warning.assert_called_once()


def test_both_logger_error_with_extra():
    """Test BothLogger.error() with extra data."""
    from app.services.logging.both import BothLogger

    logger = BothLogger(service_name="test")

    logger.file_logger.error = MagicMock()
    logger.stream_logger.error = MagicMock()

    logger.error("error message", extra={"api_key": "sk-123"})

    logger.file_logger.error.assert_called_once()
    logger.stream_logger.error.assert_called_once()


def test_both_logger_debug_with_extra():
    """Test BothLogger.debug() with extra data."""
    from app.services.logging.both import BothLogger

    logger = BothLogger(service_name="test")

    logger.file_logger.debug = MagicMock()
    logger.stream_logger.debug = MagicMock()

    logger.debug("debug message", extra={"credentials": "secret"})

    logger.file_logger.debug.assert_called_once()
    logger.stream_logger.debug.assert_called_once()


def test_both_logger_exception():
    """Test BothLogger.exception() method."""
    from app.services.logging.both import BothLogger

    logger = BothLogger(service_name="test")

    logger.file_logger.exception = MagicMock()
    logger.stream_logger.exception = MagicMock()

    try:
        raise ValueError("test error")
    except ValueError:
        logger.exception("An error occurred", extra={"error_code": 500})

    logger.file_logger.exception.assert_called_once()
    logger.stream_logger.exception.assert_called_once()


def test_prettify_extra_with_sensitive_fields():
    """Test _prettify_extra sanitizes sensitive fields."""
    from app.services.logging.both import _prettify_extra

    extra = {
        "password": "secret123",
        "token": "abc123",
        "api_key": "sk-xxx",
        "normal": "visible",
    }

    result = _prettify_extra(extra)

    assert "[REDACTED]" in result
    assert "visible" in result
    assert "secret123" not in result


def test_prettify_extra_with_no_extra():
    """Test _prettify_extra with None."""
    from app.services.logging.both import _prettify_extra

    result = _prettify_extra(None)

    assert result == ""


def test_prettify_extra_with_empty_dict():
    """Test _prettify_extra with empty dict."""
    from app.services.logging.both import _prettify_extra

    result = _prettify_extra({})

    assert result == ""


def test_prettify_extra_json_serialization_error():
    """Test _prettify_extra handles JSON serialization errors."""
    from app.services.logging.both import _prettify_extra

    class NonSerializable:
        pass

    extra = {"obj": NonSerializable()}

    result = _prettify_extra(extra)

    # Should fall back to str() representation
    assert "extra:" in result


def test_both_logger_stacklevel_parameter():
    """Test that stacklevel parameter is properly handled."""
    from app.services.logging.both import BothLogger

    logger = BothLogger(service_name="test")

    logger.file_logger.info = MagicMock()
    logger.stream_logger.info = MagicMock()

    # Test with custom stacklevel
    logger.info("test", extra={}, stacklevel=3)

    # file_logger should receive stacklevel=3
    call_kwargs = logger.file_logger.info.call_args[1]
    assert call_kwargs.get("stacklevel") == 3


def test_both_logger_default_stacklevel():
    """Test that default stacklevel is 6."""
    from app.services.logging.both import BothLogger

    logger = BothLogger(service_name="test")

    logger.file_logger.info = MagicMock()
    logger.stream_logger.info = MagicMock()

    # Test without custom stacklevel
    logger.info("test", extra={})

    # file_logger should receive default stacklevel=6
    call_kwargs = logger.file_logger.info.call_args[1]
    assert call_kwargs.get("stacklevel") == 6
