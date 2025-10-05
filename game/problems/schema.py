from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Problem:
    id: str
    slug: str
    title: str
    difficulty: str              # "Easy" | "Medium" | "Hard"
    tags: List[str]
    url: str
    text: str                    # full problem statement
    snippets: List[str]          # ordered canonical snippet lines