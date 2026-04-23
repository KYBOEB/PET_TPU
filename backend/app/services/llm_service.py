import json
from pathlib import Path

import httpx

from app.config import settings

RANGES = {
    "low":    {"exp": (10, 20),  "hunger": (5, 15)},
    "medium": {"exp": (25, 40),  "hunger": (20, 35)},
    "high":   {"exp": (60, 80),  "hunger": (50, 70)},
}

FALLBACK = {"difficulty": "medium", "exp_reward": 25, "hunger_reward": 20}

PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / ".." / "prompts" / "bulk_evaluate.txt"


def _make_fallback(title: str) -> dict:
    return {"title": title, **FALLBACK}


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def _validate_item(item: dict, title: str) -> dict:
    difficulty = item.get("difficulty")
    if difficulty not in RANGES:
        return _make_fallback(title)

    exp_lo, exp_hi = RANGES[difficulty]["exp"]
    hunger_lo, hunger_hi = RANGES[difficulty]["hunger"]

    try:
        exp_reward = _clamp(int(item["exp_reward"]), exp_lo, exp_hi)
        hunger_reward = _clamp(int(item["hunger_reward"]), hunger_lo, hunger_hi)
    except (KeyError, ValueError, TypeError):
        return _make_fallback(title)

    return {
        "title": title,
        "difficulty": difficulty,
        "exp_reward": exp_reward,
        "hunger_reward": hunger_reward,
    }


async def evaluate_tasks(titles: list[str]) -> list[dict]:
    """Returns: [{"title": str, "difficulty": str, "exp_reward": int, "hunger_reward": int}]"""
    if settings.LLM_PROVIDER == "fallback":
        return [_make_fallback(t) for t in titles]

    if settings.LLM_PROVIDER != "local":
        print(f"Unknown LLM_PROVIDER: {settings.LLM_PROVIDER}, using fallback")
        return [_make_fallback(t) for t in titles]

    try:
        prompt_text = PROMPT_PATH.read_text(encoding="utf-8")
        prompt_text = prompt_text.replace("{tasks_json}", json.dumps(titles, ensure_ascii=False))

        timeout = httpx.Timeout(settings.LLM_TIMEOUT)

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                settings.LLM_API_URL,
                json={
                    "model": settings.LLM_MODEL,
                    "prompt": prompt_text,
                    "stream": False,
                },
            )
            resp.raise_for_status()
            llm_text = resp.json()["response"]

        results = json.loads(llm_text)

        validated = []
        for i, title in enumerate(titles):
            if i < len(results):
                validated.append(_validate_item(results[i], title))
            else:
                validated.append(_make_fallback(title))

        return validated

    except Exception as e:
        print(f"LLM error: {e}, using fallback for all tasks")
        return [_make_fallback(t) for t in titles]
