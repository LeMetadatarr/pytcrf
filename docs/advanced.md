# Transport, the interstitial, and the scraper trap

pytcrf talks to one surface: the TCRF MediaWiki JSON API at
`https://tcrf.net/api.php`. Two documented site behaviors need handling.

## 1. The referer interstitial

A request to `api.php` with no `Referer` header pointing at the requested
page gets an HTTP 403 with a small HTML page:

> Request Interrupted — Please click below to verify you aren't an automated
> bot. If you continue to see this error, you may have a browser or extension
> that is blocking referrer headers.

The site names the cause itself: a missing referer. The "continue" link
points back at the same URL, so a real browser re-requests the page with a
referer equal to that URL. pytcrf reproduces exactly this: every
`Transport.api` call sends `Referer: <the request url>`. This needs no
cookie or JavaScript solving.

## 2. The `allpages` scraper trap

`list=allpages` does not return an error. It returns a valid-looking JSON
envelope whose values are the string `"invalid response for scrapers"`,
repeated for tens of megabytes (HTTP 200). Loading this with `json.loads`
buffers the whole payload, then fails deep inside the parser.

pytcrf never calls trapped modules. It enumerates through
`list=categorymembers` (the `Category:Games` tree, see
[categories.md](categories.md)), which the wiki serves normally. As a safety
net, `Transport.api` inspects the first slice of every response and raises
`ScraperBlocked` if it sees the trap marker, so a blocked module fails fast
instead of allocating gigabytes.

```python
import pytcrf
from pytcrf import Transport
from pytcrf.transport import ScraperBlocked

t = Transport()
try:
    t.api({"action": "query", "list": "allpages", "apnamespace": "0"})
except ScraperBlocked:
    pass   # expected — use Category enumeration instead
```

## Transport modes

Everything routes through `unblock_requests.CloudflareSession`. Select a mode
with a constructor keyword argument or an environment variable (`PYTCRF_`
prefix). An explicit keyword argument wins.

| Mode | Behavior |
|---|---|
| `curl_cffi` *(default)* | live fetch with Chrome/Firefox TLS impersonation (needs the `stealth` extra), else plain `requests` |
| `requests` | live fetch with plain `requests` |
| `wayback` | latest Internet Archive snapshot |
| `flaresolverr` | fetch through a FlareSolverr proxy |

```python
from pytcrf import Transport, TCRF

Transport(mode="wayback")                              # force the archive
Transport(flaresolverr_url="http://localhost:8191")  # via FlareSolverr
client = TCRF(delay=2.0)                               # 2 s between calls
```

### Environment fallbacks

| Variable | Meaning |
|---|---|
| `PYTCRF_TRANSPORT` | `requests` / `curl_cffi` / `wayback` / `flaresolverr` |
| `PYTCRF_FLARESOLVERR_URL` | FlareSolverr base URL (selects that mode) |
| `PYTCRF_FLARESOLVERR_TIMEOUT` | per-request solve budget (ms) |
| `PYTCRF_WAYBACK_FALLBACK` | fall back to the archive on a live failure |

## Politeness

`Transport(delay=…)` (default 10.0 s) enforces a minimum gap between API
calls. A section-text corpus build makes one call per section per page, so
keep the delay up and treat a full crawl as a homelab job. See
[PROVENANCE.md](../PROVENANCE.md).

---
[← The Category:Games tree](categories.md) · [Home](../README.md) · [Datasets and ML planning →](dataset.md)
