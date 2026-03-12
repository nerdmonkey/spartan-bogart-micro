"""Unit tests for app/helpers/tracer.py"""


def test_tracer_helper_imports():
    """Test that tracer helper imports work correctly."""
    from app.helpers.tracer import (
        TracerService,
        capture_lambda_handler,
        capture_method,
        get_tracer,
        trace_function,
        trace_segment,
    )

    # Verify all imports are accessible
    assert TracerService is not None
    assert capture_lambda_handler is not None
    assert capture_method is not None
    assert get_tracer is not None
    assert trace_function is not None
    assert trace_segment is not None


def test_tracer_helper_get_tracer():
    """Test getting a tracer instance."""
    from app.helpers.tracer import get_tracer

    # get_tracer() takes no arguments, it returns a singleton instance
    tracer = get_tracer()
    """Test __all__ exports from tracer helper."""
    from app.helpers import tracer

    assert hasattr(tracer, "__all__")
