# Fashion Deal Recommender — Mobile App

A React Native (Expo) frontend for the Fashion Deal Recommender backend.
Users paste a product URL, and the app shows the product plus semantically
ranked similar items from 50+ stores.

## Setup

```bash
cd frontend
npm install
npm start
```

Then press `i` (iOS simulator), `a` (Android emulator), or `w` (web), or scan
the QR code with the Expo Go app.

## Configuration

The backend URL is read from `app.json` → `expo.extra.apiBaseUrl`
(default `http://localhost:3000`).

- iOS simulator / web: `http://localhost:3000` works.
- Android emulator: use `http://10.0.2.2:3000`.
- Physical device: use your machine's LAN IP, e.g. `http://192.168.1.10:3000`,
  and make sure the backend is running with `make run`.

## Structure

- `App.js` — main screen (URL input, results, similar items)
- `src/api.js` — typed API client for the Flask backend
