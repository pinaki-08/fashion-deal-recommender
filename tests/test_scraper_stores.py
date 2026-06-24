import os
from unittest.mock import MagicMock, patch

from scraper import fetch_page
from stores import STORES, domain_to_store, store_count


def test_store_count_at_least_50():
    assert store_count() >= 50
    assert len(STORES) == store_count()


def test_domain_to_store_known():
    assert domain_to_store("www.myntra.com") == "Myntra"
    assert domain_to_store("zara.com") == "Zara"


def test_domain_to_store_unknown_returns_domain():
    assert domain_to_store("unknown-shop.test") == "unknown-shop.test"


def test_fetch_page_without_api_key_uses_plain_request():
    with patch.dict(os.environ, {}, clear=True), patch(
        "scraper.requests.get"
    ) as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        fetch_page("http://example.com/product")
        args, kwargs = mock_get.call_args
        assert args[0] == "http://example.com/product"


def test_fetch_page_with_api_key_uses_scraperapi():
    with patch.dict(os.environ, {"SCRAPER_API_KEY": "secret"}), patch(
        "scraper.requests.get"
    ) as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        fetch_page("http://example.com/product")
        args, kwargs = mock_get.call_args
        assert args[0] == "https://api.scraperapi.com"
        assert kwargs["params"]["api_key"] == "secret"
        assert kwargs["params"]["url"] == "http://example.com/product"
