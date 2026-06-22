import json
import re
import os
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlencode

from src.models.profile import InstagramProfile
from src.config import Config


INTEREST_KEYWORDS: dict[str, list[str]] = {
    "travel": ["travel", "wanderlust", "explore", "adventure", "trip", "journey", "vacation", "world", "путешествия", "путешествие"],
    "food": ["food", "foodie", "cooking", "recipe", "eat", "cuisine", "chef", "baking", "coffee", "еда", "кофе"],
    "fitness": ["fitness", "gym", "workout", "health", "yoga", "running", "sport", "training", "спорт", "фитнес"],
    "photography": ["photography", "photo", "camera", "portrait", "landscape", "shots", "photographer", "фото"],
    "music": ["music", "concert", "band", "playlist", "guitar", "dj", "singer", "song", "музыка"],
    "art": ["art", "design", "illustration", "drawing", "painting", "creative", "artist", "sketch", "искусство"],
    "tech": ["tech", "coding", "developer", "software", "startup", "ai", "data", "engineering"],
    "fashion": ["fashion", "style", "outfit", "clothes", "ootd", "designer", "streetwear", "мода", "стиль"],
    "nature": ["nature", "hiking", "outdoors", "mountains", "forest", "beach", "wildlife", "природа", "горы"],
    "mystery": ["mystery", "thriller", "crime", "detective", "dark", "horror", "suspense", "детектив", "триллер"],
    "science": ["science", "space", "astronomy", "physics", "biology", "research", "наука"],
    "history": ["history", "culture", "heritage", "museum", "ancient", "historical", "история"],
    "comedy": ["comedy", "funny", "humor", "meme", "laugh", "jokes", "fun", "юмор"],
    "drama": ["drama", "emotional", "heartfelt", "story", "narrative", "драма"],
    "fantasy": ["fantasy", "magic", "supernatural", "mythical", "dragon", "wizard", "фэнтези"],
    "anime": ["anime", "manga", "otaku", "cosplay", "japanese", "аниме"],
    "romance": ["romance", "love", "romantic", "любовь", "романтика"],
}


def extract_interests(text: str) -> list[str]:
    text_lower = text.lower()
    found: list[str] = []
    for category, keywords in INTEREST_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(category)
    return found


def extract_hashtags(text: str) -> list[str]:
    return re.findall(r"#(\w+)", text)


class InstagramService:
    def __init__(self, config: Config):
        self.config = config

    def fetch_profile(self, username: str) -> Optional[InstagramProfile]:
        if not self.config.rapidapi_key:
            return None
        try:
            params = urlencode({"username": username})
            url = f"https://instagram-scraper-api2.p.rapidapi.com/v1/info?{params}"
            req = Request(url, headers={
                "x-rapidapi-key": self.config.rapidapi_key,
                "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com",
            })
            with urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            return self._parse_profile(username, data)
        except (URLError, KeyError, json.JSONDecodeError):
            return None

    def _parse_profile(self, username: str, data: dict) -> InstagramProfile:
        user = data.get("data", data)
        bio = user.get("biography", "")
        captions: list[str] = []
        hashtags: list[str] = extract_hashtags(bio)

        posts = user.get("edge_owner_to_timeline_media", {}).get("edges", [])
        for edge in posts[:20]:
            caption = (
                edge.get("node", {})
                .get("edge_media_to_caption", {})
                .get("edges", [{}])[0]
                .get("node", {})
                .get("text", "")
            )
            if caption:
                captions.append(caption)
                hashtags.extend(extract_hashtags(caption))

        combined = bio + " " + " ".join(captions) + " " + " ".join(hashtags)
        interests = extract_interests(combined)

        return InstagramProfile(
            username=username,
            bio=bio,
            captions=captions,
            hashtags=list(set(hashtags)),
            interests=interests,
            follower_count=user.get("edge_followed_by", {}).get("count", 0),
            following_count=user.get("edge_follow", {}).get("count", 0),
        )

    def load_from_json(self, path: str) -> Optional[InstagramProfile]:
        try:
            with open(path) as f:
                data = json.load(f)
            username = data.get("username", os.path.basename(path))
            bio = data.get("bio", data.get("biography", ""))
            captions = data.get("captions", [])
            hashtags = data.get("hashtags", []) + extract_hashtags(bio)
            for cap in captions:
                hashtags.extend(extract_hashtags(cap))
            combined = bio + " " + " ".join(captions) + " " + " ".join(hashtags)
            interests = extract_interests(combined)
            return InstagramProfile(
                username=username,
                bio=bio,
                captions=captions,
                hashtags=list(set(hashtags)),
                interests=interests,
            )
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def build_mock_profile(self, username: str) -> InstagramProfile:
        interests = extract_interests(username)
        return InstagramProfile(
            username=username,
            bio="",
            interests=interests if interests else ["drama", "travel"],
        )
