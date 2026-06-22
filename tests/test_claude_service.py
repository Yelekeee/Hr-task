import pytest
from unittest.mock import MagicMock, patch

from src.services.claude_service import ClaudeService
from src.config import Config


def test_claude_service_unavailable_without_key():
    service = ClaudeService(Config())
    assert service.available is False


def test_extract_interests_returns_empty_when_unavailable():
    service = ClaudeService(Config())
    result = service.extract_interests("user", "bio", [], [])
    assert result == {}


def test_recommend_series_returns_empty_when_unavailable():
    service = ClaudeService(Config())
    result = service.recommend_series(["travel"], ["curious"], "adventurous", "traveler")
    assert result == []


def test_claude_service_available_with_key():
    config = Config(anthropic_api_key="test-key")
    with patch("src.services.claude_service._ANTHROPIC_AVAILABLE", True):
        with patch("src.services.claude_service.anthropic") as mock_anthropic:
            mock_anthropic.Anthropic.return_value = MagicMock()
            service = ClaudeService(config)
            assert service.available is True


def test_call_strips_markdown_fences():
    config = Config(anthropic_api_key="test-key")
    service = ClaudeService(config)
    service._client = MagicMock()

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text='```json\n{"key": "value"}\n```')]
    service._client.messages.create.return_value = mock_message

    result = service._call("test prompt")
    assert result == {"key": "value"}


def test_call_handles_plain_json():
    config = Config(anthropic_api_key="test-key")
    service = ClaudeService(config)
    service._client = MagicMock()

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text='["item1", "item2"]')]
    service._client.messages.create.return_value = mock_message

    result = service._call("test prompt")
    assert result == ["item1", "item2"]


def test_call_returns_none_on_error():
    config = Config(anthropic_api_key="test-key")
    service = ClaudeService(config)
    service._client = MagicMock()
    service._client.messages.create.side_effect = Exception("API error")

    result = service._call("test prompt")
    assert result is None
