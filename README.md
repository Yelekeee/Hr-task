# Hr-task — TV Series Recommender

Recommends a Friday evening TV series based on Instagram profile interests.

## Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

| Variable | Description |
|---|---|
| `RAPIDAPI_KEY` | RapidAPI key (optional — enables live Instagram + streaming data) |
| `OPENAI_API_KEY` | OpenAI key (reserved for future use) |

## Usage

```bash
# Live mode (requires RAPIDAPI_KEY)
python -m src.cli <username>

# Fallback with exported JSON
python -m src.cli <username> --json profile.json

# Adjust number of results
python -m src.cli <username> --top 3
```

## Example Output

```
Detected interests: mystery, travel, photography

Recommended Series for @example_user:

1. Dark
   Match Score: 91%
   Reason: mystery, travel, photography interests
   Genres: mystery, sci-fi, thriller
   Available: Netflix

2. The Last of Us
   Match Score: 84%
   Reason: mystery, drama interests
   Genres: drama, action, sci-fi
   Available: HBO Max
```

## JSON Fallback Format

```json
{
  "username": "example_user",
  "bio": "Travel lover, photography enthusiast",
  "captions": ["Amazing sunset #travel #photography"],
  "hashtags": ["nature", "explore"]
}
```
