# umaygpt-threads

Автоматическая публикация постов в Threads через GitHub Actions.
Расписание: вторник, четверг в 11:00 по Алматы.

## Как это работает

```
voice note (ты) ──┐
                  ├─► draft_from_voice.py ──► posts/queue/*.yml
текст напрямую ───┘                                    │
                                                       ▼
                                            GitHub Actions cron
                                            (вт/чт 11:00 Алматы)
                                                       │
                                                       ▼
                                           ┌───────────┴────────────┐
                                           ▼                        ▼
                                    Gemini image gen           Threads API
                                    (если есть image_prompt)   (двухшаговый publish)
                                           │                        │
                                           ▼                        ▼
                                    media/*.png            опубликовано в Threads
                                           │                        │
                                           └────────┬───────────────┘
                                                    ▼
                                          posts/published/*.yml
                                          (архив + IDs постов)
```

## Первичная настройка

### 1. Залить на гитхаб

```bash
cd ~/where-you-keep-code
git clone <этот архив или твой репо>
cd umaygpt-threads
git init  # если ещё не репо
gh repo create umaygpt-threads --private --source=. --remote=origin --push
```

Или через веб-интерфейс GitHub — создать репо `umaygpt-threads`, запушить туда содержимое.

### 2. Положить секреты в GitHub

Settings → Secrets and variables → Actions → New repository secret.

Обязательные:

| Имя | Откуда брать |
|-----|--------------|
| `THREADS_USER_ID` | Из ответа OAuth-флоу или `curl /me` |
| `THREADS_ACCESS_TOKEN` | Long-lived токен из Генератора маркеров |
| `GEMINI_API_KEY` | aistudio.google.com → Get API key |

Опциональные (для refresh-token workflow):

| Имя | Откуда брать |
|-----|--------------|
| `GH_PAT` | GitHub Settings → Developer settings → Personal access tokens → Fine-grained → дать права `Actions: write` и `Secrets: write` на этот репо |

### 3. Проверить что workflow видны

GitHub → твой репо → Actions → должны быть два workflow:
- **Publish Threads posts** — крутится вт/чт в 06:00 UTC (= 11:00 Алматы)
- **Refresh Threads token** — крутится каждое воскресенье

Запусти **Publish** руками через **Run workflow** для теста — если в `posts/queue/` уже есть пост с прошедшим `publish_at`, оно его опубликует.

## Как добавить пост

### Способ 1: руками в queue/

Создай файл `posts/queue/YYYY-MM-DD-name.yml`:

```yaml
publish_at: '2026-05-26T11:00:00+05:00'
topic: my-topic
image_prompt: >-
  Описание картинки на английском, минималистично, vertical 4:5,
  тёмный фон, без людей и брендов.
thread:
  - text: |-
      первый пост треда, хук + контекст
  - text: |-
      второй пост, раскрытие
  - text: |-
      третий пост, инсайт или вопрос
```

Запушь — GitHub Action подхватит в ближайший слот.

### Способ 2: из voice note через draft_from_voice.py

Локально:

```bash
# Установить зависимости
pip install -r requirements.txt

# Положить .env с ANTHROPIC_API_KEY (см .env.example)
cp .env.example .env
# отредактировать .env

# Запустить
python scripts/draft_from_voice.py --text "сегодня сделал штуку которая..."

# Или из файла транскрипта
python scripts/draft_from_voice.py --file ~/voice-transcript.txt

# Или из stdin
echo "сегодня..." | python scripts/draft_from_voice.py
```

Скрипт покажет 3 варианта треда, ты выбираешь номер, оно кладёт YAML в `posts/queue/`.

### Интеграция с твоим телеграм-ботом

В твоём телеграм-боте в Claude Code добавь команду которая дёргает этот скрипт:

```python
# В обработчике voice message:
import subprocess
import os

def voice_to_threads(transcript: str) -> str:
    """Вызывает draft_from_voice.py и возвращает результат."""
    repo_path = os.path.expanduser("~/code/umaygpt-threads")
    result = subprocess.run(
        ["python", "scripts/draft_from_voice.py", "--text", transcript],
        cwd=repo_path,
        input="1\n",  # автоматически выбирает вариант 1, можно сделать выбор интерактивным
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.stdout
```

После того как пост в queue — `git add posts/ && git commit && git push` и оно само опубликуется в расписании.

## Slot logic

`draft_from_voice.py` сам подбирает ближайший свободный слот:
- Берёт ближайший вт/чт в 11:00 Алматы
- Проверяет нет ли уже поста на это время в очереди
- Если занят — ищет следующий

Так посты не наслаиваются. Если хочешь конкретное время:

```bash
python scripts/draft_from_voice.py --text "..." --when 2026-06-03T11:00
```

## Refresh токена

Long-lived токен живёт 60 дней. Workflow `refresh-token.yml` каждое воскресенье:

1. Дёргает `refresh_access_token` endpoint
2. Получает новый токен на 60 дней
3. Обновляет GitHub Secret `THREADS_ACCESS_TOKEN` через GitHub API (нужен `GH_PAT`)

Если `GH_PAT` не настроен — workflow просто покажет новый токен в логе, тебе придётся скопировать его руками в Secret.

## Когда что-то сломается

### Workflow упал на публикации

GitHub → Actions → клик на упавший run → смотришь лог. Самые частые причины:

- **Токен протух** — запусти Refresh workflow руками, или если уже >60 дней без рефреша, нужно заново пройти OAuth и положить новый токен
- **Картинка не сгенерилась** — Gemini вернул refusal (контент-политика). Упрости промпт, убери человекоподобные термины
- **Threads вернул ошибку при reply** — Threads иногда тормозит между постами треда. Текущая пауза 3 секунды + 5 секунд на публикацию контейнера; если ловишь ошибки, увеличь паузы в `threads_client.py`

### Не успел протестить и пост улетел корявым

Зайди в Threads приложение, удали пост руками. Удали соответствующий YAML из `posts/published/` если хочешь почистить историю.

## Структура папок

```
umaygpt-threads/
├── .github/workflows/        # GitHub Actions
├── scripts/                  # CLI входы
│   ├── post_to_threads.py    # публикатор (запускает Action)
│   ├── draft_from_voice.py   # voice → YAML (запускаешь ты)
│   └── refresh_token.py      # обновление токена (Action)
├── lib/                      # клиенты API
│   ├── threads_client.py
│   ├── gemini_client.py
│   └── claude_client.py
├── prompts/                  # промпты для Claude
│   ├── voice_to_thread.md    # ← стиль Султана живёт здесь
│   └── image_style.md        # ← визуальный референс
├── posts/
│   ├── queue/                # ждут публикации
│   └── published/            # архив
├── media/                    # сгенерированные картинки
├── requirements.txt
├── .env.example
└── README.md
```

## Контент-стратегия (краткое напоминание)

Полная стратегия — в чате с Claude. Тут только напоминалки:

- **Хук в первой строке** — конкретное действие или цифра, не общие слова
- **2-4 поста в треде** — больше не читают
- **Без emoji**
- **Без длинных тире**
- **Лоукейс**
- **Картинка к первому посту** — буст охвата на ~60%
- **Открытый вопрос в конце** — но не банальное "что думаете?", а профессиональный конкретный
- **4 поста в неделю** (вт/чт обычные, пт вечером антипример) — золотая середина
