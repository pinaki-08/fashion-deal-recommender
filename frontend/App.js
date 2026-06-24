import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

import { analyzeProduct, getStores } from "./src/api";

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [storeCount, setStoreCount] = useState(null);

  useEffect(() => {
    getStores()
      .then((data) => setStoreCount(data.count))
      .catch(() => setStoreCount(null));
  }, []);

  const onAnalyze = async () => {
    if (!url.trim()) {
      setError("Please enter a product URL.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeProduct(url.trim());
      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar style="dark" />
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Fashion Deal Recommender</Text>
        {storeCount != null && (
          <Text style={styles.subtitle}>
            Searching across {storeCount}+ stores
          </Text>
        )}

        <TextInput
          style={styles.input}
          placeholder="Paste a product URL..."
          autoCapitalize="none"
          autoCorrect={false}
          value={url}
          onChangeText={setUrl}
        />

        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={onAnalyze}
          disabled={loading}
        >
          <Text style={styles.buttonText}>
            {loading ? "Analyzing..." : "Find Deals"}
          </Text>
        </TouchableOpacity>

        {loading && <ActivityIndicator style={{ marginTop: 16 }} />}

        {error && <Text style={styles.error}>{error}</Text>}

        {result && (
          <View style={styles.resultBox}>
            <Text style={styles.sectionTitle}>Product</Text>
            <Text style={styles.productName}>
              {result.product_info?.name || "Unknown product"}
            </Text>
            {result.product_info?.price != null && (
              <Text style={styles.price}>{result.product_info.price}</Text>
            )}

            <Text style={[styles.sectionTitle, { marginTop: 20 }]}>
              Similar items
            </Text>
            {(!result.similar_products ||
              result.similar_products.length === 0) && (
              <Text style={styles.muted}>No similar products found.</Text>
            )}
            <FlatList
              scrollEnabled={false}
              data={result.similar_products || []}
              keyExtractor={(item, idx) => `${item.url || item.name}-${idx}`}
              renderItem={({ item }) => (
                <View style={styles.card}>
                  <Text style={styles.cardName}>{item.name}</Text>
                  <View style={styles.cardRow}>
                    {item.price != null && (
                      <Text style={styles.cardPrice}>{item.price}</Text>
                    )}
                    {item.source && (
                      <Text style={styles.cardSource}>{item.source}</Text>
                    )}
                    {item.similarity_score != null && (
                      <Text style={styles.cardScore}>
                        {Math.round(item.similarity_score * 100)}% match
                      </Text>
                    )}
                  </View>
                </View>
              )}
            />
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#fafafa" },
  container: { padding: 20 },
  title: { fontSize: 26, fontWeight: "700", color: "#111" },
  subtitle: { fontSize: 14, color: "#666", marginTop: 4, marginBottom: 16 },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 10,
    padding: 14,
    backgroundColor: "#fff",
    fontSize: 15,
  },
  button: {
    marginTop: 12,
    backgroundColor: "#111",
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: "center",
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: "#fff", fontWeight: "600", fontSize: 16 },
  error: { marginTop: 16, color: "#c0392b" },
  resultBox: { marginTop: 24 },
  sectionTitle: { fontSize: 18, fontWeight: "600", color: "#111" },
  productName: { fontSize: 16, marginTop: 6, color: "#222" },
  price: { fontSize: 16, marginTop: 2, color: "#2e7d32", fontWeight: "600" },
  muted: { color: "#888", marginTop: 8 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 10,
    padding: 14,
    marginTop: 10,
    borderWidth: 1,
    borderColor: "#eee",
  },
  cardName: { fontSize: 15, color: "#222", fontWeight: "500" },
  cardRow: { flexDirection: "row", marginTop: 6, alignItems: "center" },
  cardPrice: { color: "#2e7d32", fontWeight: "600", marginRight: 12 },
  cardSource: { color: "#555", marginRight: 12 },
  cardScore: { color: "#1565c0", fontWeight: "600" },
});
