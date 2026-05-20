"""
Клиент Claude API для превращения voice transcript в готовый тред для Threads.

Использует Claude Sonnet, читает stylesheet из prompts/voice_to_thread.md,
возвращает YAML готовый положить в posts/queue/.
"""

import os
import json
import requests
from pathlib import Path


SYSTEM_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "prompts" / "voice_to_thread.md"
)


class ClaudeClient:
    def __init__(self):
        self.api_key = os.environ["ANTHROPIC_API_KEY"]
        self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    def voice_to_thread(self, transcript: str) -> dict:
        """
        Берёт сырой transcript, возвращает dict с готовым тредом:
        {
            "topic": "...",
            "variants": [
                {"thread": [{"text": "..."}, ...], "image_prompt": "..."},
                ...
            ]
        }
        """
        system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [{
                "role": "user",
                "content": (
                    f"Вот мой voice transcript:\n\n{transcript}\n\n"
                    "Сделай 3 варианта треда в моём стиле. "
                    "Верни ответ строго в JSON без преамбулы и без ```."
                )
            }]
        }

        r = requests.post(url, headers=headers, json=payload, timeout=120)
        if not r.ok:
            raise RuntimeError(
                f"Claude API failed [{r.status_code}]: {r.text}"
            )

        text = r.json()["content"][0]["text"].strip()
        # На всякий чистим ```json фенсы если Claude их вставил
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(text)
