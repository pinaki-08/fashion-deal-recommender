from unittest.mock import MagicMock, patch

from agent import analyze_product_url


def test_analyze_product_url_valid():
    """Test analyzing a valid product URL."""
    test_url = "http://example.com/product"
    mock_html = """
    <div class="product">
        <h1 class="product-name">Test Product</h1>
        <span class="price">$99.99</span>
        <div class="description">A great product</div>
    </div>
    """

    with patch("scraper.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = analyze_product_url(test_url)

        assert result["product_info"]["name"] == "Test Product"
        assert result["product_info"]["price"] == "$99.99"
        assert "similar_products" in result
        mock_get.assert_called_once()


def test_analyze_product_url_invalid():
    """Test analyzing an invalid product URL."""
    test_url = "http://example.com/nonexistent"

    with patch("scraper.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = analyze_product_url(test_url)

        assert "error" in result
        assert result["error"] == "Failed to fetch product page"


def test_analyze_product_url_parsing_error():
    """Test handling parsing errors in product analysis."""
    test_url = "http://example.com/product"
    mock_html = "<div>Invalid product page</div>"

    with patch("scraper.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = analyze_product_url(test_url)

        assert "error" in result
        assert "Failed to parse product information" in result["error"]


def test_analyze_product_url_network_error():
    """Test handling network errors in product analysis."""
    test_url = "http://example.com/product"

    with patch("scraper.requests.get") as mock_get:
        mock_get.side_effect = Exception("Network error")

        result = analyze_product_url(test_url)

        assert "error" in result
        assert "Failed to fetch product page" in result["error"]


def test_analyze_product_url_with_similar_products():
    """Test analyzing a product URL with similar products."""
    test_url = "http://example.com/product"
    mock_html = """
    <div class="product">
        <h1 class="product-name">Test Product</h1>
        <span class="price">$99.99</span>
        <div class="similar-products">
            <div class="product">
                <a href="/product1">Similar Product 1</a>
                <span class="price">$89.99</span>
            </div>
            <div class="product">
                <a href="/product2">Similar Product 2</a>
                <span class="price">$79.99</span>
            </div>
        </div>
    </div>
    """

    with patch("scraper.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = analyze_product_url(test_url)

        assert len(result["similar_products"]) == 2
        assert "name" in result["similar_products"][0]
        assert "url" in result["similar_products"][0]
        assert "similarity_score" in result["similar_products"][0]
