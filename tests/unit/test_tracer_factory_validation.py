"""Unit tests for TracerFactory validation, service name validation, and caching"""

import pytest
import sys
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def mock_aws_xray(monkeypatch):
    """Mock AWS XRay SDK to prevent socket creation during imports."""
    # Create a mock xray recorder
    mock_xray_recorder = MagicMock()

    # Create mock modules
    mock_xray = MagicMock()
    mock_xray.core.xray_recorder = mock_xray_recorder

    # Install mocks before any imports
    sys.modules["aws_xray_sdk"] = mock_xray
    sys.modules["aws_xray_sdk.core"] = mock_xray.core

    # Allow socket operations for these tests
    monkeypatch.delattr("socket.socket", raising=False)

    yield

    # Cleanup - remove the cloud tracer from cache if it was imported
    if "app.services.tracing.cloud" in sys.modules:
        del sys.modules["app.services.tracing.cloud"]
    if "app.services.tracing.factory" in sys.modules:
        del sys.modules["app.services.tracing.factory"]


def test_tracer_factory_cloud_tracer_types(monkeypatch, mock_aws_xray):
    """Test TracerFactory with various cloud tracer type aliases."""
    from app.services.tracing.factory import TracerFactory

    # Test 'cloud'
    tracer = TracerFactory.create_tracer("test", tracer_type="cloud")
    assert tracer.__class__.__name__ == "CloudTracer"

    # Test 'aws'
    tracer = TracerFactory.create_tracer("test", tracer_type="aws")
    assert tracer.__class__.__name__ == "CloudTracer"

    # Test 'xray'
    tracer = TracerFactory.create_tracer("test", tracer_type="xray")
    assert tracer.__class__.__name__ == "CloudTracer"


def test_tracer_factory_unknown_type_raises_error():
    """Test TracerFactory raises ValueError for unknown tracer type."""
    from app.services.tracing.factory import TracerFactory

    with pytest.raises(ValueError) as exc_info:
        TracerFactory.create_tracer("test", tracer_type="unknown_type")

    assert "Unknown tracer_type" in str(exc_info.value)


def test_validate_service_name_empty_raises_error():
    """Test validate_service_name raises ValueError for empty names."""
    from app.services.tracing.factory import validate_service_name

    with pytest.raises(ValueError) as exc_info:
        validate_service_name("")

    assert "Invalid service name" in str(exc_info.value)


def test_validate_service_name_whitespace_only():
    """Test validate_service_name with whitespace-only string."""
    from app.services.tracing.factory import validate_service_name

    with pytest.raises(ValueError):
        validate_service_name("   ")


def test_validate_service_name_none():
    """Test validate_service_name with None."""
    from app.services.tracing.factory import validate_service_name

    with pytest.raises(ValueError):
        validate_service_name(None)


def test_validate_service_name_strips_whitespace():
    """Test validate_service_name strips whitespace."""
    from app.services.tracing.factory import validate_service_name

    result = validate_service_name("  test-service  ")
    assert result == "test-service"


def test_tracer_factory_env_override(monkeypatch):
    """Test TracerFactory uses TRACER_TYPE from environment."""
    # Clear the module cache to ensure fresh import
    if "app.services.tracing.factory" in sys.modules:
        del sys.modules["app.services.tracing.factory"]
    if "app.services.tracing.local" in sys.modules:
        del sys.modules["app.services.tracing.local"]

    monkeypatch.setattr(
        "app.helpers.environment.env",
        lambda k, d=None: {
            "TRACER_TYPE": "local",
            "APP_NAME": "test",
            "APP_ENVIRONMENT": "local",
        }.get(k, d),
    )

    from app.services.tracing.factory import TracerFactory

    # Should use env override
    tracer = TracerFactory.create_tracer()
    assert tracer.__class__.__name__ == "LocalTracer"


def test_get_tracer_cached():
    """Test that get_tracer caches results."""
    from app.services.tracing.factory import get_tracer

    tracer1 = get_tracer("test-service")
    tracer2 = get_tracer("test-service")

    # Should be cached (same instance)
    assert tracer1 is tracer2
