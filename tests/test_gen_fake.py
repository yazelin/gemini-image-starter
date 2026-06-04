#!/usr/bin/env python3
"""End-to-end gen test against a local fake Gemini server. No API key, no network.

Exercises the real client path (build body -> POST -> parse inlineData ->
decode -> save) by pointing base_url at the fake server.
"""
import base64
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from app.gen import generate, save_image  # noqa: E402
from tests.fake_gemini import PNG_B64, start  # noqa: E402


def main():
    server, base_url = start()
    try:
        img = generate("a cat, style: ukiyo-e", api_key="fake-key", base_url=base_url)
        assert img == base64.b64decode(PNG_B64), "decoded image bytes mismatch"

        out = pathlib.Path(tempfile.gettempdir()) / "_gen_fake_test.png"
        save_image(img, str(out))
        assert out.read_bytes() == img, "saved file bytes mismatch"
        out.unlink()
        print("OK: gen against fake Gemini server passed")
    finally:
        server.shutdown()


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
