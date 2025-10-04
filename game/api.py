import os
import requests

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

    def get_user(self, username):
        return self._get(f"/user/{username}")
