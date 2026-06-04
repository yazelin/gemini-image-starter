"""Structured prompt builder — the heart of Part 2.

Part 1 (part1_naive/) sends a bare one-line prompt like "a cat": the model
fills in every unstated decision itself, so you get a different, uncontrolled
image each time. Part 2 assembles a *structured* prompt from named fields, so
the same inputs describe the same picture every time and you control style,
lighting, composition, palette, and what to avoid.

This module is pure (no network, no API key), so it is fully deterministic and
easy to test.
"""
from __future__ import annotations


def build_prompt(
    subject: str,
    *,
    style: str | None = None,
    lighting: str | None = None,
    composition: str | None = None,
    color: str | None = None,
    extra: str | None = None,
    negative: str | None = None,
) -> str:
    """Assemble a structured image prompt from named fields.

    Same inputs always produce the same string. `negative` becomes an
    "Avoid: ..." clause the model treats as things to leave out.
    """
    parts = [subject.strip()]
    if style:
        parts.append(f"style: {style.strip()}")
    if lighting:
        parts.append(f"lighting: {lighting.strip()}")
    if composition:
        parts.append(f"composition: {composition.strip()}")
    if color:
        parts.append(f"color palette: {color.strip()}")
    if extra:
        parts.append(extra.strip())
    prompt = ", ".join(parts)
    if negative:
        prompt += f". Avoid: {negative.strip()}"
    return prompt
