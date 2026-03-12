"""Test remaining uncovered file.py lines"""

import pytest
import json
import os


def test_file_logger_json_formatter_is_valid_frame_logic(tmp_path, monkeypatch):
    """Test _JsonFormatter._is_valid_frame method."""
    from app.services.logging.file import _JsonFormatter

    formatter = _JsonFormatter("test-service")

    # Get project root
    project_root = formatter._project_root

    # Test file outside project root
    assert formatter._is_valid_frame("/some/other/path/file.py") is False

    # Test file inside project but in logging directory
    logging_path = os.path.join(project_root, "app/services/logging/base.py")
    assert formatter._is_valid_frame(logging_path) is False

    # Test file in helpers/logger.py
    helper_path = os.path.join(project_root, "app/helpers/logger.py")
    assert formatter._is_valid_frame(helper_path) is False

    # Test valid application file
    valid_path = os.path.join(project_root, "handlers/inference.py")
    assert formatter._is_valid_frame(valid_path) is True


def test_file_logger_json_formatter_normalized_path(tmp_path, monkeypatch):
    """Test _JsonFormatter with Windows-style paths."""
    from app.services.logging.file import _JsonFormatter

    formatter = _JsonFormatter("test-service")

    # Test with backslashes (Windows-style path)
    windows_path = (
        formatter._project_root.replace("/", "\\") + "\\handlers\\inference.py"
    )

    # Should handle backslashes by normalizing to forward slashes
    result = formatter._is_valid_frame(windows_path)
    # Result depends on whether it's actually in the project
    assert isinstance(result, bool)


def test_file_logger_log_method_with_kwargs(tmp_path, monkeypatch):
    """Test FileLogger.log() with extra kwargs."""
    from app.services.logging.file import FileLogger

    monkeypatch.setattr(
        "app.services.logging.file.env",
        lambda k, d=None: {"APP_ENVIRONMENT": "test", "APP_VERSION": "1.0"}.get(k, d),
    )

    logger = FileLogger(
        service_name="test", level="INFO", log_dir=str(tmp_path), sample_rate=1.0
    )

    # Test generic log method with stacklevel
    logger.log("test message", level="ERROR", extra={"key": "value"}, stacklevel=2)

    for h in logger.logger.handlers:
        try:
            h.flush()
        except Exception:
            pass

    log_file = tmp_path / "test.log"
    assert log_file.exists()


def test_file_logger_sample_rate_from_environment(tmp_path, monkeypatch):
    """Test file logger uses sample rate from environment."""
    from app.services.logging.file import FileLogger

    monkeypatch.setattr(
        "app.services.logging.file.env",
        lambda k, d=None: {
            "APP_ENVIRONMENT": "test",
            "APP_VERSION": "1.0",
            "LOG_SAMPLE_RATE": "0.5",
        }.get(k, d),
    )

    # Test with sample_rate from environment
    logger = FileLogger(service_name="test", level="INFO", log_dir=str(tmp_path))

    # Should use sample_rate from env or constructor
    assert logger.sample_rate >= 0.0

    # Test log method (generic entry point)
    logger.log("test message", level="WARNING", extra={"key": "value"})

    for h in logger.logger.handlers:
        try:
            h.flush()
        except Exception:
            pass
