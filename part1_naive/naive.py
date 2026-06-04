"""Part 1 baseline: the naive one-line prompt.

Run this a few times and you get a different cat every time — pose, style,
background, lighting all decided by the model, not you. That is the pain
Part 2 (a structured prompt) fixes.

    GEMINI_API_KEY=xxx uv run python part1_naive/naive.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.gen import generate, save_image  # noqa: E402

PROMPT = "a cat"  # bare. no style, no lighting, no composition -> uncontrolled


def main():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("set GEMINI_API_KEY first (free: https://aistudio.google.com/apikey)")
        sys.exit(1)
    img = generate(PROMPT, key)
    save_image(img, "naive_cat.png")
    print("saved naive_cat.png  (run again -> a different cat, every time)")


if __name__ == "__main__":
    main()
