"""HTTP transport for The Cutting Room Floor (``tcrf.net``).

pytcrf talks to a single surface: the **MediaWiki JSON API** at
``https://tcrf.net/api.php`` (``action=query`` / ``action=parse``). It is a
clean JSON endpoint — but the wiki sits behind two layers of anti-bot defence:

1. A **referer interstitial**. Any request without a ``Referer`` header that
   points back at the page being requested is answered with a small "Request
   Interrupted / verify you aren't an automated bot" HTML page (HTTP 403). The
   site itself spells out the fix: the page is reachable when the request
   carries a referer. This transport sends a self-referencing ``Referer`` header
   (equal to the request URL) on every call, which is exactly what a browser
   sends when a user clicks the "continue" link.
2. A **per-module scraper trap**. A few enumeration modules (notably
   ``list=allpages``) answer a multi-megabyte ``"invalid response for
   scrapers"`` garbage payload at HTTP 200. pytcrf never uses those modules —
   enumeration goes through ``list=categorymembers`` (the ``Category:Games``
   tree), which is served normally. :meth:`Transport.api` defensively rejects a
   scraper-trap body so a blocked module fails loudly instead of buffering tens
   of megabytes.

Everything is routed through the org transport
:class:`unblock_requests.CloudflareSession` — a drop-in ``requests.Session``
subclass with curl_cffi TLS impersonation, a FlareSolverr proxy, and a Wayback
fallback. Transport is configurable via **constructor kwargs** or **environment
variables** (prefix ``PYTCRF_``); explicit kwargs win.

Modes (passed straight to ``CloudflareSession``):

- ``curl_cffi`` *(default)* — live fetch with Chrome/Firefox TLS impersonation
  when the ``stealth`` extra is installed, else plain ``requests``;
- ``requests`` — live fetch with plain ``requests``;
- ``wayback`` — fetch the latest Internet Archive snapshot;
- ``flaresolverr`` — fetch through a FlareSolverr proxy.

Environment fallbacks: ``PYTCRF_TRANSPORT``, ``PYTCRF_FLARESOLVERR_URL``,
``PYTCRF_FLARESOLVERR_TIMEOUT`` (ms), ``PYTCRF_WAYBACK_FALLBACK``.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from unblock_requests import CloudflareSession

BASE = "https://tcrf.net"
API_ENDPOINT = "https://tcrf.net/api.php"
ENV_PREFIX = "PYTCRF"

_VALID_MODES = {"requests", "curl_cffi", "wayback", "flaresolverr"}

# Marker the wiki injects when it decides a request is a scraper. The body is a
# valid-looking JSON envelope whose values are this phrase repeated for tens of
# megabytes; spotting it in the first slice avoids buffering the whole thing.
_SCRAPER_TRAP = "invalid response for scrapers"


class ScraperBlocked(RuntimeError):
    """Raised when tcrf.net serves its anti-scraper trap payload for a module."""


class Transport:
    """Resolves *how* tcrf.net is fetched, from explicit kwargs with environment
    fallbacks. Wraps a single :class:`CloudflareSession` and a polite delay.

    Args:
        mode:                 ``"requests"`` / ``"curl_cffi"`` / ``"wayback"`` /
                              ``"flaresolverr"``. ``None`` → resolve from the
                              environment, then auto.
        flaresolverr_url:     FlareSolverr base URL; setting this alone selects
                              the ``flaresolverr`` mode.
        flaresolverr_timeout_ms: per-request solve budget.
        wayback_fallback:     fall back to the Wayback Machine on a live failure.
        delay:                minimum seconds between API calls (politeness).

    Example::

        from pytcrf import Transport
        t = Transport(delay=1.5)
        data = t.api({"action": "query", "meta": "siteinfo"})
    """

    def __init__(self, *, mode: Optional[str] = None,
                 flaresolverr_url: Optional[str] = None,
                 flaresolverr_timeout_ms: Optional[int] = None,
                 wayback_fallback: Optional[bool] = None,
                 delay: float = 1.0) -> None:
        if mode is not None and mode.lower() not in _VALID_MODES:
            raise ValueError(
                f"mode must be one of {sorted(_VALID_MODES)} or None, got {mode!r}")
        self.mode = mode.lower() if mode else None
        self.flaresolverr_url = flaresolverr_url
        self.flaresolverr_timeout_ms = flaresolverr_timeout_ms
        self.wayback_fallback = wayback_fallback
        self.delay = max(0.0, delay)
        self._session: Optional[CloudflareSession] = None
        self._last_request: float = 0.0

    # -- session ----------------------------------------------------------

    @property
    def session(self) -> CloudflareSession:
        """The shared, lazily-built :class:`CloudflareSession`."""
        if self._session is None:
            self._session = CloudflareSession(
                mode=self.mode,
                flaresolverr_url=self.flaresolverr_url,
                flaresolverr_timeout_ms=self.flaresolverr_timeout_ms,
                wayback_fallback=self.wayback_fallback,
                env_prefix=ENV_PREFIX,
            )
        return self._session

    def _resolved_mode(self) -> str:
        """The transport mode that will actually be used (for introspection)."""
        return self.session._resolved_mode()

    def _throttle(self) -> None:
        if not self.delay:
            return
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request = time.time()

    # -- fetch ------------------------------------------------------------

    def api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call the MediaWiki API and return the parsed JSON.

        ``format=json`` is added automatically. A self-referencing ``Referer``
        header is sent to clear the wiki's interstitial. The body is checked for
        the scraper-trap marker before being parsed as JSON.

        Raises:
            ScraperBlocked: the wiki served its anti-scraper payload (the module
                used is trapped — switch to a ``categorymembers``-based path).
        """
        self._throttle()
        query = {k: v for k, v in params.items() if v is not None}
        query.setdefault("format", "json")
        url = f"{API_ENDPOINT}?{urlencode(query)}"
        r = self.session.get(url, headers={"Referer": url}, timeout=60)
        r.raise_for_status()
        head = r.text[:512]
        if _SCRAPER_TRAP in head:
            raise ScraperBlocked(
                f"tcrf.net served the anti-scraper trap for params={params!r}; "
                "this API module is blocked — enumerate via Category:Games instead")
        return r.json()

    def get_html(self, path: str, **kwargs: Any) -> str:
        """GET ``{BASE}{path}`` (or an absolute URL) and return the HTML."""
        self._throttle()
        url = path if path.startswith("http") else f"{BASE}{path}"
        r = self.session.get(url, headers={"Referer": url}, timeout=60, **kwargs)
        r.raise_for_status()
        return r.text


_DEFAULT_TRANSPORT: Optional[Transport] = None


def default_transport() -> Transport:
    """Return the shared, environment-driven :class:`Transport`."""
    global _DEFAULT_TRANSPORT
    if _DEFAULT_TRANSPORT is None:
        _DEFAULT_TRANSPORT = Transport()
    return _DEFAULT_TRANSPORT
