"""
Клиент для Threads API. Двухшаговая публикация:
1. POST /{user_id}/threads -> создаёт media container, возвращает creation_id
2. POST /{user_id}/threads_publish -> публикует контейнер, возвращает post_id

Для реплая внутри треда передаётся reply_to_id на шаге создания контейнера.
"""

import os
import time
import requests


GRAPH_BASE = "https://graph.threads.net/v1.0"


class ThreadsClient:
    def __init__(self):
        self.user_id = os.environ["THREADS_USER_ID"]
        self.access_token = os.environ["THREADS_ACCESS_TOKEN"]

    def _create_container(self, text, image_url=None, reply_to_id=None):
        url = f"{GRAPH_BASE}/{self.user_id}/threads"
        params = {
            "access_token": self.access_token,
            "text": text,
        }
        if image_url:
            params["media_type"] = "IMAGE"
            params["image_url"] = image_url
        else:
            params["media_type"] = "TEXT"

        if reply_to_id:
            params["reply_to_id"] = reply_to_id

        r = requests.post(url, data=params, timeout=60)
        if not r.ok:
            raise RuntimeError(
                f"create_container failed [{r.status_code}]: {r.text}"
            )
        return r.json()["id"]

    def _publish_container(self, creation_id):
        url = f"{GRAPH_BASE}/{self.user_id}/threads_publish"
        params = {
            "access_token": self.access_token,
            "creation_id": creation_id,
        }
        r = requests.post(url, data=params, timeout=60)
        if not r.ok:
            raise RuntimeError(
                f"publish_container failed [{r.status_code}]: {r.text}"
            )
        return r.json()["id"]

    def publish_post(self, text, image_url=None, reply_to_id=None):
        """Создаёт контейнер -> ждёт обработки -> публикует. Возвращает post_id."""
        creation_id = self._create_container(text, image_url, reply_to_id)

        # Threads рекомендует подождать перед публикацией, особенно для медиа
        wait_seconds = 30 if image_url else 5
        time.sleep(wait_seconds)

        post_id = self._publish_container(creation_id)
        return post_id
