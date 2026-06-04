#!/usr/bin/env python3
"""Deterministic test for the structured prompt builder. No key, no network."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from app.prompt import build_prompt  # noqa: E402


def main():
    p = build_prompt(
        "a cat",
        style="ukiyo-e woodblock",
        lighting="soft morning light",
        composition="centered, close-up",
        negative="text, watermark",
    )
    assert p.startswith("a cat"), p
    assert "style: ukiyo-e woodblock" in p, p
    assert "lighting: soft morning light" in p, p
    assert "composition: centered, close-up" in p, p
    assert p.endswith("Avoid: text, watermark"), p

    # structured = deterministic: same inputs -> identical string
    again = build_prompt(
        "a cat",
        style="ukiyo-e woodblock",
        lighting="soft morning light",
        composition="centered, close-up",
        negative="text, watermark",
    )
    assert again == p, "same inputs must give the same prompt"

    # minimal: subject only
    assert build_prompt("a cat") == "a cat"

    print("OK: prompt builder test passed")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
