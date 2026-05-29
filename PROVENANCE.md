# Provenance

## Source

Data is read from [tcrf.net](https://tcrf.net) — **The Cutting Room Floor**, a
MediaWiki documenting the unused, cut, regional and debug content of individual
video games.

pytcrf reads **structured wiki metadata only** through the MediaWiki API: page
titles, category membership, section structure, and rendered section text. It
does not download, host, or redistribute ROMs, game assets, or any media files.

## Licensing

TCRF content is contributed by its community and released under the
**Creative Commons Attribution-ShareAlike (CC BY-SA)** terms stated on the site.
Any dataset derived with this tool inherits those terms:

- **Attribution** — credit The Cutting Room Floor and link back to the source
  page (every record carries a canonical `tcrf_title` and `url`).
- **ShareAlike** — redistribute derivatives under compatible terms.

## Polite scraping

- Default 1.0 s delay between API calls (`Transport(delay=…)` / `TCRF(delay=…)`).
- A browser-class transport via `unblock_requests` (curl_cffi TLS impersonation);
  no headed browser, no Selenium/nodriver.
- Enumeration is seeded from the `Category:Games` tree, not blind crawling, and
  never uses the `list=allpages` module the site traps for scrapers.
- Every API request carries the self-referencing `Referer` header the site asks
  for to clear its bot interstitial — pytcrf behaves like a user clicking
  "continue", not like a header-stripping crawler.

Respect `robots.txt` and the site's terms. This client is intended for
legitimate game-preservation, metadata and dataset work, not bulk mirroring.
