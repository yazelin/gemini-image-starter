"""Minimal Gemini image-generation client.

Mirrors the real Google Gemini image API so the same code works against the
live service and against a local fake server in tests:

    POST {base_url}/{model}:generateContent?key={api_key}
    body: {"contents":[{"parts":[{"text": prompt}]}],
           "generationConfig":{"responseModalities":["IMAGE"]}}
    resp: candidates[0].content.parts[].inlineData.data  (base64 image)

Get a free key at https://aistudio.google.com/apikey and set GEMINI_API_KEY.
"""
from __future__ import annotations

import base64

import httpx

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-2.5-flash-image"  # fallback: gemini-2.0-flash-exp-image-generation


def build_request_body(prompt: str) -> dict:
    """Pure: turn a prompt string into the Gemini generateContent body."""
    return {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }


def extract_image(result: dict) -> bytes:
    """Pure: pull the first inline image out of a Gemini response, decoded."""
    candidates = result.get("candidates", [])
    if candidates:
        for part in candidates[0].get("content", {}).get("parts", []):
            data = part.get("inlineData", {}).get("data")
            if data:
                return base64.b64decode(data)
    raise ValueError("no image found in response")


def generate(
    prompt: str,
    api_key: str,
    *,
    model: str = DEFAULT_MODEL,
    base_url: str = GEMINI_BASE,
    timeout: float = 60.0,
) -> bytes:
    """Call Gemini and return the generated image bytes.

    `base_url` is injectable so tests can point at a local fake server.
    """
    url = f"{base_url}/{model}:generateContent?key={api_key}"
    resp = httpx.post(url, json=build_request_body(prompt), timeout=timeout)
    resp.raise_for_status()
    return extract_image(resp.json())


def save_image(data: bytes, path: str) -> None:
    with open(path, "wb") as f:
        f.write(data)
