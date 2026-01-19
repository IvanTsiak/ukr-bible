import json
import re
import os
import random
from typing import List, Optional
from .models import Verse
from aliases import BOOK_ALIASES

class Bible:
    def __init__(self):
        """
        Initializes the Bible instance by loading the embedded JSON data.
        
        Raises:
            FileNotFoundError: If the 'ukr_bible_data.json' file is missing.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'ukr_bible_data.json')

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"File doesn't found: {json_path}")

        self.data = self._load_data(json_path)
        self.book_map = self._build_book_map()

    def _load_data(self, path: str) -> dict:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _normalize_name(self, s: str) -> str:
        if not s:
            return ""
        s = s.lower()
        s = s.replace(".", "")
        s = s.replace("’", "'").replace("`", "'").replace("ʼ", "'")
        s = re.sub(r"\s+", " ", s)
        return s.strip()
        
    def _build_book_map(self) -> dict:
        mapping = {}

        for short_name, content in self.data.items():
            norm_short = self._normalize_name(short_name)
            mapping[norm_short] = short_name

            norm_long = self._normalize_name(content['ids']['long_name'])
            mapping[norm_long] = short_name

        for correct_key, aliases in BOOK_ALIASES.items():
            if correct_key in self.data:
                for alias in aliases:
                    norm_alias = self._normalize_name(alias)
                    mapping[norm_alias] = correct_key

        return mapping
    
    def _parse_reference(self, reference: str):
        pattern = r"^(.+?)[\s\.]+(\d+):(\d+)(?:-(\d+))?$"
        match = re.match(pattern, reference.strip())

        if not match:
            return None
        
        raw_book, chapter, v_start, v_end = match.groups()

        clean_book_name = self._normalize_name(raw_book)
        book_key = self.book_map.get(clean_book_name)

        if not book_key:
            return None
        
        start = int(v_start)
        end = int(v_end) if v_end else start

        return book_key, str(chapter), start, end
    
    def get(self, reference: str) -> List[Verse]:
        """
        Retrieves verses based on a reference string.

        Supports standard reference formats including abbreviations and ranges.
        
        Args:
            reference (str): A string citation (e.g., "Мт 5:3", "Матвія 5:3-10").

        Returns:
            List[Verse]: A list of Verse objects found. Returns an empty list 
            if the reference is invalid or not found.

        Example:
            >>> bible.get("Мт 5:3")
            [<Verse Мт 5:3>]
        """
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
                if s_v_num in chapter_data:
                    results.append(Verse(
                        book_short=book_info['short_name'],
                        book_long=book_info['long_name'],
                        chapter=int(chapter),
                        verse=v_num,
                        text=chapter_data[s_v_num]
                    ))

        return results
    
    def search(self, query: str) -> List[Verse]:
        """
        Performs a case-insensitive substring search across the entire Bible.

        Args:
            query (str): The word or phrase to search for.

        Returns:
            List[Verse]: A list of Verse objects containing the query string.
        """
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
        """
        Returns a single random verse from the Bible.

        Returns:
            Verse: A randomly selected Verse object.
        """
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
        """
        Returns a list of all available books in the library.

        Returns:
            List[dict]: A list of dictionaries, where each dictionary contains:
                - 'id' (int): The internal book ID.
                - 'short' (str): Short name (abbreviation).
                - 'long' (str): Full official title.
            The list is sorted by book ID.
        """
        books = []
        for key, content in self.data.items():
            ids = content['ids']
            books.append({
                "id": ids['book_number'],
                "short": ids['short_name'],
                "long": ids['long_name']
            })

        return sorted(books, key=lambda x: x['id'])