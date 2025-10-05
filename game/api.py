import os
import re
import html
import requests

try:
    from bs4 import BeautifulSoup
    _HAS_BS4 = True
except Exception:
    _HAS_BS4 = False

_TAG_RE = re.compile(r"<[^>]+>")

def _strip_html(s: str) -> str:
    if not s:
        return ""
    if _HAS_BS4:
        return BeautifulSoup(s, "html.parser").get_text("\n")
    # fallback: crude but dependency-free
    return html.unescape(_TAG_RE.sub("", s))

def _norm_tags(tags):
    out = []
    for t in tags or []:
        if isinstance(t, dict):
            out.append(t.get("name") or t.get("slug") or t.get("topicName") or "")
        else:
            out.append(str(t))
    return [x for x in out if x]

class LCClient:
    def __init__(self, base=None, timeout=8):
        self.base = base or os.getenv("LC_API", "http://localhost:8000")
        self.timeout = timeout

    def _get(self, path):
        url = f"{self.base.rstrip('/')}/{path.lstrip('/')}"
        r = requests.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def get_daily(self):
        return self._get("/daily")

    def get_problem(self, slug_or_id):
        return self._get(f"/problem/{slug_or_id}")

    def problem_meta(self, slug_or_id):
        """Return compact problem metadata (with optional plain-text 'text' if present)."""
        p = self.get_problem(slug_or_id)
        slug = p.get("titleSlug") or p.get("slug") or str(slug_or_id)
        meta = {
            "id": p.get("frontendQuestionId") or p.get("id"),
            "slug": slug,
            "title": p.get("title") or p.get("questionTitle"),
            "difficulty": p.get("difficulty"),
            "tags": _norm_tags(p.get("topicTags") or p.get("tags")),
            "url": f"https://leetcode.com/problems/{slug}/",
            "paidOnly": bool(p.get("paidOnly", False)),
            "hasEditorial": bool(p.get("hasEditorial", False)),
        }
        content = p.get("content") or p.get("translatedContent") or ""
        if content:
            meta["text"] = _strip_html(content)
        return meta