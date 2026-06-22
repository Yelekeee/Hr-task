import pytest

from src.services.streaming_service import StreamingService, STATIC_CATALOG
from src.models.profile import StreamingAvailability
from src.config import Config


def make_service() -> StreamingService:
    return StreamingService(Config())


def test_static_lookup_netflix():
    service = make_service()
    avail = service._static_lookup("Dark")
    assert avail.netflix is True
    assert avail.hbo_max is False


def test_static_lookup_hbo():
    service = make_service()
    avail = service._static_lookup("The Last of Us")
    assert avail.hbo_max is True
    assert avail.netflix is False


def test_static_lookup_prime():
    service = make_service()
    avail = service._static_lookup("The Boys")
    assert avail.prime_video is True


def test_static_lookup_case_insensitive():
    service = make_service()
    avail = service._static_lookup("dark")
    assert avail.netflix is True


def test_static_lookup_unknown():
    service = make_service()
    avail = service._static_lookup("Unknown Show XYZ")
    assert avail.netflix is False
    assert avail.hbo_max is False
    assert avail.prime_video is False


def test_available_platforms_netflix():
    avail = StreamingAvailability(netflix=True)
    platforms = avail.available_platforms()
    assert "Netflix" in platforms


def test_available_platforms_multiple():
    avail = StreamingAvailability(netflix=True, hbo_max=True)
    platforms = avail.available_platforms()
    assert "Netflix" in platforms
    assert "HBO Max" in platforms


def test_available_platforms_none():
    avail = StreamingAvailability()
    assert avail.available_platforms() == []


def test_check_uses_static_when_no_api_key():
    service = make_service()
    avail = service.check("Breaking Bad")
    assert avail.netflix is True
