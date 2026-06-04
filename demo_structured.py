"""Part 2: a structured prompt -> a controllable, reproducible image.

Compare with part1_naive/naive.py ("a cat"): here every decision is named, so
you steer style / lighting / composition / palette and say what to avoid.

    GEMINI_API_KEY=xxx uv run python demo_structured.py
"""
import os
import sys

from app.gen import generate, save_image
from app.prompt import build_prompt


def main():
    prompt = build_prompt(
        "a cat sitting by a window",
        style="ukiyo-e woodblock print",
        lighting="soft morning light",
        composition="centered, close-up",
        color="muted indigo and gold",
        negative="text, watermark, extra limbs",
    )
    print("prompt:", prompt)

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("(set GEMINI_API_KEY to actually generate: https://aistudio.google.com/apikey)")
        return
    img = generate(prompt, key)
    save_image(img, "structured_cat.png")
    print("saved structured_cat.png  (same fields -> same kind of picture, every time)")


if __name__ == "__main__":
    main()
