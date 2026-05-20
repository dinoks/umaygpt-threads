# Визуальный стиль картинок к постам

Этот файл — референс для написания image_prompt. Не используется напрямую кодом, но Claude должен ориентироваться на него когда генерит image_prompt в варианте поста.

## Базовые правила

- **Vertical 4:5** — оптимальная пропорция для feed Threads (1080x1350)
- **Тёмный фон** — соответствует визуальному стилю UmayGPT и не слепит в ленте
- **Без людей** — генерация людей часто выходит криво и съедает аутентичность
- **Без названий брендов и реальных лого** — Gemini часто рендерит коряво и это палится
- **Без текста на картинке** — кроме случаев когда это часть концепта (схема, dashboard mockup)

## Стили которые работают

### 1. Минималистичная 3D иллюстрация
```
Minimalist 3D illustration on dark navy background, abstract geometric shapes,
soft gradient lighting, modern professional aesthetic, vertical 4:5 composition,
no text, no people, subtle glow effects
```

### 2. Дашборд / интерфейс-мокап
```
UI dashboard mockup on dark background, clean modern interface with data charts,
graph visualization, soft purple and teal accents, no real brand names,
vertical 4:5 layout, minimalist design
```

### 3. Схема процесса (флоу)
```
Diagram flow chart on dark background, connected nodes with arrows,
abstract icons representing process steps, soft gradient line connections,
minimalist technical illustration, vertical 4:5, no labels or text
```

### 4. Концепт-арт продукта
```
Concept art of abstract tech product on dark gradient background,
soft volumetric lighting, modern industrial design aesthetic,
deep purple to blue color palette, vertical 4:5, photorealistic render
```

### 5. Метафорическая визуализация
```
Abstract metaphorical visualization: [метафора - микрофон + волны для аудио,
шестигранник для оценки, нейронная сеть для AI], dark moody background,
glowing accents, minimalist editorial illustration style, vertical 4:5
```

## Цветовая палитра по умолчанию

- Основа: глубокий тёмно-синий / navy (#0a0e27, #1a1f3a)
- Акценты: фиолетовый (#7c3aed), бирюзовый (#06b6d4), мягкий пурпурный (#a855f7)
- Подсветка: тёплый янтарный (#f59e0b) для редких акцентов

## Чего избегать

- Стоковые фото-выглядящие изображения
- Иллюстрации с плоскими градиентами без объёма
- Картинки с очевидным AI-look (искажённые пальцы, странные глаза)
- Яркие пёстрые цвета — выглядят дёшево
- Корпоративный clipart-look
- Тексты-плакаты ("AI revolution", "Future is here") — это палится моментально
