import json
from unittest.mock import MagicMock, patch

import pytest

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Test the index route returns correct message."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Fashion Deal Recommender Backend is running" in response.data


def test_recent_searches_empty(client):
    """Test recent searches route when no searches exist."""
    with patch("app.db") as mock_db:
        mock_db.all.return_value = []
        response = client.get("/recent-searches")
        assert response.status_code == 200
        assert json.loads(response.data) == {"searches": []}


def test_recent_searches_with_data(client):
    """Test recent searches route with mock data."""
    mock_searches = [
        {"url": "http://example.com/product1", "timestamp": "2025-08-03T10:00:00"},
        {"url": "http://example.com/product2", "timestamp": "2025-08-03T11:00:00"},
    ]
    with patch("app.db") as mock_db:
        mock_db.all.return_value = mock_searches
        response = client.get("/recent-searches")
        assert response.status_code == 200
        assert json.loads(response.data) == {"searches": mock_searches}


def test_analyze_product_no_url(client):
    """Test analyze product route without URL."""
    response = client.post("/analyze-product", json={})
    assert response.status_code == 400
    assert json.loads(response.data)["error"] == "No URL provided"


def test_analyze_product_success(client):
    """Test analyze product route with valid URL."""
    test_url = "http://example.com/product"
    mock_result = {
        "product_info": {"name": "Test Product", "price": "99.99", "currency": "USD"},
        "similar_products": [],
    }

    with patch("app.analyze_product_url") as mock_analyze, patch("app.db") as mock_db:
        mock_analyze.return_value = mock_result
        mock_db.insert = MagicMock()

        response = client.post("/analyze-product", json={"url": test_url})

        assert response.status_code == 200
        assert json.loads(response.data) == mock_result
        mock_analyze.assert_called_once_with(test_url)
        mock_db.insert.assert_called_once()


def test_analyze_product_failure(client):
    """Test analyze product route when analysis fails."""
    with patch("app.analyze_product_url") as mock_analyze:
        mock_analyze.side_effect = Exception("Analysis failed")
        response = client.post(
            "/analyze-product", json={"url": "http://example.com/product"}
        )

        assert response.status_code == 500
        assert "Analysis failed" in json.loads(response.data)["error"]


def test_clear_history(client):
    """Test clear history route."""
    with patch("app.db") as mock_db:
        mock_db.truncate = MagicMock()
        response = client.post("/clear-history")

        assert response.status_code == 200
        assert json.loads(response.data)["message"] == "Search history cleared"
        mock_db.truncate.assert_called_once()


def test_stores_route(client):
    """Test the stores catalog route returns 50+ stores."""
    response = client.get("/stores")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["count"] >= 50
    assert len(data["stores"]) == data["count"]


def test_semantic_search_route(client):
    """Test semantic search ranks candidates and requires a query."""
    payload = {
        "query": "running shoes",
        "candidates": [
            {"name": "leather wallet"},
            {"name": "mens running shoes"},
        ],
    }
    response = client.post("/semantic-search", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["results"][0]["name"] == "mens running shoes"


def test_semantic_search_no_query(client):
    response = client.post("/semantic-search", json={"candidates": []})
    assert response.status_code == 400
    assert json.loads(response.data)["error"] == "No query provided"
