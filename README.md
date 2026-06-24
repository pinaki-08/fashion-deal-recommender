# Fashion Deal Recommender

A smart shopping assistant that helps users find the best deals on fashion items. This application allows users to input product URLs and finds similar items at better prices through web scraping technology.

## Features

- Product URL analysis and information extraction
- Automated web scraping for fashion products (ScraperAPI-backed)
- Semantic similarity recommendations across 50+ online stores
- Price comparisons and deal finding
- Clean and intuitive mobile interface

## Tech Stack

### Backend
- Python + Flask for the REST API
- BeautifulSoup4 for web scraping
- ScraperAPI integration for reliable data collection
- sentence-transformers for semantic similarity (with offline fallback)

### ML / Recommendations
- Semantic ranking of candidate products via sentence embeddings
  (`all-MiniLM-L6-v2`), with a deterministic bag-of-words cosine fallback
  so the service runs anywhere, even without the ML extras installed.
- Catalog of 50+ supported retailers (see `stores.py`).

### Frontend
- React Native/Expo mobile app
- Modern UI components
- Cross-platform compatibility

### CI/CD & Deployment
- GitHub Actions pipeline (`.github/workflows/ci.yml`): lint, test, then
  build and push the Docker image on merge to `main`.
- Kubernetes manifests under `k8s/` for deployment to AWS EKS.

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Health check |
| `/analyze-product` | POST | Analyze a product URL, return semantically ranked similar items |
| `/semantic-search` | POST | Rank candidate products by semantic similarity to a query |
| `/stores` | GET | List supported online stores (50+) |
| `/recent-searches` | GET | Last 10 searches |
| `/save-search` | POST | Persist a search |
| `/clear-history` | POST | Clear search history |

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js and npm
- ScraperAPI account and API key

### Project Setup

1. Set up both backend and frontend in one command:
```bash
make setup
```

Or set up components individually:

### Backend Setup

1. Install Python dependencies:
```bash
make install
```

2. Configure ScraperAPI:
```bash
export SCRAPER_API_KEY='your_key_here'
```

   To enable transformer-based semantic similarity (optional):
```bash
pip install -r requirements-ml.txt
```

3. Start the backend server:
```bash
make run
```

### Frontend Setup

1. Install frontend dependencies:
```bash
make frontend
```

2. Start the development server:
```bash
make run-frontend
```

### Additional Make Commands

- `make help` - Show all available commands
- `make clean` - Clean up generated files and dependencies
- `make test` - Run both backend and frontend tests

## How to Use

1. Open the mobile app
2. Paste a URL of a fashion item you like
3. Wait for the app to analyze the product
4. Browse through similar items and deals
5. Save your favorite finds

## Project Structure

```
.
├── backend/
│   ├── app.py        # Flask server
│   └── agent.py      # Scraping logic
├── frontend/
│   ├── App.js
│   ├── components/   # UI components
│   └── screens/      # App screens
└── Makefile         # Build automation
```

## Development

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React Native code
- Write tests for new features
- Keep the codebase clean and documented

## Contributing

1. Fork the project
2. Create your feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use and modify the code as you wish
