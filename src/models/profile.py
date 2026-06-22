from dataclasses import dataclass, field
from typing import List


@dataclass
class InstagramProfile:
    username: str
    bio: str = ""
    captions: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    follower_count: int = 0
    following_count: int = 0
    claude_data: dict = field(default_factory=dict)  # enriched by Claude API


@dataclass
class StreamingAvailability:
    netflix: bool = False
    hbo_max: bool = False
    prime_video: bool = False

    def available_platforms(self) -> List[str]:
        platforms = []
        if self.netflix:
            platforms.append("Netflix")
        if self.hbo_max:
            platforms.append("HBO Max")
        if self.prime_video:
            platforms.append("Prime Video")
        return platforms


@dataclass
class SeriesRecommendation:
    title: str
    match_score: int
    reason: str
    genres: List[str]
    streaming: StreamingAvailability = field(default_factory=StreamingAvailability)

    def priority_score(self) -> float:
        platform_bonus = 0.0
        if self.streaming.netflix or self.streaming.hbo_max:
            platform_bonus = 5.0
        return self.match_score + platform_bonus
