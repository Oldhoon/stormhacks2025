# game/api.py
import os
import re
import html
import requests

# Optional: if you install bs4, we'll use it for nicer HTML->text
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
    # handle ["dp","graph"] or [{"name":"Dynamic Programming"}, ...]
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

    # --- your original raw endpoints (keep these) ---
    def get_daily(self):
        return self._get("/daily")

    def get_problem(self, slug_or_id):
        return self._get(f"/problem/{slug_or_id}")

    def get_user(self, username):
        return self._get(f"/user/{username}")

    # --- parsed/normalized helpers (new) ---
    def daily_meta(self):
        """Return a compact daily challenge object:
        {date, id, slug, title, difficulty, tags, url, paidOnly}"""
        raw = self.get_daily()
        prob = (
            raw.get("problem")
            or raw.get("question")
            or raw.get("data", {}).get("problem")
            or raw.get("questionData")
            or {}
        )
        slug = prob.get("titleSlug") or prob.get("slug") or ""
        return {
            "date": raw.get("date"),
            "id": prob.get("frontendQuestionId") or prob.get("id"),
            "slug": slug,
            "title": prob.get("title") or prob.get("questionTitle"),
            "difficulty": prob.get("difficulty"),
            "tags": _norm_tags(prob.get("topicTags") or prob.get("tags")),
            "url": f"https://leetcode.com/problems/{slug}/" if slug else None,
            "paidOnly": bool(prob.get("paidOnly")),
        }

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

    def user_stats(self, username):
        """Return user totals in a stable shape: {username, solvedTotal, byDifficulty, recentSubmissions[]}"""
        u = self.get_user(username)
        by = u.get("byDifficulty") or {}
        return {
            "username": u.get("username") or username,
            "solvedTotal": (
                u.get("solvedTotal")
                or u.get("submitStats", {}).get("acSubmissionNumTotal")
                or sum(int(n.get("count", 0)) for n in u.get("submitStats", {}).get("acSubmissionNum", []))
                or None
            ),
            "byDifficulty": {
                "easy": u.get("easySolved") or by.get("easy", 0),
                "medium": u.get("mediumSolved") or by.get("medium", 0),
                "hard": u.get("hardSolved") or by.get("hard", 0),
            },
            "recentSubmissions": [
                {
                    "id": s.get("id") or s.get("submissionId") or "",
                    "slug": s.get("slug") or s.get("titleSlug") or "",
                    "status": s.get("status") or s.get("statusDisplay") or "",
                    "language": s.get("lang") or s.get("language") or "",
                    "submittedAt": s.get("timestamp") or s.get("time") or "",
                }
                for s in u.get("recentSubmissions", [])
            ],
        }
