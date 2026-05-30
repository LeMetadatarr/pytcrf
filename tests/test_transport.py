"""Transport configuration + scraper-trap guard (no network)."""
import pytest

from pytcrf import transport as tr


def _clear_env(monkeypatch):
    for suffix in ("TRANSPORT", "FLARESOLVERR_URL", "FLARESOLVERR_TIMEOUT",
                   "WAYBACK_FALLBACK"):
        monkeypatch.delenv(f"PYTCRF_{suffix}", raising=False)
        monkeypatch.delenv(f"UNBLOCK_REQUESTS_{suffix}", raising=False)


def test_mode_from_kwargs(monkeypatch):
    _clear_env(monkeypatch)
    assert tr.Transport()._resolved_mode() == "curl_cffi"
    assert tr.Transport(mode="wayback")._resolved_mode() == "wayback"
    assert tr.Transport(flaresolverr_url="http://x:8191")._resolved_mode() == \
        "flaresolverr"


def test_env_prefix(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("PYTCRF_TRANSPORT", "requests")
    assert tr.Transport()._resolved_mode() == "requests"
    assert tr.Transport(mode="wayback")._resolved_mode() == "wayback"


def test_rejects_bad_mode():
    with pytest.raises(ValueError):
        tr.Transport(mode="nonsense")


def test_session_is_cloudflare_session(monkeypatch):
    _clear_env(monkeypatch)
    from unblock_requests import CloudflareSession
    sess = tr.Transport(mode="requests").session
    assert isinstance(sess, CloudflareSession)
    assert sess.env_prefix == "PYTCRF"


def test_api_referer_and_scraper_trap(monkeypatch):
    """api() sends a self-referencing Referer and rejects the scraper trap."""
    _clear_env(monkeypatch)
    t = tr.Transport(mode="requests", delay=0)

    captured = {}

    class FakeResp:
        def __init__(self, text):
            self.text = text
            self.status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            import json
            return json.loads(self.text)

    class FakeSession:
        def get(self, url, headers=None, timeout=None):
            captured["url"] = url
            captured["referer"] = (headers or {}).get("Referer")
            if "list=allpages" in url:
                return FakeResp('{"x": "invalid response for scrapers ' * 50 + '"}')
            return FakeResp('{"ok": true}')

    t._session = FakeSession()  # type: ignore[assignment]

    out = t.api({"action": "query", "meta": "siteinfo"})
    assert out == {"ok": True}
    # Referer must equal the request URL (clears the interstitial)
    assert captured["referer"] == captured["url"]
    assert "format=json" in captured["url"]

    with pytest.raises(tr.ScraperBlocked):
        t.api({"action": "query", "list": "allpages"})


def test_client_kwargs(monkeypatch):
    _clear_env(monkeypatch)
    import pytcrf
    assert pytcrf.TCRF(wayback=True).transport._resolved_mode() == "wayback"
    c = pytcrf.TCRF(flaresolverr_url="http://localhost:8191")
    assert c.transport._resolved_mode() == "flaresolverr"
