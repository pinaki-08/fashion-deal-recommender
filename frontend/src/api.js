// API client for the Fashion Deal Recommender backend.
import Constants from "expo-constants";

// Configure via app.json -> expo.extra.apiBaseUrl, or override here.
const API_BASE_URL =
  (Constants.expoConfig &&
    Constants.expoConfig.extra &&
    Constants.expoConfig.extra.apiBaseUrl) ||
  "http://localhost:3000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || `Request failed (${response.status})`);
  }
  return data;
}

export function analyzeProduct(url) {
  return request("/analyze-product", {
    method: "POST",
    body: JSON.stringify({ url, timestamp: new Date().toISOString() }),
  });
}

export function getRecentSearches() {
  return request("/recent-searches", { method: "GET" });
}

export function getStores() {
  return request("/stores", { method: "GET" });
}

export function clearHistory() {
  return request("/clear-history", { method: "POST" });
}

export { API_BASE_URL };
