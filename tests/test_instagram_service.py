import json
import tempfile
import os
import pytest

from src.services.instagram_service import extract_interests, extract_hashtags, InstagramService
from src.config import Config


def test_extract_hashtags_basic():
    text = "Love #travel and #food!"
    result = extract_hashtags(text)
    assert "travel" in result
    assert "food" in result


def test_extract_hashtags_empty():
    assert extract_hashtags("no hashtags here") == []


def test_extract_interests_travel():
    interests = extract_interests("I love to travel and explore the world")
    assert "travel" in interests


def test_extract_interests_multiple():
    interests = extract_interests("photography enthusiast, foodie, coding nerd")
    assert "photography" in interests
    assert "food" in interests
    assert "tech" in interests


def test_extract_interests_empty():
    result = extract_interests("")
    assert isinstance(result, list)


def test_extract_interests_case_insensitive():
    interests = extract_interests("TRAVEL PHOTOGRAPHY ART")
    assert "travel" in interests
    assert "photography" in interests
    assert "art" in interests


def test_load_from_json_valid():
    data = {
        "username": "testuser",
        "bio": "I love photography and travel",
        "captions": ["beautiful sunset #travel"],
        "hashtags": ["photography"],
    }
    config = Config()
    service = InstagramService(config)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        path = f.name
    try:
        profile = service.load_from_json(path)
        assert profile is not None
        assert profile.username == "testuser"
        assert "travel" in profile.interests or "photography" in profile.interests
    finally:
        os.unlink(path)


def test_load_from_json_missing_file():
    service = InstagramService(Config())
    result = service.load_from_json("/nonexistent/path.json")
    assert result is None


def test_build_mock_profile():
    service = InstagramService(Config())
    profile = service.build_mock_profile("travelphotographer")
    assert profile.username == "travelphotographer"
    assert isinstance(profile.interests, list)
