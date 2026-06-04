#!/usr/bin/env python3
"""Deterministic test for the Gemini request/response shaping. No key, no network."""
import base64
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from app.gen import build_request_body, extract_image  # noqa: E402


def main():
    body = build_request_body("a cat, style: ukiyo-e")
    assert body["contents"][0]["parts"][0]["text"] == "a cat, style: ukiyo-e", body
    assert body["generationConfig"]["responseModalities"] == ["IMAGE"], body

    # extract_image pulls + decodes the first inlineData
    raw = b"\x89PNGfake"
    result = {"candidates": [{"content": {"parts": [
        {"text": "here you go"},
        {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(raw).decode()}},
    ]}}]}
    assert extract_image(result) == raw

    # no image -> clear error
    try:
        extract_image({"candidates": [{"content": {"parts": [{"text": "no image"}]}}]})
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError when no image in response")

    print("OK: request/response shaping test passed")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
