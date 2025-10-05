from __future__ import annotations
from typing import Dict, List
import random

BANK: List[Dict] = [
    {
        "prompt": "What is the average-case time complexity of quicksort?",
        "options": [
            {"text": "O(n log n)", "correct": True},
            {"text": "O(n^2)", "correct": False},
            {"text": "O(n)", "correct": False},
            {"text": "O(log n)", "correct": False},
        ],
    },
    {
        "prompt": "What is the lookup time complexity of a hash map (average case)?",
        "options": [
            {"text": "O(1)", "correct": True},
            {"text": "O(log n)", "correct": False},
            {"text": "O(n)", "correct": False},
            {"text": "O(n log n)", "correct": False},
        ],
    },
    {
        "prompt": "What is the time complexity of inserting into a binary search tree (average case)?",
        "options": [
            {"text": "O(log n)", "correct": True},
            {"text": "O(n)", "correct": False},
            {"text": "O(1)", "correct": False},
            {"text": "O(n log n)", "correct": False},
        ],
    },
    {
        "prompt": "What is the time complexity of merge sort?",
        "options": [
            {"text": "O(n log n)", "correct": True},
            {"text": "O(n)", "correct": False},
            {"text": "O(n^2)", "correct": False},
            {"text": "O(log n)", "correct": False},
        ],
    },
    {
        "prompt": "What is the worst-case time complexity of accessing an element in an array?",
        "options": [
            {"text": "O(1)", "correct": True},
            {"text": "O(n)", "correct": False},
            {"text": "O(log n)", "correct": False},
            {"text": "O(n log n)", "correct": False},
        ],
    },
]

def random_question(shuffle: bool = True) -> Dict:
    """Return a dict with 'prompt' and 'options'. Options are copied (and shuffled if asked)."""
    q = random.choice(BANK)
    options = [dict(opt) for opt in q["options"]]
    if shuffle:
        random.shuffle(options)
    return {"prompt": q["prompt"], "options": options}
