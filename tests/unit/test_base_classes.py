"""Unit tests for abstract base classes"""

import pytest
from abc import ABC


def test_base_logger_is_abstract():
    """Test that BaseLogger is abstract and cannot be instantiated."""
    from app.services.logging.base import BaseLogger

    # Should raise TypeError when trying to instantiate directly
    with pytest.raises(TypeError):
        BaseLogger()


def test_base_logger_requires_all_methods():
    """Test that BaseLogger subclass must implement all abstract methods."""
    from app.services.logging.base import BaseLogger

    # Incomplete implementation should fail
    class IncompleteLogger(BaseLogger):
        def info(self, message: str, **kwargs):
            pass

    with pytest.raises(TypeError):
        IncompleteLogger()


def test_base_logger_complete_implementation():
    """Test that complete implementation of BaseLogger works."""
    from app.services.logging.base import BaseLogger

    class CompleteLogger(BaseLogger):
        def info(self, message: str, **kwargs):
            pass

        def error(self, message: str, **kwargs):
            pass

        def warning(self, message: str, **kwargs):
            pass

        def debug(self, message: str, **kwargs):
            pass

        def exception(self, message: str, **kwargs):
            pass

    # Should work
    logger = CompleteLogger()
    assert logger is not None


def test_base_tracer_is_abstract():
    """Test that BaseTracer is abstract and cannot be instantiated."""
    from app.services.tracing.base import BaseTracer

    with pytest.raises(TypeError):
        BaseTracer()


def test_base_tracer_requires_all_methods():
    """Test that BaseTracer subclass must implement all abstract methods."""
    from app.services.tracing.base import BaseTracer

    class IncompleteTracer(BaseTracer):
        def capture_lambda_handler(self, handler):
            pass

    with pytest.raises(TypeError):
        IncompleteTracer()


def test_base_tracer_complete_implementation():
    """Test that complete implementation of BaseTracer works."""
    from app.services.tracing.base import BaseTracer
    from contextlib import contextmanager

    class CompleteTracer(BaseTracer):
        def capture_lambda_handler(self, handler):
            return handler

        def capture_method(self, method):
            return method

        @contextmanager
        def create_segment(self, name: str, metadata=None):
            yield

    tracer = CompleteTracer()
    assert tracer is not None
