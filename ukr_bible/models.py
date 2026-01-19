from dataclasses import dataclass, asdict

@dataclass
class Verse:
    book_short: str
    book_long: str
    chapter: int
    verse: int
    text: str

    def to_dict(self):
        return asdict(self)
    
    def __repr__(self):
        return f"<Verse {self.book_short} {self.chapter}:{self.verse}>"
    
    def __str__(self):
        return f"[{self.book_short} {self.chapter}:{self.verse}] {self.text}"