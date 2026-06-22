import json
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlencode

from src.models.profile import StreamingAvailability
from src.config import Config

# Static catalog for fallback when API is unavailable.
# Format: title_lower -> {"netflix": bool, "hbo_max": bool, "prime_video": bool}
STATIC_CATALOG: dict[str, dict[str, bool]] = {
    "dark": {"netflix": True, "hbo_max": False, "prime_video": False},
    "the last of us": {"netflix": False, "hbo_max": True, "prime_video": False},
    "succession": {"netflix": False, "hbo_max": True, "prime_video": False},
    "stranger things": {"netflix": True, "hbo_max": False, "prime_video": False},
    "the boys": {"netflix": False, "hbo_max": False, "prime_video": True},
    "game of thrones": {"netflix": False, "hbo_max": True, "prime_video": False},
    "house of cards": {"netflix": True, "hbo_max": False, "prime_video": False},
    "ozark": {"netflix": True, "hbo_max": False, "prime_video": False},
    "the wire": {"netflix": False, "hbo_max": True, "prime_video": False},
    "narcos": {"netflix": True, "hbo_max": False, "prime_video": False},
    "breaking bad": {"netflix": True, "hbo_max": False, "prime_video": False},
    "the sopranos": {"netflix": False, "hbo_max": True, "prime_video": False},
    "westworld": {"netflix": False, "hbo_max": True, "prime_video": False},
    "attack on titan": {"netflix": True, "hbo_max": False, "prime_video": True},
    "the mandalorian": {"netflix": False, "hbo_max": False, "prime_video": False},
    "the office": {"netflix": False, "hbo_max": False, "prime_video": True},
    "parks and recreation": {"netflix": False, "hbo_max": False, "prime_video": True},
    "mindhunter": {"netflix": True, "hbo_max": False, "prime_video": False},
    "wednesday": {"netflix": True, "hbo_max": False, "prime_video": False},
    "euphoria": {"netflix": False, "hbo_max": True, "prime_video": False},
    "the crown": {"netflix": True, "hbo_max": False, "prime_video": False},
    "peaky blinders": {"netflix": True, "hbo_max": False, "prime_video": False},
    "the witcher": {"netflix": True, "hbo_max": False, "prime_video": False},
    "squid game": {"netflix": True, "hbo_max": False, "prime_video": False},
    "money heist": {"netflix": True, "hbo_max": False, "prime_video": False},
    "white lotus": {"netflix": False, "hbo_max": True, "prime_video": False},
    "band of brothers": {"netflix": False, "hbo_max": True, "prime_video": False},
    "chernobyl": {"netflix": False, "hbo_max": True, "prime_video": False},
    "severance": {"netflix": False, "hbo_max": False, "prime_video": True},
    "reacher": {"netflix": False, "hbo_max": False, "prime_video": True},
}


class StreamingService:
    def __init__(self, config: Config):
        self.config = config

    def check(self, title: str) -> StreamingAvailability:
        if self.config.rapidapi_key:
            result = self._fetch_api(title)
            if result is not None:
                return result
        return self._static_lookup(title)

    def _fetch_api(self, title: str) -> "StreamingAvailability | None":
        try:
            params = urlencode({"title": title, "country": "us"})
            url = f"https://streaming-availability.p.rapidapi.com/search/title?{params}"
            req = Request(url, headers={
                "x-rapidapi-key": self.config.rapidapi_key,
                "x-rapidapi-host": "streaming-availability.p.rapidapi.com",
            })
            with urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read())
            return self._parse_availability(data)
        except (URLError, KeyError, json.JSONDecodeError):
            return None

    def _parse_availability(self, data: dict) -> StreamingAvailability:
        result_list = data.get("result", [])
        avail = StreamingAvailability()
        for item in result_list:
            streaming_info = item.get("streamingInfo", {}).get("us", {})
            if "netflix" in streaming_info:
                avail.netflix = True
            if "hbo" in streaming_info or "hboMax" in streaming_info:
                avail.hbo_max = True
            if "prime" in streaming_info or "amazonPrime" in streaming_info:
                avail.prime_video = True
        return avail

    def _static_lookup(self, title: str) -> StreamingAvailability:
        entry = STATIC_CATALOG.get(title.lower(), {})
        return StreamingAvailability(
            netflix=entry.get("netflix", False),
            hbo_max=entry.get("hbo_max", False),
            prime_video=entry.get("prime_video", False),
        )
