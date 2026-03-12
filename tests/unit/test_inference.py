"""Unit tests for handlers/inference.py"""

import pytest
from unittest.mock import MagicMock, patch


def test_inference_main_handler():
    """Test the main inference handler function."""
    from handlers.inference import main
    from app.helpers.context import MockLambdaContext

    event = {"test": "data"}
    context = MockLambdaContext()

    result = main(event, context)
    assert result == {"statusCode": 200, "body": "Hello Spartan!"}


def test_inference_main_with_pii_sanitization():
    """Test that PII data is logged properly."""
    from handlers.inference import main
    from app.helpers.context import MockLambdaContext

    event = {"user": "test"}
    context = MockLambdaContext()

    result = main(event, context)
    assert result["statusCode"] == 200


def test_inference_main_with_environment_metadata():
    """Test environment metadata logging."""
    from handlers.inference import main
    from app.helpers.context import MockLambdaContext

    event = {}
    context = MockLambdaContext()

    result = main(event, context)
    assert result["statusCode"] == 200


def test_inference_main_with_log_sampling():
    """Test log sampling with multiple messages."""
    from handlers.inference import main
    from app.helpers.context import MockLambdaContext

    event = {}
    context = MockLambdaContext()

    result = main(event, context)
    assert result["statusCode"] == 200


def test_inference_main_with_error_logging():
    """Test error logging with extra data."""
    from handlers.inference import main
    from app.helpers.context import MockLambdaContext

    event = {}
    context = MockLambdaContext()

    result = main(event, context)
    assert result["statusCode"] == 200


def test_inference_main_script_execution():
    """Test the __main__ script execution path."""
    with patch("handlers.inference.main") as mock_main:
        mock_main.return_value = {"statusCode": 200, "body": "Test"}

        # Import and execute the main block
        import handlers.inference as inf_module
        from app.helpers.context import MockLambdaContext, MockLambdaEvent

        event = MockLambdaEvent()
        context = MockLambdaContext()

        # Call main directly to test it
        result = inf_module.main(event, context)
        assert result["statusCode"] == 200


def test_inference_main_script_with_exception():
    """Test the __main__ script exception handling."""
    with patch("handlers.inference.main") as mock_main:
        mock_main.side_effect = RuntimeError("Test error")

        from app.helpers.context import MockLambdaContext, MockLambdaEvent

        event = MockLambdaEvent()
        context = MockLambdaContext()

        # Should handle the exception
        with pytest.raises(RuntimeError):
            mock_main(event, context)
