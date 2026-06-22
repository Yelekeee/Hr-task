# Hr-task — Friday Date TV Series Recommender

Scans an Instagram profile, uses Claude AI to analyze interests, and recommends a TV series for a Friday date night with streaming availability on Netflix, HBO Max, and Prime Video.

## Installation

```bash
cd Hr-task
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Get from console.anthropic.com |
| `RAPIDAPI_KEY` | Optional | Enables live Instagram scraping |
| `CLAUDE_MODEL` | Optional | Defaults to `claude-haiku-4-5` |

## Usage

```bash
# Activate venv first
source .venv/bin/activate

# Run with Instagram username (no @)
python -m src.cli username

# Run with exported JSON profile (no API keys needed)
python -m src.cli username --json profile.json

# Change number of results
python -m src.cli username --top 3
```

## JSON Profile Format (fallback mode)

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
Claude summary: A mystery-loving traveler with a dark aesthetic
Detected interests: mystery, travel, photography
Getting Claude recommendations...

Recommended Series for @example_user:

1. Dark
   Match Score: 91%
   Reason: Her love of mystery and travel perfectly matches this mind-bending thriller
   Genres: mystery, sci-fi, thriller
   Available: Netflix

2. The Last of Us
   Match Score: 84%
   Reason: Emotional depth and stunning landscapes appeal to her adventurous side
   Genres: drama, action, sci-fi
   Available: HBO Max
```

## Run Tests

```bash
python -m pytest tests/ -v
```
