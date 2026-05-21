"""
CLI для превращения voice transcript в готовый YAML для очереди.

Использование:
    # Из текста напрямую
    python scripts/draft_from_voice.py --text "сегодня сделал такую штуку..."

    # Из файла транскрипта
    python scripts/draft_from_voice.py --file /tmp/transcript.txt

    # С указанием времени публикации
    python scripts/draft_from_voice.py --text "..." --when 2026-05-27T11:00

После запуска показывает 3 варианта в терминале, ты выбираешь номер,
и YAML кладётся в posts/queue/ с правильным publish_at.

Время по умолчанию - ближайший слот Вт/Ср/Чт 11:00 Алматы.
"""

import argparse
import sys
import yaml
from pathlib import Path
from datetime import datetime, timedelta, timezone, time as dt_time
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.claude_client import ClaudeClient

QUEUE_DIR = Path(__file__).resolve().parent.parent / "posts" / "queue"
ALMATY = ZoneInfo("Asia/Almaty")
SLOT_HOUR = 11
SLOT_MINUTE = 0
# 1=Tue, 3=Thu, 5=Sat (Python weekday: Mon=0)
SLOT_WEEKDAYS = {1, 3, 5}


def next_slot(from_dt=None):
    """Возвращает ближайший слот Вт/Чт/Сб 11:00 Алматы после from_dt."""
    if from_dt is None:
        from_dt = datetime.now(ALMATY)

    candidate = from_dt.replace(
        hour=SLOT_HOUR, minute=SLOT_MINUTE, second=0, microsecond=0
    )
    if candidate <= from_dt:
        candidate += timedelta(days=1)

    while candidate.weekday() not in SLOT_WEEKDAYS:
        candidate += timedelta(days=1)
    return candidate


def free_slot():
    """Ищет первый слот в котором ещё нет поста в очереди."""
    existing = set()
    for p in QUEUE_DIR.glob("*.yml"):
        with open(p, "r", encoding="utf-8") as f:
            d = yaml.safe_load(f)
        existing.add(str(d.get("publish_at"))[:16])  # YYYY-MM-DDTHH:MM

    candidate = next_slot()
    while candidate.isoformat()[:16] in existing:
        candidate = next_slot(candidate)
    return candidate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", help="Voice transcript текстом")
    parser.add_argument("--file", help="Путь к файлу с transcript")
    parser.add_argument(
        "--when",
        help="ISO время публикации в зоне Алматы, иначе следующий свободный слот"
    )
    args = parser.parse_args()

    if args.text:
        transcript = args.text
    elif args.file:
        transcript = Path(args.file).read_text(encoding="utf-8")
    else:
        print("Введи transcript (Ctrl+D чтобы закончить):")
        transcript = sys.stdin.read()

    if not transcript.strip():
        print("Пустой transcript, выхожу.")
        sys.exit(1)

    if args.when:
        publish_at = datetime.fromisoformat(args.when).replace(tzinfo=ALMATY)
    else:
        publish_at = free_slot()

    print(f"\nГенерирую варианты через Claude API...\n")
    client = ClaudeClient()
    result = client.voice_to_thread(transcript)

    variants = result.get("variants", [])
    if not variants:
        print("Claude не вернул вариантов, проверь промпт.")
        sys.exit(1)

    for i, v in enumerate(variants, 1):
        print(f"\n{'=' * 60}")
        print(f"ВАРИАНТ {i}")
        print('=' * 60)
        for j, post in enumerate(v.get("thread", []), 1):
            print(f"\n[{j}/{len(v['thread'])}]")
            print(post["text"])
        if v.get("image_prompt"):
            print(f"\n[image_prompt]: {v['image_prompt']}")
    print()

    choice = input(f"Выбери вариант (1-{len(variants)}) или Enter для отмены: ").strip()
    if not choice:
        print("Отменено.")
        sys.exit(0)

    chosen = variants[int(choice) - 1]

    topic = result.get("topic", "post")
    safe_topic = "".join(c if c.isalnum() or c in "-_" else "-" for c in topic.lower())[:40]
    filename = f"{publish_at.strftime('%Y-%m-%d')}-{safe_topic}.yml"
    out_path = QUEUE_DIR / filename

    out_data = {
        "publish_at": publish_at.isoformat(),
        "topic": topic,
        "thread": chosen["thread"],
    }
    if chosen.get("image_prompt"):
        out_data["image_prompt"] = chosen["image_prompt"]

    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(out_data, f, allow_unicode=True, sort_keys=False)

    print(f"\n[ok] Положил в {out_path}")
    print(f"     Публикация: {publish_at.strftime('%a %d %b в %H:%M')} по Алматы")


if __name__ == "__main__":
    main()
