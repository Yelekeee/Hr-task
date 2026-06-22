import pytest
from unittest.mock import MagicMock

from src.models.profile import InstagramProfile, StreamingAvailability, SeriesRecommendation
from src.services.recommendation_service import RecommendationService, _score_series
from src.services.streaming_service import StreamingService
from src.services.claude_service import ClaudeService
from src.config import Config


def make_services():
    streaming = StreamingService(Config())
    claude = ClaudeService(Config())  # no API key → unavailable
    return streaming, claude


def test_score_series_perfect_match():
    series = {"title": "Dark", "genres": ["mystery"], "tags": ["mystery", "science"]}
    score = _score_series(series, ["mystery", "science"])
    assert score > 70


def test_score_series_no_match():
    series = {"title": "Dark", "genres": ["mystery"], "tags": ["mystery", "science"]}
    score = _score_series(series, ["comedy", "food"])
    assert score < 70


def test_score_series_partial_match():
    series = {"title": "Dark", "genres": ["mystery"], "tags": ["mystery", "science", "travel"]}
    score_partial = _score_series(series, ["mystery"])
    score_full = _score_series(series, ["mystery", "science", "travel"])
    assert score_full >= score_partial


def test_score_series_empty_interests():
    series = {"title": "Dark", "genres": ["mystery"], "tags": ["mystery"]}
    score = _score_series(series, [])
    assert score == 50


def test_recommend_returns_list():
    profile = InstagramProfile(username="testuser", interests=["mystery", "travel"])
    service = RecommendationService(*make_services())
    recs = service.recommend(profile, top_n=5)
    assert len(recs) <= 5
    assert all(isinstance(r, SeriesRecommendation) for r in recs)


def test_recommend_sorted_by_priority():
    profile = InstagramProfile(username="testuser", interests=["drama", "mystery"])
    service = RecommendationService(*make_services())
    recs = service.recommend(profile, top_n=5)
    scores = [r.priority_score() for r in recs]
    assert scores == sorted(scores, reverse=True)


def test_priority_score_netflix_bonus():
    avail_netflix = StreamingAvailability(netflix=True)
    avail_none = StreamingAvailability()
    rec_netflix = SeriesRecommendation(title="A", match_score=80, reason="test", genres=[], streaming=avail_netflix)
    rec_none = SeriesRecommendation(title="B", match_score=80, reason="test", genres=[], streaming=avail_none)
    assert rec_netflix.priority_score() > rec_none.priority_score()


def test_priority_score_hbo_bonus():
    avail_hbo = StreamingAvailability(hbo_max=True)
    avail_none = StreamingAvailability()
    rec_hbo = SeriesRecommendation(title="A", match_score=75, reason="test", genres=[], streaming=avail_hbo)
    rec_none = SeriesRecommendation(title="B", match_score=75, reason="test", genres=[], streaming=avail_none)
    assert rec_hbo.priority_score() > rec_none.priority_score()


def test_recommend_with_claude_data():
    profile = InstagramProfile(
        username="testuser",
        interests=["travel", "romance"],
        claude_data={
            "interests": ["travel", "romance"],
            "personality_traits": ["adventurous"],
            "content_mood": "romantic",
            "summary": "A romantic traveler",
        },
    )
    streaming, _ = make_services()
    mock_claude = MagicMock()
    mock_claude.available = True
    mock_claude.recommend_series.return_value = [
        {"title": "Dark", "match_score": 88, "reason": "loves mystery", "genres": ["mystery"]},
        {"title": "Stranger Things", "match_score": 82, "reason": "sci-fi fan", "genres": ["sci-fi"]},
    ]
    service = RecommendationService(streaming, mock_claude)
    recs = service.recommend(profile, top_n=5)
    assert len(recs) == 2
    assert recs[0].title in ["Dark", "Stranger Things"]


def test_recommend_fallback_when_claude_returns_empty():
    profile = InstagramProfile(username="testuser", interests=["drama"], claude_data={"interests": ["drama"]})
    streaming, _ = make_services()
    mock_claude = MagicMock()
    mock_claude.available = True
    mock_claude.recommend_series.return_value = []
    service = RecommendationService(streaming, mock_claude)
    recs = service.recommend(profile, top_n=3)
    assert len(recs) == 3
