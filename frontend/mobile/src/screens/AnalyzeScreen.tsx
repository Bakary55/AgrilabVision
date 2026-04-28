import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import * as ImagePicker from "expo-image-picker";
import { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { API_BASE_URL } from "../constants/config";
import { RootStackParamList } from "../navigation/types";
import type { SoilAnalysisResult } from "../types/api";

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, "Analyze">;
};

export function AnalyzeScreen({ navigation }: Props) {
  const [language, setLanguage] = useState<"en" | "fr">("en");
  const [uri, setUri] = useState<string | null>(null);
  const [mime, setMime] = useState<string>("image/jpeg");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SoilAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [manualLoading, setManualLoading] = useState(false);
  const [manualError, setManualError] = useState<string | null>(null);
  const [manualRecommendation, setManualRecommendation] = useState<any | null>(null);
  const [ph, setPh] = useState("");
  const [moisture, setMoisture] = useState("");
  const [organicMatter, setOrganicMatter] = useState("");
  const [clay, setClay] = useState("");
  const [phosphate, setPhosphate] = useState("");

  function applyPickedAsset(asset: ImagePicker.ImagePickerAsset) {
    setUri(asset.uri);
    if (asset.mimeType?.startsWith("image/")) {
      setMime(asset.mimeType);
    } else {
      setMime("image/jpeg");
    }
    setResult(null);
    setError(null);
  }

  async function pickImage() {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) {
      Alert.alert(
        "Permission denied",
        "Allow photo library access to choose a soil image."
      );
      return;
    }
    const picked = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      quality: 0.85,
    });
    if (picked.canceled || !picked.assets?.[0]) return;
    applyPickedAsset(picked.assets[0]);
  }

  async function takePhoto() {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) {
      Alert.alert(
        "Permission denied",
        "Allow camera access to take a soil photo."
      );
      return;
    }
    const shot = await ImagePicker.launchCameraAsync({
      mediaTypes: ["images"],
      quality: 0.85,
    });
    if (shot.canceled || !shot.assets?.[0]) return;
    applyPickedAsset(shot.assets[0]);
  }

  function buildSoilSummary(r: SoilAnalysisResult): string {
    return [
      `Soil type: ${r.soil_type}`,
      `Moisture estimate: ${r.moisture_estimate}`,
      `Crops: ${r.recommended_crops.join(", ")}`,
      `Fertilizer: ${r.fertilizer_recommendations.join(" | ")}`,
    ].join(". ");
  }

  async function analyze() {
    if (!uri) {
      Alert.alert("Photo", "Choose an image first.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("language", language);
      form.append("image", {
        uri,
        name: "soil.jpg",
        type: mime,
      } as unknown as Blob);

      const res = await fetch(`${API_BASE_URL}/ai/soil-analyze`, {
        method: "POST",
        body: form,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Analysis failed. Please try again."
        );
      }
      setResult(data as SoilAnalysisResult);
    } catch (e) {
      let msg = e instanceof Error ? e.message : "Network error";
      if (
        msg === "Network request failed" ||
        msg.toLowerCase().includes("network")
      ) {
        const isLoopback =
          API_BASE_URL.includes("127.0.0.1") ||
          API_BASE_URL.includes("localhost");
        msg =
          isLoopback
            ? "Cannot reach the server. On a real phone, set EXPO_PUBLIC_API_BASE_URL in mobile/.env to your PC's Wi‑Fi IP (e.g. http://192.168.1.10:8000), restart Expo, and ensure uvicorn runs with --host 0.0.0.0."
            : `Cannot reach ${API_BASE_URL}. Same Wi‑Fi as the PC, firewall allows port 8000, backend running.`;
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  async function analyzeManual() {
    setManualError(null);
    setManualRecommendation(null);
    const parsed = {
      ph: Number(ph),
      moisture: Number(moisture),
      organic_matter: Number(organicMatter),
      clay: Number(clay),
      phosphate: Number(phosphate),
    };
    if (Object.values(parsed).some((v) => Number.isNaN(v))) {
      setManualError("Please fill all manual fields with valid numbers.");
      return;
    }

    setManualLoading(true);
    try {
      const createRes = await fetch(`${API_BASE_URL}/soil-samples`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed),
      });
      const created = await createRes.json().catch(() => ({}));
      if (!createRes.ok || !created.id) {
        throw new Error("Could not save manual soil data.");
      }

      const recRes = await fetch(
        `${API_BASE_URL}/soil-samples/${created.id}/recommendation`
      );
      const recData = await recRes.json().catch(() => ({}));
      if (!recRes.ok) {
        throw new Error("Could not generate recommendation from manual data.");
      }
      setManualRecommendation(recData);
    } catch (e) {
      setManualError(e instanceof Error ? e.message : "Manual analysis failed.");
    } finally {
      setManualLoading(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.label}>Analysis language</Text>
      <View style={styles.row}>
        <TouchableOpacity
          style={[styles.chip, language === "en" && styles.chipOn]}
          onPress={() => setLanguage("en")}
        >
          <Text style={language === "en" ? styles.chipTextOn : styles.chipText}>
            English
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.chip, language === "fr" && styles.chipOn]}
          onPress={() => setLanguage("fr")}
        >
          <Text style={language === "fr" ? styles.chipTextOn : styles.chipText}>
            Français
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.pickRow}>
        <TouchableOpacity
          style={[styles.pickBtn, styles.pickBtnHalf]}
          onPress={pickImage}
        >
          <Text style={styles.pickBtnText}>Choose photo</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.pickBtn, styles.pickBtnHalf]}
          onPress={takePhoto}
        >
          <Text style={styles.pickBtnText}>Take photo</Text>
        </TouchableOpacity>
      </View>
      {uri ? (
        <Image source={{ uri }} style={styles.preview} resizeMode="cover" />
      ) : null}

      <TouchableOpacity
        style={[styles.analyzeBtn, loading && styles.disabled]}
        onPress={analyze}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.analyzeBtnText}>Analyze soil</Text>
        )}
      </TouchableOpacity>

      {error ? <Text style={styles.error}>{error}</Text> : null}

      {result ? (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Result</Text>
          <Text style={styles.line}>
            <Text style={styles.bold}>Soil type: </Text>
            {result.soil_type}
          </Text>
          <Text style={styles.line}>
            <Text style={styles.bold}>Moisture: </Text>
            {result.moisture_estimate}
          </Text>
          <Text style={styles.line}>
            <Text style={styles.bold}>Photo quality: </Text>
            {result.photo_quality_label} ({result.photo_quality_score}/100)
          </Text>
          {(result.photo_quality_notes || []).slice(0, 1).map((n) => (
            <Text key={n} style={styles.bullet}>
              • {n}
            </Text>
          ))}
          <Text style={styles.bold}>Recommended crops</Text>
          {result.recommended_crops.length > 0 ? (
            result.recommended_crops.map((c) => (
              <Text key={c} style={styles.bullet}>
                • {c}
              </Text>
            ))
          ) : (
            <Text style={styles.bullet}>
              • Not enough confidence from photo only. Add manual measurements for crop recommendations.
            </Text>
          )}
          <Text style={[styles.bold, styles.mt]}>Fertilizer</Text>
          {result.fertilizer_recommendations.map((c) => (
            <Text key={c} style={styles.bullet}>
              • {c}
            </Text>
          ))}
          <Text style={[styles.bold, styles.mt]}>Notes</Text>
          {result.notes
            .filter(
              (n) =>
                !n.toLowerCase().includes("technical detail") &&
                !n.toLowerCase().includes("fallback analysis")
            )
            .map((n) => (
            <Text key={n} style={styles.bullet}>
              • {n}
            </Text>
            ))}
          <TouchableOpacity
            style={styles.linkBtn}
            onPress={() =>
              navigation.navigate("MapWeather", {
                soilSummary: buildSoilSummary(result),
              })
            }
          >
            <Text style={styles.linkBtnText}>
              Weather, map & AI advice for this soil →
            </Text>
          </TouchableOpacity>
        </View>
      ) : null}

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Manual soil input (recommended)</Text>
        <Text style={styles.label}>
          Enter measurements to get stronger recommendations.
        </Text>

        <TextInput
          style={styles.input}
          placeholder="pH (0-14)"
          keyboardType="decimal-pad"
          value={ph}
          onChangeText={setPh}
        />
        <TextInput
          style={styles.input}
          placeholder="Moisture % (0-100)"
          keyboardType="decimal-pad"
          value={moisture}
          onChangeText={setMoisture}
        />
        <TextInput
          style={styles.input}
          placeholder="Organic matter % (0-100)"
          keyboardType="decimal-pad"
          value={organicMatter}
          onChangeText={setOrganicMatter}
        />
        <TextInput
          style={styles.input}
          placeholder="Clay % (0-100)"
          keyboardType="decimal-pad"
          value={clay}
          onChangeText={setClay}
        />
        <TextInput
          style={styles.input}
          placeholder="Phosphate (>=0)"
          keyboardType="decimal-pad"
          value={phosphate}
          onChangeText={setPhosphate}
        />

        <TouchableOpacity
          style={[styles.analyzeBtn, manualLoading && styles.disabled]}
          onPress={analyzeManual}
          disabled={manualLoading}
        >
          {manualLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.analyzeBtnText}>Analyze manual data</Text>
          )}
        </TouchableOpacity>

        {manualError ? <Text style={styles.error}>{manualError}</Text> : null}

        {manualRecommendation ? (
          <View style={[styles.card, { marginTop: 12 }]}>
            <Text style={styles.bold}>
              Fertility score: {manualRecommendation.fertility_score}
            </Text>
            <Text style={styles.line}>
              <Text style={styles.bold}>Soil class: </Text>
              {manualRecommendation.soil_type}
            </Text>
            <Text style={styles.bold}>Recommended crops</Text>
            {(manualRecommendation.recommended_crops || []).map((c: string) => (
              <Text key={c} style={styles.bullet}>
                • {c}
              </Text>
            ))}
            <Text style={[styles.bold, styles.mt]}>Fertilizer</Text>
            <Text style={styles.bullet}>
              • {manualRecommendation.fertilizer_suggestion}
            </Text>
            <Text style={[styles.bold, styles.mt]}>Irrigation</Text>
            <Text style={styles.bullet}>
              • {manualRecommendation.irrigation_suggestion}
            </Text>
          </View>
        ) : null}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    paddingBottom: 40,
    backgroundColor: "#f4f7f4",
  },
  label: { fontSize: 15, color: "#333", marginBottom: 8 },
  row: { flexDirection: "row", gap: 10, marginBottom: 16 },
  chip: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#1c6b2d",
  },
  chipOn: { backgroundColor: "#1c6b2d" },
  chipText: { color: "#1c6b2d" },
  chipTextOn: { color: "#fff", fontWeight: "600" },
  pickRow: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 8,
  },
  pickBtn: {
    backgroundColor: "#e8f5e9",
    padding: 14,
    borderRadius: 10,
    marginBottom: 12,
  },
  pickBtnHalf: { flex: 1, marginBottom: 0 },
  pickBtnText: { color: "#1c6b2d", fontWeight: "600", textAlign: "center" },
  input: {
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#cdd7cd",
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    marginBottom: 10,
    fontSize: 14,
  },
  preview: {
    width: "100%",
    height: 220,
    borderRadius: 12,
    marginBottom: 16,
    backgroundColor: "#ddd",
  },
  analyzeBtn: {
    backgroundColor: "#1c6b2d",
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
  },
  analyzeBtnText: { color: "#fff", fontSize: 17, fontWeight: "600" },
  disabled: { opacity: 0.7 },
  error: { color: "#b00020", marginTop: 12 },
  card: {
    marginTop: 20,
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    elevation: 2,
    shadowColor: "#000",
    shadowOpacity: 0.08,
    shadowRadius: 8,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#1c6b2d",
    marginBottom: 12,
  },
  line: { fontSize: 15, marginBottom: 8, color: "#222" },
  bold: { fontWeight: "700" },
  bullet: { fontSize: 14, color: "#333", marginLeft: 8 },
  mt: { marginTop: 12 },
  linkBtn: { marginTop: 16, paddingVertical: 12 },
  linkBtnText: { color: "#1565c0", fontWeight: "600", fontSize: 15 },
});
