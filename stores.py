# --- Supported online stores (50+) ---
#
# Each entry maps a retailer key to its display name and primary domain.
# These are the stores the nightly indexer crawls and that semantic search
# results are matched against.

STORES = {
    "amazon": {"name": "Amazon", "domain": "amazon.com"},
    "amazon_in": {"name": "Amazon India", "domain": "amazon.in"},
    "flipkart": {"name": "Flipkart", "domain": "flipkart.com"},
    "myntra": {"name": "Myntra", "domain": "myntra.com"},
    "ajio": {"name": "AJIO", "domain": "ajio.com"},
    "zara": {"name": "Zara", "domain": "zara.com"},
    "hm": {"name": "H&M", "domain": "hm.com"},
    "uniqlo": {"name": "Uniqlo", "domain": "uniqlo.com"},
    "asos": {"name": "ASOS", "domain": "asos.com"},
    "shein": {"name": "SHEIN", "domain": "shein.com"},
    "nykaa_fashion": {"name": "Nykaa Fashion", "domain": "nykaafashion.com"},
    "tatacliq": {"name": "Tata CLiQ", "domain": "tatacliq.com"},
    "meesho": {"name": "Meesho", "domain": "meesho.com"},
    "snapdeal": {"name": "Snapdeal", "domain": "snapdeal.com"},
    "nike": {"name": "Nike", "domain": "nike.com"},
    "adidas": {"name": "Adidas", "domain": "adidas.com"},
    "puma": {"name": "Puma", "domain": "puma.com"},
    "reebok": {"name": "Reebok", "domain": "reebok.com"},
    "levis": {"name": "Levi's", "domain": "levi.com"},
    "gap": {"name": "Gap", "domain": "gap.com"},
    "forever21": {"name": "Forever 21", "domain": "forever21.com"},
    "mango": {"name": "Mango", "domain": "mango.com"},
    "bershka": {"name": "Bershka", "domain": "bershka.com"},
    "pullandbear": {"name": "Pull&Bear", "domain": "pullandbear.com"},
    "stradivarius": {"name": "Stradivarius", "domain": "stradivarius.com"},
    "massimodutti": {"name": "Massimo Dutti", "domain": "massimodutti.com"},
    "nordstrom": {"name": "Nordstrom", "domain": "nordstrom.com"},
    "macys": {"name": "Macy's", "domain": "macys.com"},
    "shopbop": {"name": "Shopbop", "domain": "shopbop.com"},
    "revolve": {"name": "Revolve", "domain": "revolve.com"},
    "boohoo": {"name": "Boohoo", "domain": "boohoo.com"},
    "prettylittlething": {"name": "PrettyLittleThing", "domain": "prettylittlething.com"},
    "missguided": {"name": "Missguided", "domain": "missguided.com"},
    "next": {"name": "Next", "domain": "next.co.uk"},
    "riverisland": {"name": "River Island", "domain": "riverisland.com"},
    "topshop": {"name": "Topshop", "domain": "topshop.com"},
    "urbanoutfitters": {"name": "Urban Outfitters", "domain": "urbanoutfitters.com"},
    "anthropologie": {"name": "Anthropologie", "domain": "anthropologie.com"},
    "abercrombie": {"name": "Abercrombie & Fitch", "domain": "abercrombie.com"},
    "hollister": {"name": "Hollister", "domain": "hollisterco.com"},
    "americaneagle": {"name": "American Eagle", "domain": "ae.com"},
    "oldnavy": {"name": "Old Navy", "domain": "oldnavy.com"},
    "bananarepublic": {"name": "Banana Republic", "domain": "bananarepublic.com"},
    "jcrew": {"name": "J.Crew", "domain": "jcrew.com"},
    "uniqlo_uk": {"name": "Uniqlo UK", "domain": "uniqlo.com/uk"},
    "decathlon": {"name": "Decathlon", "domain": "decathlon.com"},
    "lifestylestores": {"name": "Lifestyle", "domain": "lifestylestores.com"},
    "westside": {"name": "Westside", "domain": "westside.com"},
    "biba": {"name": "Biba", "domain": "biba.in"},
    "fabindia": {"name": "FabIndia", "domain": "fabindia.com"},
    "bewakoof": {"name": "Bewakoof", "domain": "bewakoof.com"},
    "thesouledstore": {"name": "The Souled Store", "domain": "thesouledstore.com"},
}


def store_count():
    """Return the number of supported stores."""
    return len(STORES)


def domain_to_store(domain):
    """Return the store name for a domain, or the domain itself if unknown."""
    domain = (domain or "").lower()
    for entry in STORES.values():
        if entry["domain"] in domain:
            return entry["name"]
    return domain


def search_store(store, query, fetcher, timeout=30):
    """
    Search a single retailer for products matching ``query``.

    ``fetcher`` is a callable that takes a URL and returns a requests-like
    Response (so callers can reuse ScraperAPI). Returns a list of candidate
    product dicts tagged with their source store. Failures are swallowed so a
    single broken store never breaks the fan-out.
    """
    from urllib.parse import quote_plus

    from bs4 import BeautifulSoup

    try:
        url = f"https://{store['domain']}/search?q={quote_plus(query)}"
        resp = fetcher(url, timeout=timeout)
        if getattr(resp, "status_code", 0) != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for card in soup.select(".product-card, .product, li.product-item"):
            link = card.find("a", href=True)
            price = card.find(class_="price")
            if not link:
                continue
            name = link.text.strip()
            if len(name) < 3:
                continue
            results.append(
                {
                    "name": name,
                    "url": link["href"],
                    "price": price.text.strip() if price else "N/A",
                    "source": store["name"],
                }
            )
        return results
    except Exception:
        return []


def gather_candidates(query, fetcher, stores=None, max_workers=20, timeout=30):
    """
    Fan out the query across stores in parallel and merge candidates.

    Runs one ``search_store`` per retailer concurrently so total latency is
    close to a single store's, not the sum of all. One store failing does not
    affect the others.
    """
    from concurrent.futures import ThreadPoolExecutor

    targets = list((stores or STORES).values())
    candidates = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(search_store, s, query, fetcher, timeout) for s in targets
        ]
        for fut in futures:
            candidates.extend(fut.result())
    return candidates
