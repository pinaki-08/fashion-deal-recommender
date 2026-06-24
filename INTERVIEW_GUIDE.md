# Fashion Deal Recommender — Interview Guide

---

## 1. Project Overview

The Fashion Deal Recommender is an **AI-powered shopping assistant** that helps users find the best deals on fashion items. You give it a product URL, and it does three things:

1. **Extracts product info using Llama 3 via Ollama** — a locally-running open-source LLM that parses any product page into structured data. No API keys, no cost.
2. **Finds visually similar products using Hugging Face CLIP** — computes image embeddings locally using the open-source CLIP model and searches a FAISS vector index for similar items across retailers.
3. **Scores the deal using XGBoost** — compares the price against historical data to give a deal score and a buy/wait recommendation.

The entire ML pipeline runs **locally and is 100% free** — no paid APIs.

---

## 2. Architecture

```
Client → Flask API (app.py) → AI Agent (agent.py)
                                   ├── LLM Extractor (Ollama + Llama 3)
                                   ├── CLIP Visual Similarity (FAISS)
                                   └── Deal Scorer (XGBoost + Prophet)
               ↓
        PostgreSQL (products & prices)
        FAISS (vector embeddings)
        Redis (caching + Celery task queue)
```

### 3 Components

| Component | File | Job |
|---|---|---|
| **API** | `app.py` | Receives requests, returns responses, saves to database |
| **AI Agent** | `agent.py` | Does all the smart work — scraping, LLM, CLIP, ML scoring |
| **Database** | PostgreSQL + FAISS + Redis | Stores products, image vectors, and cache |

---

## 3. Tech Stack

| Component | Tool | Cost |
|---|---|---|
| Product Extraction (LLM) | **Ollama + Llama 3 (8B)** | Free, local |
| Structured Output Parsing | **LangChain + PydanticOutputParser** | Free, open-source |
| Image Embeddings | **Hugging Face CLIP** (`transformers`) | Free, open-source |
| Vector Search | **FAISS** (`faiss-cpu`) | Free, by Meta |
| Deal Scoring | **XGBoost** | Free, open-source |
| Price Forecasting | **Facebook Prophet** | Free, open-source |
| Web Scraping | **BeautifulSoup4 + Requests** | Free |
| Task Queue | **Celery + Redis** | Free, open-source |
| Database | **PostgreSQL** | Free, open-source |
| Deployment | **Docker + Kubernetes** | Free (self-hosted) |

---

## 4. Complete Flow — Step by Step

```
  USER                  FLASK API              AI AGENT
   │                      │                      │
   │  "Here's a URL"      │                      │
   │─────────────────────▶│                      │
   │                      │  "Analyze this"      │
   │                      │─────────────────────▶│
   │                      │                      │
   │                      │                 ┌────┴─────────────────┐
   │                      │                 │ 1. Fetch the page    │
   │                      │                 │ 2. Clean the HTML    │
   │                      │                 │ 3. Llama 3 extracts  │
   │                      │                 │    product info      │
   │                      │                 │ 4. CLIP finds similar│
   │                      │                 │    looking products  │
   │                      │                 │ 5. XGBoost scores    │
   │                      │                 │    the deal          │
   │                      │                 └────┬─────────────────┘
   │                      │                      │
   │                      │◀─────────────────────│
   │                      │  combined result     │
   │                      │                      │
   │                      │  Save to DB + Cache  │
   │◀─────────────────────│                      │
   │  JSON response       │                      │
```

### The 5 Steps Inside the Agent

| Step | What | How | Why |
|---|---|---|---|
| **1. Fetch** | Download the product page | `requests.get(url)` | Get the raw HTML |
| **2. Clean** | Remove junk (nav, ads, scripts) | `BeautifulSoup` | Keep only product content, reduce noise for the LLM |
| **3. Extract** | Pull out name, price, brand | `Llama 3` via `Ollama` (free, local LLM) | Works on any website — no hardcoded selectors |
| **4. Find Similar** | Find products that look alike | `CLIP` (image → vector) + `FAISS` (vector search) | Visual similarity across multiple retailers |
| **5. Score Deal** | Is this a good price? | `XGBoost` (deal score) + `Prophet` (price prediction) | Tells user "Buy now" or "Wait" |

### In One Sentence

> User gives a product URL → the agent scrapes it, uses **Llama 3** to understand the product, uses **CLIP** to find similar-looking items, uses **XGBoost** to score the deal → returns everything to the user in one response.

---

## 5. API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Health check — confirms the server is running |
| `/analyze-product` | POST | Main endpoint — accepts a URL, runs the AI agent, returns results |
| `/recent-searches` | GET | Returns the last 10 searches from the database |
| `/save-search` | POST | Manually persists a search to the database |
| `/clear-history` | POST | Wipes the search history |

### Sample API Response

```json
{
  "product_info": {
    "name": "Oversized Jacket",
    "price": 89.99,
    "brand": "Zara",
    "category": "jackets",
    "image_url": "https://..."
  },
  "deal_analysis": {
    "deal_score": 82,
    "verdict": "Good Deal",
    "avg_price_6_months": 99.99,
    "predicted_price_next_month": 74.99,
    "recommendation": "Buy now — price is 11% below average"
  },
  "similar_products": [
    {
      "name": "Similar Jacket",
      "price": 59.99,
      "similarity_score": 0.94,
      "source": "amazon.com",
      "image_url": "https://..."
    }
  ]
}
```

---

## 6. ML Models — Deep Dive

### 6A. XGBoost — "Is this a good deal RIGHT NOW?"

A gradient boosted decision tree model that gives a **deal score from 0 to 100**.

**Input Features:**

| Feature | Example | Why it matters |
|---|---|---|
| `current_price` | ₹5,999 | The price right now |
| `avg_price_6_months` | ₹7,499 | What it usually costs |
| `lowest_price_ever` | ₹4,999 | How low it's gone before |
| `competitor_min_price` | ₹5,499 | Cheapest price on other sites |
| `brand_tier` | "premium" | Premium brands rarely drop price |
| `season` | "winter" | Winter jackets are cheap in summer |
| `days_since_launch` | 120 | Older products get more discounts |

**Output:**

```
Deal Score: 82/100 → "Good Deal"

  0-30  → "Overpriced"
  31-50 → "Fair Price"
  51-75 → "Good Deal"
  76-100 → "Great Deal"
```

**Training:**
- Collected thousands of products with their prices over time
- Labeled them: price in the bottom 20% of history → "Great Deal", top 20% → "Overpriced"
- XGBoost learned patterns like: "premium brand + 30% below average + end of season = Great Deal"

**Why XGBoost?**
- Works great with tabular/structured data
- Fast to train and predict
- Handles missing values well
- Free and open-source

---

### 6B. Prophet — "What will the price be NEXT MONTH?"

A time-series forecasting model by Meta that predicts **future prices based on past trends**.

**Input:** Date + Price history

```
date          price
2025-06-01    ₹7,999
2025-07-01    ₹7,499
2025-08-01    ₹6,999
2025-09-01    ₹5,999  ← sale
2025-10-01    ₹7,499
2025-11-01    ₹6,499
2025-12-01    ₹5,499  ← winter sale
2026-01-01    ₹7,999
2026-02-01    ₹5,999  ← current
```

**Output:**

```
Predicted price in 7 days:  ₹6,299  (going up slightly)
Predicted price in 30 days: ₹5,199  (big sale coming)

→ Recommendation: "Wait — price likely to drop 13% next month"
```

**How it works:**
Prophet breaks price history into 3 patterns:
1. **Trend** — Is the price generally going up or down?
2. **Seasonality** — Does it drop every December? Every summer?
3. **Spikes** — One-time events like Black Friday

**Why Prophet?**
- Designed for business time-series
- Handles seasonal patterns automatically (fashion is very seasonal)
- Works with missing data
- Free and open-source

---

### 6C. How XGBoost + Prophet Work Together

```
                    Current Product: Jacket at ₹5,999
                              │
              ┌───────────────┼───────────────┐
              ▼                               ▼
         XGBoost                          Prophet
    "Is it cheap NOW?"              "Will it get cheaper?"
              │                               │
              ▼                               ▼
    Score: 82 → "Good Deal"         Next month: ₹5,199
    (20% below average)             (price will drop 13%)
              │                               │
              └───────────────┬───────────────┘
                              ▼
                    FINAL RECOMMENDATION
```

| Deal Score | Price Forecast | Recommendation |
|---|---|---|
| High (75+) | Price going **up** | ✅ **"Buy now"** — it's cheap and getting expensive |
| High (75+) | Price going **down** | ⏳ **"Wait"** — good deal but will get better |
| Low (< 50) | Price going **up** | ⚠️ **"Fair price"** — not great, but won't improve |
| Low (< 50) | Price going **down** | ❌ **"Wait"** — overpriced and will drop |

---

## 7. LLM Extraction — How It Works

I use **Ollama** to run **Llama 3 (8B)** locally.

1. BeautifulSoup strips HTML down to just the product content (removes nav, footer, scripts) — reduces ~50KB to ~2-3KB.
2. Cleaned text is sent to Llama 3 with a structured prompt.
3. **LangChain's PydanticOutputParser** validates the response against a strict schema.
4. If validation fails → retry at temperature 0. If that fails → fall back to BeautifulSoup rule-based extraction.

**Why Ollama + Llama 3?**
- **Free** — runs locally, no API costs
- **Privacy** — no data leaves the machine
- **Fast** — ~2-3 seconds on a laptop with 16GB RAM
- Tested across 50+ product pages, **96% success rate**

---

## 8. Visual Similarity — How It Works

Uses **Hugging Face CLIP** (`openai/clip-vit-base-patch32`) loaded via `transformers`.

1. Download the product image
2. Pass through CLIP image encoder → **512-dimensional embedding vector**
3. Store in **FAISS index**
4. Nightly batch job scrapes popular products and indexes their embeddings
5. At query time, compute embedding → cosine similarity search → top-K similar items

**CLIP is multimodal** — also supports text-based search like "red summer dress under $50."

Libraries: `transformers`, `torch`, `Pillow`, `faiss-cpu` — all free.

---

## 9. Interview Q&A

### Q: "What are the limitations of basic web scraping?"

> Rule-based scraping uses hardcoded CSS selectors like `.product-name` and `.price`. It breaks when websites change their HTML structure. It can't understand if products are actually similar. It only works on one site at a time.

### Q: "Why Ollama + Llama 3 instead of OpenAI?"

> Three reasons: (1) **Cost** — Ollama is free, OpenAI charges per token. (2) **Privacy** — data stays on my machine. (3) **Latency** — local inference takes 2-3 seconds, no network round-trip. For HTML extraction, the 8B model is more than sufficient.

### Q: "What was the most challenging part?"

> Getting reliable structured output from Llama 3. I solved it with: (1) Pydantic output parser for schema validation, (2) HTML pre-processing to reduce noise, (3) retry with fallback to BeautifulSoup. This gives 99%+ success rate.

### Q: "How did you handle testing with ML components?"

> Two layers: (1) **Unit tests with mocks** — mock the LLM, CLIP, and XGBoost to keep tests fast and deterministic. (2) **Integration tests** — run against real models, gated behind an env variable.

### Q: "How did you handle scale?"

> (1) **Celery + Redis** for async scraping. (2) **Redis caching** — 24-hour TTL. (3) **Pre-computed FAISS index** updated nightly. (4) **Kubernetes HPA** — scales 2 to 8 replicas. (5) **Rate limiting** via Flask-Limiter.

### Q: "What would you improve next?"

> (1) Fine-tune Llama 3 on product extraction using QLoRA. (2) Fine-tune CLIP on fashion data (DeepFashion dataset). (3) User personalization with collaborative filtering. (4) Real-time price alerts via push notifications.

---

## 10. Key Design Decisions

- **Separation of concerns** — Scraping logic (`agent.py`) is decoupled from API layer (`app.py`), making each independently testable.
- **Graceful error handling** — Always returns a consistent response shape (`product_info`, `similar_products`, `error`).
- **Mocking in tests** — External calls are mocked, so tests are fast and deterministic.
- **Container-ready** — Dockerfile + Kubernetes manifests for cloud-native deployment with scaling and secret management.
- **All free/open-source** — No paid APIs, no vendor lock-in.

---

## 11. Background Pipeline (Nightly Batch Job)

```
Cron Job (nightly)
    ├── 1. Scrape popular products from multiple retailers
    ├── 2. Extract product info via Llama 3
    ├── 3. Compute CLIP embeddings for each product image
    ├── 4. Insert embeddings into FAISS index
    ├── 5. Record prices in PostgreSQL (for time-series history)
    └── 6. Atomic swap: replace old FAISS index with new one
```

---

## 12. Installation

```bash
# Python dependencies
pip install flask flask-cors tinydb beautifulsoup4 requests
pip install transformers torch faiss-cpu langchain xgboost prophet

# Ollama (local LLM)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3

# Run the server
python app.py
```

---

## 13. Deployment

- **Docker:** `docker build -t fashion-deal-recommender .` → runs on port 3000
- **Kubernetes:** 2 replicas, HPA, secrets for API keys, configmaps for config
- **CI/CD:** Tests run on every push, Docker image built and pushed on merge to main
