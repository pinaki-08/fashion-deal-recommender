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
