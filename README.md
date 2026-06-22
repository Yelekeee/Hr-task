# Hr-task — Friday Date TV Series Recommender

Scans an Instagram profile, uses **Claude AI** to analyze interests, and recommends a TV series for a Friday date night with streaming availability on Netflix, HBO Max, and Prime Video.

## Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env`:

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Recommended | Claude API key for intelligent analysis |
| `RAPIDAPI_KEY` | Optional | Live Instagram scraping via RapidAPI |
| `CLAUDE_MODEL` | Optional | Defaults to `claude-haiku-4-5` |

## Usage

```bash
# With Claude API (recommended)
python -m src.cli <username>

# With exported JSON profile
python -m src.cli <username> --json profile.json

# Adjust number of results
python -m src.cli <username> --top 3
```

## JSON Fallback Format

```json
{
  "username": "example_user",
  "bio": "Люблю горы, кофе и детективы",
  "captions": ["Amazing sunset #travel #photography"],
  "hashtags": ["nature", "mystery"]
}
```

## Example Output

```
Analyzing profile with Claude...
Claude summary: A mystery-loving traveler with a taste for dark aesthetics
Detected interests: mystery, travel, photography
Getting Claude recommendations...

Recommended Series for @example_user:

1. Dark
   Match Score: 91%
   Reason: Her love of mystery and travel perfectly matches this mind-bending German thriller
   Genres: mystery, sci-fi, thriller
   Available: Netflix

2. The Last of Us
   Match Score: 84%
   Reason: Emotional depth and stunning landscapes appeal to her adventurous side
   Genres: drama, action, sci-fi
   Available: HBO Max
```

## Architecture

```
cli.py
  ├── InstagramService   — fetch/parse profile, keyword interest extraction
  ├── ClaudeService      — AI interest analysis + series recommendations
  ├── RecommendationService — orchestrates Claude + static fallback scoring
  └── StreamingService   — availability check (API or static catalog)
```

## Run Tests

```bash
python -m pytest tests/ -v
```
