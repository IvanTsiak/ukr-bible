A lightweight, zero-dependency Python library for interacting with the Ukrainian Bible (Ivan Ohienko / Іван Огієнко translation).
Designed for developers, researchers, and bot creators who need fast, offline access to biblical texts in Ukrainian.

## Features

- **Offline Access:** No API keys or internet connection required. The text is embedded in the library.
- **Smart Parsing:** Understands various book abbreviations (e.g., "Мт", "Матвія", "Євангелія від Матвія").
- **Range Support:** Fetch single verses (`"Ів 3:16"`) or ranges (`"Мт 5:3-10"`).
- **Search:** Case-insensitive substring search across the entire text.
- **Random Verses:** Perfect for "Verse of the Day" features.

## Installation

Install the library via pip:

```bash
pip install ukr-bible
```
## Quick Start

### 1. Fetching Verses
The `get()` method returns a list of `Verse` objects.

```python
from ukr_bible import Bible

bible = Bible()

# Get a single verse
verses = bible.get("Івана 3:16")
for v in verses:
    print(f"{v.book_long} {v.chapter}:{v.verse} — {v.text}")

# Output:
# Євангелія від Івана 3:16 — Бо так полюбив Бог світ, що дав Сина Свого Однородженого...
```
### 2. Fetching a Range
You can request multiple verses at once

```python
# Get the Beatitudes (Matthew 5:3-5)
beatitudes = bible.get("Мт 5:3-5")

for v in beatitudes:
    print(f"[{v.verse}] {v.text}")
```
### 3. Searching
Find verses containing specific words or phrases.

```python
# Search for "світло для світу"
results = bible.search("світло для світу")

print(f"Found {len(results)} matches:")
for v in results:
    print(v)
```
### 4. Random Verse
Get a random verse from the entire Bible.

```python
random_v = bible.random_verse()
print(f"Random wisdom: {random_v.text} ({random_v.book_short} {random_v.chapter}:{random_v.verse})")
```
### Data Structure
The library returns `Verse` objects with the following attributes:

- `book_short` (`str`): Abbreviated book name (e.g., "Мт").
- `book_long` (`str`): Full book name (e.g., "Євангелія від Матвія").
- `chapter` (`int`): Chapter number.
- `verse` (`int`): Verse number.
- `text` (`str`): The text of the verse.