from typing import List

from src.models.profile import InstagramProfile, SeriesRecommendation, StreamingAvailability
from src.services.streaming_service import StreamingService
from src.services.claude_service import ClaudeService

# Fallback static catalog used when Claude API is unavailable
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
    {"title": "Squid Game", "genres": ["thriller", "drama", "mystery"], "tags": ["mystery", "drama", "fitness", "travel"]},
    {"title": "Money Heist", "genres": ["crime", "thriller", "drama"], "tags": ["drama", "mystery", "travel", "music"]},
    {"title": "Euphoria", "genres": ["drama"], "tags": ["drama", "music", "fashion", "art", "photography"]},
    {"title": "White Lotus", "genres": ["drama", "comedy", "mystery"], "tags": ["travel", "drama", "comedy", "food"]},
    {"title": "Band of Brothers", "genres": ["drama", "action", "history"], "tags": ["history", "fitness", "drama"]},
    {"title": "Game of Thrones", "genres": ["fantasy", "drama", "action"], "tags": ["fantasy", "history", "drama", "travel"]},
    {"title": "The Boys", "genres": ["action", "comedy", "sci-fi"], "tags": ["comedy", "drama", "mystery"]},
    {"title": "Severance", "genres": ["sci-fi", "thriller", "drama"], "tags": ["mystery", "tech", "drama", "science"]},
    {"title": "The Crown", "genres": ["drama", "history"], "tags": ["history", "fashion", "drama", "travel"]},
    {"title": "Wednesday", "genres": ["mystery", "comedy", "fantasy"], "tags": ["mystery", "comedy", "art", "fashion"]},
    {"title": "Chilling Adventures of Sabrina", "genres": ["fantasy", "horror", "drama"], "tags": ["fantasy", "mystery", "art"]},
    {"title": "Emily in Paris", "genres": ["romance", "comedy", "drama"], "tags": ["romance", "fashion", "travel", "food"]},
    {"title": "Bridgerton", "genres": ["romance", "drama", "history"], "tags": ["romance", "fashion", "history", "drama"]},
    {"title": "Outlander", "genres": ["romance", "drama", "history"], "tags": ["romance", "history", "travel", "fantasy"]},
    {"title": "Reacher", "genres": ["action", "crime", "thriller"], "tags": ["fitness", "mystery", "travel", "drama"]},
]


def _score_series(series: dict, interests: list[str]) -> int:
    if not interests:
        return 50
    tags = series["tags"]
    matches = sum(1 for interest in interests if interest in tags)
    base = int((matches / len(tags)) * 80)
    bonus = min(matches * 3, 20)
    return min(base + bonus + 40, 99)


class RecommendationService:
    def __init__(self, streaming_service: StreamingService, claude_service: ClaudeService):
        self.streaming = streaming_service
        self.claude = claude_service

    def recommend(self, profile: InstagramProfile, top_n: int = 5) -> List[SeriesRecommendation]:
        # Try Claude-powered recommendations first
        if self.claude.available and profile.claude_data:
            recs = self._recommend_with_claude(profile, top_n)
            if recs:
                return recs

        # Fallback to keyword-based scoring
        return self._recommend_static(profile, top_n)

    def _recommend_with_claude(self, profile: InstagramProfile, top_n: int) -> List[SeriesRecommendation]:
        claude_data = profile.claude_data
        suggestions = self.claude.recommend_series(
            interests=claude_data.get("interests", profile.interests),
            traits=claude_data.get("personality_traits", []),
            mood=claude_data.get("content_mood", "neutral"),
            summary=claude_data.get("summary", ""),
        )
        if not suggestions:
            return []

        recommendations: list[SeriesRecommendation] = []
        for item in suggestions[:top_n]:
            title = item.get("title", "")
            if not title:
                continue
            avail = self.streaming.check(title)
            rec = SeriesRecommendation(
                title=title,
                match_score=int(item.get("match_score", 75)),
                reason=item.get("reason", ""),
                genres=item.get("genres", []),
                streaming=avail,
            )
            recommendations.append(rec)

        recommendations.sort(key=lambda r: r.priority_score(), reverse=True)
        return recommendations

    def _recommend_static(self, profile: InstagramProfile, top_n: int) -> List[SeriesRecommendation]:
        interests = profile.interests or ["drama", "mystery"]
        scored = sorted(
            [(s, _score_series(s, interests)) for s in SERIES_CATALOG],
            key=lambda x: x[1],
            reverse=True,
        )
        candidates = scored[:top_n * 2]

        recommendations: list[SeriesRecommendation] = []
        for series, score in candidates:
            avail = self.streaming.check(series["title"])
            matched = [i for i in interests if i in series["tags"]]
            reason = ", ".join(matched[:4]) + " interests" if matched else "general match"
            rec = SeriesRecommendation(
                title=series["title"],
                match_score=score,
                reason=reason,
                genres=series["genres"],
                streaming=avail,
            )
            recommendations.append(rec)

        recommendations.sort(key=lambda r: r.priority_score(), reverse=True)
        return recommendations[:top_n]
