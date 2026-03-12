"""Unit tests for app/services/logger.py"""

import pytest


def test_get_logger_with_service_name():
    """Test get_logger with explicit service name."""
    from app.services.logger import get_logger

    logger = get_logger("test-service")
    assert logger is not None


def test_get_logger_without_service_name():
    """Test get_logger without service name falls back to default."""
    from app.services.logger import get_logger

    # Should use default "spartan-framework"
    logger = get_logger()
    assert logger is not None


def test_get_logger_none_service_name():
    """Test get_logger with None explicitly."""
    from app.services.logger import get_logger

    logger = get_logger(None)
    assert logger is not None


def test_logger_service_get_logger():
    """Test LoggerService.get_logger directly."""
    from app.services.logger import LoggerService

    logger1 = LoggerService.get_logger("test")
    logger2 = LoggerService.get_logger("test")

    # Should be cached (same instance)
    assert logger1 is logger2


def test_logger_service_caching():
    """Test that logger service caches instances."""
    from app.services.logger import LoggerService

    # Get same logger twice
    logger1 = LoggerService.get_logger("cache-test")
    logger2 = LoggerService.get_logger("cache-test")

    # Should be the same cached instance due to lru_cache
    assert logger1 is logger2

    # Different service name should return different instance
    logger3 = LoggerService.get_logger("other-service")
    assert logger1 is not logger3
