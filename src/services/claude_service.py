import json
from typing import Optional

from src.config import Config

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False


INTEREST_EXTRACTION_PROMPT = """You are analyzing an Instagram profile to identify this person's interests for a TV series recommendation.

Profile data:
- Username: {username}
- Bio: {bio}
- Recent captions: {captions}
- Hashtags: {hashtags}

Extract interests and personality traits from this profile. Consider:
- Hobbies, passions, lifestyle
- Aesthetic preferences
- Topics they engage with
- Mood/tone of their content

Return a JSON object with:
{{
  "interests": ["list", "of", "interests"],
  "personality_traits": ["list", "of", "traits"],
  "content_mood": "dark/light/adventurous/romantic/etc",
  "summary": "one sentence about this person"
}}

Be concise. Infer from limited data if needed. Works for any language (Russian, English, etc.)."""


RECOMMENDATION_PROMPT = """You are recommending TV series for a Friday date night based on someone's Instagram interests.

Person's profile:
- Interests: {interests}
- Personality traits: {traits}
- Content mood: {mood}
- Summary: {summary}

Recommend exactly 5 TV series for a romantic Friday evening. Prioritize series available on Netflix or HBO Max.

For each series return:
- title: exact English title
- match_score: 60-99 (how well it fits this person)
- reason: 1 sentence why it fits HER interests specifically (personal, not generic)
- genres: list of 2-3 genres
- preferred_platform: "Netflix", "HBO Max", "Prime Video", or "Unknown"

Return a JSON array of 5 objects. No extra text."""


class ClaudeService:
    def __init__(self, config: Config):
        self.config = config
        self._client: Optional[object] = None
        if _ANTHROPIC_AVAILABLE and config.anthropic_api_key:
            self._client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    @property
    def available(self) -> bool:
        return self._client is not None

    def extract_interests(
        self,
        username: str,
        bio: str,
        captions: list[str],
        hashtags: list[str],
    ) -> dict:
        if not self.available:
            return {}
        prompt = INTEREST_EXTRACTION_PROMPT.format(
            username=username,
            bio=bio or "(empty)",
            captions="; ".join(captions[:10]) or "(none)",
            hashtags=", ".join(hashtags[:30]) or "(none)",
        )
        return self._call(prompt) or {}

    def recommend_series(
        self,
        interests: list[str],
        traits: list[str],
        mood: str,
        summary: str,
    ) -> list[dict]:
        if not self.available:
            return []
        prompt = RECOMMENDATION_PROMPT.format(
            interests=", ".join(interests) or "general",
            traits=", ".join(traits) or "unknown",
            mood=mood or "neutral",
            summary=summary or "Instagram user",
        )
        result = self._call(prompt)
        if isinstance(result, list):
            return result
        return []

    def _call(self, prompt: str) -> "dict | list | None":
        try:
            message = self._client.messages.create(
                model=self.config.claude_model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            text = message.content[0].text.strip()
            # Strip markdown code fences if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except Exception as e:
            if self.config.debug:
                print(f"[Claude API error] {e}")
            return None
