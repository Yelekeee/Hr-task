from typing import List

from src.models.profile import InstagramProfile, SeriesRecommendation, StreamingAvailability
from src.services.streaming_service import StreamingService

# Catalog: title -> {genres, interest_tags, base_score}
SERIES_CATALOG: list[dict] = [
    {"title": "Dark", "genres": ["mystery", "sci-fi", "thriller"], "tags": ["mystery", "science", "travel", "photography"]},
    {"title": "The Last of Us", "genres": ["drama", "action", "sci-fi"], "tags": ["drama", "fitness", "nature", "history"]},
    {"title": "Stranger Things", "genres": ["sci-fi", "mystery", "drama"], "tags": ["mystery", "science", "fantasy", "comedy"]},
    {"title": "Breaking Bad", "genres": ["crime", "drama", "thriller"], "tags": ["drama", "mystery", "tech", "science"]},
    {"title": "Succession", "genres": ["drama", "comedy"], "tags": ["drama", "fashion", "food", "tech"]},
    {"title": "The Wire", "genres": ["crime", "drama"], "tags": ["mystery", "history", "drama"]},
    {"title": "Chernobyl", "genres": ["drama", "history", "thriller"], "tags": ["history", "science", "drama", "mystery"]},
    {"title": "Westworld", "genres": ["sci-fi", "drama", "thriller"], "tags": ["tech", "science", "mystery", "fantasy"]},
    {"title": "Ozark", "genres": ["crime", "drama", "thriller"], "tags": ["mystery", "drama", "nature", "travel"]},
    {"title": "Mindhunter", "genres": ["crime", "drama", "thriller"], "tags": ["mystery", "science", "history"]},
    {"title": "The Sopranos", "genres": ["crime", "drama"], "tags": ["drama", "food", "fitness", "history"]},
    {"title": "Narcos", "genres": ["crime", "drama", "thriller"], "tags": ["travel", "history", "drama"]},
    {"title": "Peaky Blinders", "genres": ["crime", "drama", "history"], "tags": ["history", "fashion", "drama", "mystery"]},
    {"title": "Attack on Titan", "genres": ["anime", "action", "fantasy"], "tags": ["anime", "fantasy", "mystery", "fitness"]},
    {"title": "The Witcher", "genres": ["fantasy", "action", "adventure"], "tags": ["fantasy", "travel", "history", "nature"]},
    {"title": "House of Cards", "genres": ["drama", "thriller"], "tags": ["drama", "history", "tech"]},
    {"title": "Squid Game", "genres": ["thriller", "drama", "mystery"], "tags": ["mystery", "drama", "fitness", "travel"]},
    {"title": "Money Heist", "genres": ["crime", "thriller", "drama"], "tags": ["drama", "mystery", "travel", "music"]},
    {"title": "Euphoria", "genres": ["drama"], "tags": ["drama", "music", "fashion", "art", "photography"]},
    {"title": "White Lotus", "genres": ["drama", "comedy", "mystery"], "tags": ["travel", "drama", "comedy", "food"]},
    {"title": "Band of Brothers", "genres": ["drama", "action", "history"], "tags": ["history", "fitness", "drama"]},
    {"title": "Game of Thrones", "genres": ["fantasy", "drama", "action"], "tags": ["fantasy", "history", "drama", "travel"]},
    {"title": "The Boys", "genres": ["action", "comedy", "sci-fi"], "tags": ["comedy", "sci-fi", "drama", "mystery"]},
    {"title": "Severance", "genres": ["sci-fi", "thriller", "drama"], "tags": ["mystery", "tech", "drama", "science"]},
    {"title": "The Crown", "genres": ["drama", "history"], "tags": ["history", "fashion", "drama", "travel"]},
    {"title": "Wednesday", "genres": ["mystery", "comedy", "fantasy"], "tags": ["mystery", "comedy", "art", "fashion"]},
    {"title": "The Office", "genres": ["comedy"], "tags": ["comedy", "drama", "food"]},
    {"title": "Parks and Recreation", "genres": ["comedy"], "tags": ["comedy", "nature", "food", "travel"]},
    {"title": "Reacher", "genres": ["action", "crime", "thriller"], "tags": ["fitness", "mystery", "travel", "drama"]},
]


def score_series(series: dict, interests: list[str]) -> int:
    if not interests:
        return 50
    tags = series["tags"]
    matches = sum(1 for interest in interests if interest in tags)
    base = int((matches / len(tags)) * 80)
    # Bonus for each interest hit
    bonus = min(matches * 3, 20)
    return min(base + bonus + 40, 99)


class RecommendationService:
    def __init__(self, streaming_service: StreamingService):
        self.streaming = streaming_service

    def recommend(self, profile: InstagramProfile, top_n: int = 5) -> List[SeriesRecommendation]:
        interests = profile.interests or ["drama", "mystery"]
        scored: list[tuple[int, dict]] = []
        for series in SERIES_CATALOG:
            score = score_series(series, interests)
            scored.append((score, series))

        scored.sort(key=lambda x: x[0], reverse=True)
        candidates = scored[:top_n * 2]

        recommendations: list[SeriesRecommendation] = []
        for score, series in candidates:
            avail = self.streaming.check(series["title"])
            matched_interests = [i for i in interests if i in series["tags"]]
            reason = ", ".join(matched_interests[:4]) + " interests" if matched_interests else "general match"
            rec = SeriesRecommendation(
                title=series["title"],
                match_score=score,
                reason=reason,
                genres=series["genres"],
                streaming=avail,
            )
            recommendations.append(rec)

        # Sort: prefer Netflix/HBO Max, then by match score
        recommendations.sort(key=lambda r: r.priority_score(), reverse=True)
        return recommendations[:top_n]
