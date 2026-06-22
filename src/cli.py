#!/usr/bin/env python3
"""CLI entrypoint: python -m src.cli <username> [--json <path>]"""

import sys
import argparse
from dotenv import load_dotenv

from src.config import Config
from src.services.instagram_service import InstagramService
from src.services.streaming_service import StreamingService
from src.services.claude_service import ClaudeService
from src.services.recommendation_service import RecommendationService

load_dotenv()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Friday date TV series recommender based on Instagram interests"
    )
    parser.add_argument("username", help="Instagram username")
    parser.add_argument("--json", metavar="FILE", help="Path to exported profile JSON (fallback)")
    parser.add_argument("--top", type=int, default=5, help="Number of recommendations (default: 5)")
    return parser.parse_args()


def print_recommendations(recommendations: list, username: str) -> None:
    print(f"\nRecommended Series for @{username}:\n")
    for i, rec in enumerate(recommendations, 1):
        platforms = rec.streaming.available_platforms()
        availability = ", ".join(platforms) if platforms else "Not in catalog"
        print(f"{i}. {rec.title}")
        print(f"   Match Score: {rec.match_score}%")
        print(f"   Reason: {rec.reason}")
        print(f"   Genres: {', '.join(rec.genres)}")
        print(f"   Available: {availability}")
        print()


def main() -> int:
    args = parse_args()
    config = Config.from_env()

    ig_service = InstagramService(config)
    streaming_service = StreamingService(config)
    claude_service = ClaudeService(config)
    rec_service = RecommendationService(streaming_service, claude_service)

    profile = None

    # 1. JSON fallback
    if args.json:
        profile = ig_service.load_from_json(args.json)
        if profile is None:
            print(f"Error: could not load JSON from {args.json}", file=sys.stderr)
            return 1
        print(f"Loaded profile from JSON: {args.json}")

    # 2. Live Instagram API
    if profile is None and config.rapidapi_key:
        print(f"Fetching Instagram profile for @{args.username}...")
        profile = ig_service.fetch_profile(args.username)
        if profile is None:
            print("Warning: Instagram API unavailable, using fallback mode.", file=sys.stderr)

    # 3. Mock fallback
    if profile is None:
        print("Using fallback mode (no live Instagram data).")
        profile = ig_service.build_mock_profile(args.username)

    if not profile.interests:
        profile.interests = ["drama", "mystery"]

    # 4. Enrich with Claude if available
    if claude_service.available:
        print("Analyzing profile with Claude...")
        claude_data = claude_service.extract_interests(
            username=profile.username,
            bio=profile.bio,
            captions=profile.captions,
            hashtags=profile.hashtags,
        )
        if claude_data:
            profile.claude_data = claude_data
            profile.interests = claude_data.get("interests", profile.interests)
            print(f"Claude summary: {claude_data.get('summary', '')}")
        print(f"Detected interests: {', '.join(profile.interests)}")
        print("Getting Claude recommendations...")
    else:
        print(f"Detected interests: {', '.join(profile.interests)}")

    recommendations = rec_service.recommend(profile, top_n=args.top)
    print_recommendations(recommendations, args.username)
    return 0


if __name__ == "__main__":
    sys.exit(main())
