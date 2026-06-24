# Fashion Deal Recommender Backend

from flask import Flask, jsonify, request
from flask_cors import CORS
from tinydb import TinyDB

from agent import analyze_product_url
from recommender import rank_by_similarity
from stores import STORES, store_count

app = Flask(__name__)
CORS(app)
db = TinyDB("products.json")  # Store product search history


@app.route("/")
def index():
    return "Fashion Deal Recommender Backend is running."


@app.route("/stores", methods=["GET"])
def get_stores():
    """Return the catalog of supported online stores."""
    return jsonify({"count": store_count(), "stores": list(STORES.values())})


@app.route("/semantic-search", methods=["POST"])
def semantic_search():
    """Rank candidate products by semantic similarity to a text query."""
    data = request.json or {}
    query = data.get("query")
    candidates = data.get("candidates", [])
    if not query:
        return jsonify({"error": "No query provided"}), 400

    top_k = data.get("top_k")
    ranked = rank_by_similarity(query, candidates, text_key="name", top_k=top_k)
    return jsonify({"query": query, "results": ranked})


@app.route("/recent-searches", methods=["GET"])
def get_recent_searches():
    searches = db.all()
    return jsonify({"searches": searches[-10:]})  # Return last 10 searches


@app.route("/save-search", methods=["POST"])
def save_search():
    data = request.json
    if not data or "url" not in data:
        return jsonify({"error": "Invalid request data"}), 400

    search_data = {
        "url": data["url"],
        "timestamp": request.json.get("timestamp"),
        "product_info": request.json.get("product_info", {}),
    }
    db.insert(search_data)
    return jsonify({"message": "Search saved successfully"})


@app.route("/analyze-product", methods=["POST"])
def analyze_product():
    """Analyze a product URL and find similar items with better deals."""
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Analyze the product and find similar items
        result = analyze_product_url(url)

        # Save the search if analysis was successful
        if not result.get("error"):
            search_data = {
                "url": url,
                "timestamp": data.get("timestamp"),
                "product_info": result.get("product_info", {}),
            }
            db.insert(search_data)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/clear-history", methods=["POST"])
def clear_history():
    """Clear the search history."""
    db.truncate()
    return jsonify({"message": "Search history cleared"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
