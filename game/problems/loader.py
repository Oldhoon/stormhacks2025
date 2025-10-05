import os, random, glob, yaml
from typing import Dict, List, Optional
from .schema import Problem

_BANK_DIR = os.path.join(os.path.dirname(__file__), "bank")

def _load_file(path: str) -> Problem:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Problem(
        id=str(data["id"]),
        slug=data["slug"],
        title=data["title"],
        difficulty=data["difficulty"],
        tags=list(data.get("tags", [])),
        url=data.get("url", ""),
        text=data.get("text", "").rstrip(),
        snippets=list(data.get("snippets", [])),
    )

def load_all() -> List[Problem]:
    problems = []
    for p in glob.glob(os.path.join(_BANK_DIR, "*.yaml")):
        problems.append(_load_file(p))
    return problems

def by_slug() -> Dict[str, Problem]:
    return {p.slug: p for p in load_all()}

def get(slug: str) -> Optional[Problem]:
    return by_slug().get(slug)

def random_problem(difficulty: Optional[str] = None) -> Problem:
    all_problems = load_all()
    if difficulty:
        filtered = [p for p in all_problems if p.difficulty.lower() == difficulty.lower()]
        if filtered:
            all_problems = filtered
    return random.choice(all_problems)

def random_other(current_slug: str, difficulty: Optional[str] = None) -> Problem:
    candidates = [p for p in load_all() if p.slug != current_slug]
    if difficulty:
        candidates = [p for p in candidates if p.difficulty.lower() == difficulty.lower()] or candidates
    return random.choice(candidates) if candidates else get(current_slug)