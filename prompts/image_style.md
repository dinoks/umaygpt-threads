# Визуальный стиль картинок к постам

Этот файл — референс для написания image_prompt. Используется Claude когда
он генерит image_prompt для нового поста. Цель: картинка должна показывать
СУТЬ РЕЗУЛЬТАТА работы, а не быть абстрактным символом.

## Главный принцип

**Снимай результат как продукт, а не идею через метафору.**

Если пост про дашборд — покажи реальный экран дашборда (или его натурный мокап
на ноутбуке/телефоне). Если про call-аналитику — покажи интерфейс с волной
звука и метриками. Если про премиум-товары — покажи коробку как из product
photography. Не лепи "поток данных в виде цветных линий" или "микрофон
переходящий в график". Это AI-stock.

Картинка должна отвечать на вопрос «что у Султана на экране сейчас стоит»,
а не «что бы могло быть метафорой темы».

## Базовый формат

- **Vertical 4:5** (1080×1350) для основного формата
- **Реалистичный 3D render или photoreal product shot** — не "illustration", не "concept art"
- **Глубина кадра** — главный объект в фокусе, фон с soft bokeh / depth of field
- **Рим-свет** (rim light) и мягкие тени — даёт объём и кинематографичность
- **Один герой кадра** — не пять объектов в композиции. Один главный, остальное контекст

## Что должно быть в любом промпте

Стандартный технический хвост (вшит в gemini_client.py — повторять в prompt не надо):

```
photoreal 3D render, octane / cinema 4d quality, cinematic lighting, rim light,
soft directional shadows, depth of field, shallow focus, vertical 4:5
composition, product photography aesthetic
```

В сам prompt пиши **что снимаем + материалы + освещение + палитра + сцена**.

## Шаблоны по типам постов

### A. Пост про софт / интерфейс / дашборд / приложение
Снимаем экран продукта в реалистичном контексте, не абстракцию.

```
Photoreal product shot: matte black 14-inch laptop angled three-quarter view on
a dark walnut desk, screen displays a clean dark-mode dashboard with crisp data
visualizations (bar charts, line graphs, KPI tiles in teal and warm white,
sample numbers blurred). Single warm lamp from upper-left, rim light catches
laptop edge, soft shadow on desk. Background: blurred home office with deep
indigo wall, out of focus. Vertical 4:5.
```

Альтернатива — экран телефона в руке (но без лица), либо плавающий экран без
устройства (как Apple keynote slide), без логотипа на корпусе.

### B. Пост про физический продукт / коробку / товар
Чистый product shot как у premium бренда.

```
Photoreal product photography: single matte champagne-gold gift box sitting on
brushed concrete surface, soft satin ribbon catching light, fine paper texture
visible. Hard rim light from back-left creating sharp highlight, soft fill from
front. Background gradient from deep charcoal at top to warm umber at bottom,
shallow depth of field. Editorial commercial style, vertical 4:5.
```

### C. Пост про процесс / систему / автоматизацию
Покажи рабочее место или артефакт работы, не "блок-схему со стрелками".

```
Photoreal overhead shot of a developer workspace: matte mechanical keyboard,
open notebook with handwritten flow diagram (lines abstract, not readable),
small coffee cup with steam, smartphone face-down showing a single notification
glow. Warm desk lamp light from top-right, deep amber and teal accents.
Shallow focus on notebook. Vertical 4:5.
```

### D. Пост-рассуждение / без конкретного объекта
Если объекта нет — снимай ATMOSFERA не символ.

```
Photoreal cinematic still: dimly lit home office at night, single laptop screen
glowing teal in foreground (content not readable, just light), window with city
lights bokeh in background. Mood: focused late-night work. No people in frame.
Vertical 4:5, shallow depth of field, anamorphic feel.
```

## Палитра — выбирается под тему, не всегда navy+teal

| Тема | Палитра |
|---|---|
| Аналитика, технари, продукт | глубокий navy + teal + warm white, акцент янтарь |
| Премиум-товары, lifestyle | champagne gold + charcoal + soft cream |
| AI / автоматизация / код | dark slate + electric cyan + magenta highlights |
| Колл-центр / коммуникации | warm amber + deep brown + cream |
| Маркетинг / реклама / креатив | sunset orange + plum + ivory |
| Стратегические рассуждения | monochrome dark with one warm accent |

Никогда не "rainbow gradient" — палитра 3 цвета максимум.

## Анти-AI-stock чек-лист

Промпт НЕ должен содержать:

- ❌ "abstract geometric shapes" / "abstract data flow"
- ❌ "lines connecting nodes" / "network visualization"
- ❌ "magical glow" / "futuristic interface"
- ❌ "X transforms into Y" (микрофон в волны, мозг в схему)
- ❌ "holographic" / "neon cyberpunk"
- ❌ "minimalist illustration" (просим РЕНДЕР, не иллюстрацию)
- ❌ "soft gradient background" без детали что именно
- ❌ Стрелки, мозги с лампочкой, рукопожатия, глобус с линиями
- ❌ Слово "creative" / "innovative" / "modern" без конкретики

Промпт ДОЛЖЕН содержать:

- ✅ Конкретный главный объект ("matte black 14-inch laptop" а не "device")
- ✅ Материалы ("brushed aluminum", "satin paper", "matte ceramic", "frosted glass")
- ✅ Конкретное освещение ("warm key light from upper-left, cool rim from back-right")
- ✅ Поверхность / сцена ("dark walnut desk", "brushed concrete", "white marble")
- ✅ Глубину кадра ("shallow depth of field", "background blurred")
- ✅ Палитру 3 цветов с конкретными значениями
- ✅ Vertical 4:5 composition

## Правило «вообрази обложку Wired»

Спроси себя: «эта картинка могла бы быть на обложке Wired / Monocle / Apple
keynote?» Если ответ «нет, это похоже на превью к статье Forbes про AI» —
переписывай. Целишься в editorial product photography, не в иллюстративный
сток.

## Когда лучше реальный скриншот вместо генерации

Если пост про конкретный интерфейс который у тебя реально работает —
прикрепи скриншот вместо генерации. Это всегда сильнее любого 3D-рендера.
Скрин показывает что продукт реальный. Пример: пост про шестигранник
использует реальный скриншот UI, не сгенерённую картинку.
