import json
import re
import os
import random
from typing import List, Optional
from .models import Verse

BOOK_ALIASES = {
    "1М": ["1м", "бут", "буття", "перша книга мойсеєва: буття", "перша книга мойсеєва", "книга буття", "1 м", "1 мойсеева", "1-a мойсеєва"],
    "2М": ["2м", "вих", "вихід", "книга вихід", "друга книга мойсеева: вихід", "2 м", "2 мойсеева", "2-а мойсеєва"]
}

class Bible:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'ukr_bible_data.json')

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"File doesn't found: {json_path}")

        self.data = self._load_data(json_path)
        self.book_map = self._build_book_map()

    def _load_data(self, path: str) -> dict:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    def _build_book_map(self) -> dict:
        mapping = {}
        for short_name, content in self.data.items():
            mapping[short_name.lower()] = short_name
            long_name = content['ids']['long_name']
            mapping[long_name.lower()] = short_name

        for correct_key, aliases in BOOK_ALIASES.items():
            if correct_key in self.data:
                for alias in aliases:
                    mapping[alias.lower()] = correct_key
        return mapping
    
    def _parse_reference(self, reference: str):
        pattern = r"^(.+?)\s+(\d+):(\d+)(?:-(\d+))?$"
        match = re.match(pattern, reference.strip())

        if not match:
            return None
        
        raw_book, chapter, v_start, v_end = match.groups()

        book_key = self.book_map.get(raw_book.lower().strip())
        if not book_key:
            return None
        
        start = int(v_start)
        end = int(v_end) if v_end else start

        return book_key, str(chapter), start, end
    
    def get(self, reference: str) -> List[Verse]:
        parsed = self._parse_reference(reference)
        if not parsed:
            return []
        
        book_key, chapter, start, end = parsed
        results = []

        if book_key in self.data and chapter in self.data[book_key]['text']:
            chapter_data = self.data[book_key]['text'][chapter]
            book_info = self.data[book_key]['ids']

            for v_num in range(start, end + 1):
                s_v_num = str(v_num)
                if (s_v_num) in chapter_data:
                    results.append(Verse(
                        book_short=book_info['short_name'],
                        book_long=book_info['long_name'],
                        chapter=int(chapter),
                        verse=v_num,
                        text=chapter_data[s_v_num]
                    ))

        return results
    
    def search(self, query: str) -> List[Verse]:
        query = query.lower()
        results = []

        for book_key, book_content in self.data.items():
            book_info = book_content['ids']

            for chap_key, verses in book_content['text'].items():
                for verse_key, text in verses.items():
                    if query in text.lower():
                        results.append(Verse(
                            book_short=book_info['short_name'],
                            book_long=book_info['long_name'],
                            chapter=int(chap_key),
                            verse=int(verse_key),
                            text=text
                        ))

        return results
    
    def random_verse(self) -> Verse:
        book_keys = list(self.data.keys())
        book_key = random.choice(book_keys)
        book_data = self.data[book_key]

        chapter_keys = list(book_data['text'].keys())
        chapter_key = random.choice(chapter_keys)
        chapter_data = book_data['text'][chapter_key]

        verse_keys = list(chapter_data.keys())
        verse_key = random.choice(verse_keys)
        text = chapter_data[verse_key]

        return Verse(
            book_short=book_data['ids']['short_name'],
            book_long=book_data['ids']['long_name'],
            chapter=int(chapter_key),
            verse=int(verse_key),
            text=text
        )
    
    def list_books(self) -> List[dict]:
        books = []
        for key, content in self.data.items():
            ids = content['ids']
            books.append({
                "id": ids['book_number'],
                "short": ids['short_name'],
                "long": ids['long_name']
            })

        return sorted(books, key=lambda x: x['id'])