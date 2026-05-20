"""
Публикация тредов в Threads из очереди posts/queue/.

Логика:
1. Идём по всем YAML в posts/queue/
2. Берём те, у которых publish_at <= сейчас
3. Если есть image_prompt — генерим картинку через Gemini, коммитим в media/
4. Публикуем тред: первый пост -> reply -> reply -> ...
5. Переносим YAML в posts/published/
"""

import os
import sys
import time
import yaml
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.threads_client import ThreadsClient
from lib.gemini_client import GeminiClient

QUEUE_DIR = Path(__file__).resolve().parent.parent / "posts" / "queue"
PUBLISHED_DIR = Path(__file__).resolve().parent.parent / "posts" / "published"
MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"

# Базовый raw URL для картинок (на проде заменяется из env)
REPO_RAW_BASE = os.environ.get(
    "REPO_RAW_BASE",
    "https://raw.githubusercontent.com/USERNAME/umaygpt-threads/main"
)


def load_due_posts():
    """Возвращает YAML'ы у которых publish_at уже наступил."""
    now = datetime.now(timezone.utc)
    due = []
    for path in sorted(QUEUE_DIR.glob("*.yml")):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        publish_at = data.get("publish_at")
        if isinstance(publish_at, str):
            publish_at = datetime.fromisoformat(publish_at)
        if publish_at.tzinfo is None:
            publish_at = publish_at.replace(tzinfo=timezone.utc)
        if publish_at <= now:
            due.append((path, data))
    return due


def maybe_generate_image(post_data, base_name):
    """Если у поста есть image_prompt — генерит картинку, возвращает public URL."""
    image_prompt = post_data.get("image_prompt")
    if not image_prompt:
        return None

    filename = f"{base_name}.png"
    out_path = MEDIA_DIR / filename

    if out_path.exists() and out_path.stat().st_size > 0:
        print(f"[image] reusing existing {out_path}")
        return f"{REPO_RAW_BASE}/media/{filename}"

    gemini = GeminiClient()
    image_bytes = gemini.generate_image(image_prompt)
    out_path.write_bytes(image_bytes)
    print(f"[image] saved to {out_path}")

    if os.environ.get("GITHUB_ACTIONS") == "true":
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(
            ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
            check=True,
        )
        subprocess.run(["git", "add", str(out_path)], check=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if diff.returncode != 0:
            subprocess.run(["git", "commit", "-m", f"auto: add image for {base_name}"], check=True)
            subprocess.run(["git", "push"], check=True)
            print(f"[image] pushed to repo, waiting for CDN")
            time.sleep(20)

    return f"{REPO_RAW_BASE}/media/{filename}"


def publish_thread(data, base_name):
    """Публикует тред в Threads. Возвращает список ID опубликованных постов."""
    client = ThreadsClient()
    thread_items = data["thread"]

    posted_ids = []
    reply_to = None

    for i, item in enumerate(thread_items):
        text = item["text"]
        image_url = None

        # Картинка только у первого поста (если есть image_prompt в корне)
        if i == 0 and data.get("image_prompt"):
            image_url = maybe_generate_image(data, base_name)
            # Даём GitHub раздать raw файл (после коммита нужна секунда-две)
            if image_url:
                time.sleep(10)

        # Картинка может быть и внутри отдельного шага треда
        if item.get("image_prompt"):
            step_image = maybe_generate_image(
                {"image_prompt": item["image_prompt"]},
                f"{base_name}-step{i}"
            )
            if step_image:
                image_url = step_image
                time.sleep(10)

        post_id = client.publish_post(
            text=text,
            image_url=image_url,
            reply_to_id=reply_to,
        )
        posted_ids.append(post_id)
        reply_to = post_id

        # Между постами треда — небольшая пауза чтобы Threads успел обработать
        if i < len(thread_items) - 1:
            time.sleep(3)

    return posted_ids


def main():
    due = load_due_posts()
    if not due:
        print("Нет постов готовых к публикации.")
        return

    for path, data in due:
        base_name = path.stem
        print(f"\n=== Публикую: {base_name} ===")
        try:
            posted_ids = publish_thread(data, base_name)
            print(f"[ok] опубликовано {len(posted_ids)} постов: {posted_ids}")

            # Записываем результат и переносим в published
            data["published_at"] = datetime.now(timezone.utc).isoformat()
            data["thread_ids"] = posted_ids
            published_path = PUBLISHED_DIR / path.name
            with open(published_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
            path.unlink()
            print(f"[ok] перенесено в {published_path}")

        except Exception as e:
            print(f"[error] {base_name}: {e}")
            # Не прерываем весь батч — пытаемся опубликовать остальные
            continue


if __name__ == "__main__":
    main()
