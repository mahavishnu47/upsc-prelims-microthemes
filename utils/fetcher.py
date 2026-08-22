import hashlib
import time
import requests
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

class Fetcher:
    def __init__(self, use_cache=True, delay=0.1):
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.use_cache = use_cache
        self.delay = delay

    def _get_cache_path(self, url: str) -> Path:
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
        # Clean slug representation for easy inspection
        slug = url.split("?")[0].rstrip("/").split("/")[-1]
        slug = "".join(c if c.isalnum() or c in "-_" else "_" for c in slug)[:40]
        return CACHE_DIR / f"{slug}_{url_hash}.html"

    def get(self, url: str, max_retries: int = 4, timeout: int = 15) -> str:
        cache_path = self._get_cache_path(url)
        if self.use_cache and cache_path.exists():
            try:
                content = cache_path.read_text(encoding="utf-8")
                if content and len(content) > 200:
                    return content
            except Exception:
                pass

        for attempt in range(1, max_retries + 1):
            try:
                if self.delay > 0:
                    time.sleep(self.delay)
                response = self.session.get(url, timeout=timeout)
                if response.status_code == 200:
                    text = response.text
                    if self.use_cache and text:
                        try:
                            cache_path.write_text(text, encoding="utf-8")
                        except Exception:
                            pass
                    return text
                elif response.status_code == 404:
                    return ""
                else:
                    time.sleep(attempt * 0.5)
            except Exception as e:
                if attempt == max_retries:
                    print(f"[Fetcher] Error fetching {url}: {e}")
                    return ""
                time.sleep(attempt * 0.7)
        return ""
