"""Tests for cloud services with proper AWS SDK mocking"""

import pytest
from unittest.mock import MagicMock, Mock, patch
import sys


@pytest.fixture(autouse=True)
def mock_aws_imports(monkeypatch):
    """Mock AWS SDK imports before they're loaded."""
    # Mock aws_lambda_powertools
    mock_logger_class = MagicMock()
    mock_logger_instance = MagicMock()
    mock_logger_instance._logger = MagicMock()
    mock_logger_instance._logger.handlers = []
    mock_logger_class.return_value = mock_logger_instance

    mock_powertools = MagicMock()
    mock_powertools.Logger = mock_logger_class
    mock_powertools.logging.correlation_paths.API_GATEWAY_REST = "api_gateway"

    sys.modules["aws_lambda_powertools"] = mock_powertools
    sys.modules["aws_lambda_powertools.logging"] = mock_powertools.logging
    sys.modules["aws_lambda_powertools.logging.correlation_paths"] = (
        mock_powertools.logging.correlation_paths
    )

    # Mock aws_xray_sdk
    mock_xray_recorder = MagicMock()
    mock_xray = MagicMock()
    mock_xray.core.xray_recorder = mock_xray_recorder

    sys.modules["aws_xray_sdk"] = mock_xray
    sys.modules["aws_xray_sdk.core"] = mock_xray.core

    yield

    # Cleanup
    if "app.services.logging.cloud" in sys.modules:
        del sys.modules["app.services.logging.cloud"]
    if "app.services.tracing.cloud" in sys.modules:
        del sys.modules["app.services.tracing.cloud"]


def test_cloudwatch_logger_initialization(mock_aws_imports, monkeypatch):
    """Test CloudWatchLogger can be initialized."""
    # Prevent socket creation
    monkeypatch.delattr("socket.socket", raising=False)

    from app.services.logging.cloud import CloudWatchLogger

    logger = CloudWatchLogger(service_name="test", level="INFO", sample_rate=1.0)
    assert logger is not None
    assert logger.sample_rate == 1.0


def test_cloudwatch_logger_methods(mock_aws_imports, monkeypatch):
    """Test CloudWatchLogger logging methods."""
    monkeypatch.delattr("socket.socket", raising=False)

    from app.services.logging.cloud import CloudWatchLogger

    logger = CloudWatchLogger(service_name="test", level="DEBUG", sample_rate=1.0)

    # Test all logging methods
    logger.info("info message", extra={"key": "value"})
    logger.error("error message", extra={"code": 500})
    logger.warning("warning message")
    logger.debug("debug message")
    logger.critical("critical message")

    try:
        raise ValueError("test")
    except:
        logger.exception("exception message")


def test_cloudwatch_logger_sampling(mock_aws_imports, monkeypatch):
    """Test CloudWatchLogger sampling logic."""
    monkeypatch.delattr("socket.socket", raising=False)

    from app.services.logging.cloud import CloudWatchLogger

    # 0% sampling
    logger = CloudWatchLogger(service_name="test", sample_rate=0.0)

    # Mock random to return value > 0
    with patch("random.random", return_value=0.5):
        logger.info("should not log")
        logger.error("should not log")


def test_cloudwatch_logger_get_caller_location(mock_aws_imports, monkeypatch):
    """Test CloudWatchLogger._get_caller_location."""
    monkeypatch.delattr("socket.socket", raising=False)

    from app.services.logging.cloud import CloudWatchLogger

    logger = CloudWatchLogger(service_name="test", level="INFO")
    location = logger._get_caller_location()

    assert ":" in location


def test_cloudwatch_logger_inject_lambda_context(mock_aws_imports, monkeypatch):
    """Test CloudWatchLogger.inject_lambda_context."""
    monkeypatch.delattr("socket.socket", raising=False)

    from app.services.logging.cloud import CloudWatchLogger
    from app.helpers.context import MockLambdaContext

    logger = CloudWatchLogger(service_name="test")

    @logger.inject_lambda_context()
    def handler(event, context):
        return {"statusCode": 200}

    # Use proper mock context object
    result = handler({}, MockLambdaContext())
    monkeypatch.delattr("socket.socket", raising=False)

    from app.services.tracing.cloud import CloudTracer

    tracer = CloudTracer(service_name="test")
    assert tracer is not None
    assert tracer.service_name == "test"


def test_cloud_tracer_capture_lambda_handler(mock_aws_imports, monkeypatch):
    """Test CloudTracer.capture_lambda_handler."""
    monkeypatch.delattr("socket.socket", raising=False)

    from app.services.tracing.cloud import CloudTracer

    tracer = CloudTracer(service_name="test")

    @tracer.capture_lambda_handler
    def handler(event, context):
        return {"statusCode": 200}

    result = handler({}, {})
    assert result == {"statusCode": 200}


def test_cloud_tracer_capture_method(mock_aws_imports, monkeypatch):
    """Test CloudTracer.capture_method."""
    monkeypatch.delattr("socket.socket", raising=False)

    from app.services.tracing.cloud import CloudTracer

    tracer = CloudTracer(service_name="test")

    class TestClass:
        @tracer.capture_method
        def method(self, x):
            return x * 2

    obj = TestClass()
    result = obj.method(5)
    assert result == 10


def test_cloud_tracer_create_segment(mock_aws_imports, monkeypatch):
    """Test CloudTracer.create_segment."""
    monkeypatch.delattr("socket.socket", raising=False)

    from app.services.tracing.cloud import CloudTracer

    tracer = CloudTracer(service_name="test")

    with tracer.create_segment("test_segment"):
        result = 42

    assert result == 42


def test_cloud_tracer_create_subsegment(mock_aws_imports, monkeypatch):
    """Test CloudTracer.create_subsegment."""
    monkeypatch.delattr("socket.socket", raising=False)

    from app.services.tracing.cloud import CloudTracer

    tracer = CloudTracer(service_name="test")

    with tracer.create_subsegment("test_subsegment"):
        result = 24

    assert result == 24
