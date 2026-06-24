# --- Page Fetching with ScraperAPI support ---

import os

import requests

SCRAPERAPI_ENDPOINT = "https://api.scraperapi.com"


def fetch_page(url, timeout=30):
    """
    Fetch the HTML for a URL.

    If a SCRAPER_API_KEY environment variable is set, the request is routed
    through ScraperAPI (handles rotating proxies, JS rendering and anti-bot
    protection). Otherwise it falls back to a plain ``requests.get`` so the
    project still works locally without any API key.

    Returns the ``requests.Response`` object.
    """
    api_key = os.environ.get("SCRAPER_API_KEY")
    if api_key:
        params = {"api_key": api_key, "url": url}
        return requests.get(SCRAPERAPI_ENDPOINT, params=params, timeout=timeout)
    return requests.get(url, timeout=timeout)
