"""
Клиент для генерации картинок через Gemini API.

По умолчанию используется gemini-2.5-flash-image (Nano Banana) -
дешевле и есть free tier 500 запросов/день.

Для качественных картинок с текстом можно переключить на
gemini-3-pro-image-preview (Nano Banana Pro) через GEMINI_IMAGE_MODEL.
"""

import os
import base64
import requests


class GeminiClient:
    def __init__(self):
        self.api_key = os.environ["GEMINI_API_KEY"]
        self.model = os.environ.get(
            "GEMINI_IMAGE_MODEL",
            "gemini-2.5-flash-image"
        )

    def generate_image(self, prompt: str) -> bytes:
        """Генерирует картинку, возвращает PNG bytes."""
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self.model}:generateContent"
        )

        # Добавляем "формат для Threads" чтобы пропорция была вертикальная
        full_prompt = (
            f"{prompt}\n\n"
            "Format: portrait orientation 4:5 aspect ratio, "
            "high quality, suitable for social media post."
        )

        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "responseModalities": ["IMAGE"]
            }
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

        r = requests.post(url, json=payload, headers=headers, timeout=120)
        if not r.ok:
            raise RuntimeError(
                f"Gemini image gen failed [{r.status_code}]: {r.text}"
            )

        data = r.json()

        # Достаём inline_data из ответа
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError(f"No candidates in response: {data}")

        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"])

        raise RuntimeError(f"No image found in response: {data}")
