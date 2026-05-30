"""Configure the transport: stealth, FlareSolverr, Wayback, custom delay.

    python examples/08_transport_modes.py
"""
import pytcrf
from pytcrf import TCRF, Transport
from pytcrf.transport import ScraperBlocked


def main() -> None:
    # default: curl_cffi TLS impersonation (needs the `stealth` extra)
    print("default mode:", Transport()._resolved_mode())

    # a polite shared client (1.5 s between API calls)
    client = TCRF(delay=1.5)
    print("client mode:", client.transport._resolved_mode())

    # archive-only (no live requests)
    print("wayback mode:", Transport(mode="wayback")._resolved_mode())

    # via a FlareSolverr proxy
    print("flaresolverr mode:",
          Transport(flaresolverr_url="http://localhost:8191")._resolved_mode())

    # the scraper-trap guard in action (no real network needed to explain it)
    print("\nlist=allpages is trapped by tcrf.net; pytcrf raises ScraperBlocked")
    print("and enumerates via the Category:Games tree instead — see docs/advanced.md")
    _ = (ScraperBlocked, pytcrf.list_platforms)


if __name__ == "__main__":
    main()
