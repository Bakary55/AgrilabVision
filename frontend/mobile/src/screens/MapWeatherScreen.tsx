import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { RouteProp } from "@react-navigation/native";
import * as Location from "expo-location";
import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  Linking,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import MapView, { Marker } from "react-native-maps";
import { API_BASE_URL } from "../constants/config";
import { RootStackParamList } from "../navigation/types";
import type { FarmingInsight, WeatherCurrent } from "../types/api";

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, "MapWeather">;
  route: RouteProp<RootStackParamList, "MapWeather">;
};

export function MapWeatherScreen({ route }: Props) {
  const soilSummary = route.params?.soilSummary;
  const [lat, setLat] = useState<number | null>(null);
  const [lon, setLon] = useState<number | null>(null);
  const [locError, setLocError] = useState<string | null>(null);
  const [loadingLoc, setLoadingLoc] = useState(true);
  const [weather, setWeather] = useState<WeatherCurrent | null>(null);
  const [weatherErr, setWeatherErr] = useState<string | null>(null);
  const [loadingWeather, setLoadingWeather] = useState(false);
  const [insight, setInsight] = useState<FarmingInsight | null>(null);
  const [loadingInsight, setLoadingInsight] = useState(false);
  const [insightErr, setInsightErr] = useState<string | null>(null);

  const loadLocation = useCallback(async () => {
    setLoadingLoc(true);
    setLocError(null);
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        setLocError("Location permission denied.");
        return;
      }
      const pos = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });
      setLat(pos.coords.latitude);
      setLon(pos.coords.longitude);
    } catch {
      setLocError("Could not get GPS position.");
    } finally {
      setLoadingLoc(false);
    }
  }, []);

  useEffect(() => {
    loadLocation();
  }, [loadLocation]);

  const fetchWeather = async () => {
    if (lat == null || lon == null) return;
    setLoadingWeather(true);
    setWeatherErr(null);
    try {
      const url = `${API_BASE_URL}/weather/current?lat=${lat}&lon=${lon}`;
      const res = await fetch(url);
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Weather unavailable. Check the backend."
        );
      }
      setWeather(data as WeatherCurrent);
    } catch (e) {
      setWeatherErr(e instanceof Error ? e.message : "Weather error");
    } finally {
      setLoadingWeather(false);
    }
  };

  useEffect(() => {
    if (lat != null && lon != null) {
      fetchWeather();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lat, lon]);

  const openGoogleMaps = () => {
    if (lat == null || lon == null) return;
    const url = `https://www.google.com/maps?q=${lat},${lon}`;
    Linking.openURL(url);
  };

  const fetchInsight = async () => {
    if (lat == null || lon == null) return;
    setLoadingInsight(true);
    setInsightErr(null);
    setInsight(null);
    try {
      const res = await fetch(`${API_BASE_URL}/insights/farming`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat,
          lon,
          language: "en",
          soil_summary: soilSummary ?? null,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "AI advice is temporarily unavailable."
        );
      }
      setInsight(data as FarmingInsight);
    } catch (e) {
      setInsightErr(e instanceof Error ? e.message : "Error");
    } finally {
      setLoadingInsight(false);
    }
  };

  if (loadingLoc) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#1c6b2d" />
        <Text style={styles.muted}>Getting location…</Text>
      </View>
    );
  }

  if (locError || lat == null || lon == null) {
    return (
      <View style={styles.centered}>
        <Text style={styles.error}>{locError ?? "Unknown position"}</Text>
        <TouchableOpacity style={styles.btn} onPress={loadLocation}>
          <Text style={styles.btnText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.coords}>
        {lat.toFixed(5)}, {lon.toFixed(5)}
      </Text>
      <TouchableOpacity style={styles.outlineBtn} onPress={openGoogleMaps}>
        <Text style={styles.outlineBtnText}>Open in Google Maps</Text>
      </TouchableOpacity>

      <View style={styles.mapWrap}>
        <MapView
          style={styles.map}
          initialRegion={{
            latitude: lat,
            longitude: lon,
            latitudeDelta: 0.02,
            longitudeDelta: 0.02,
          }}
        >
          <Marker coordinate={{ latitude: lat, longitude: lon }} title="You" />
        </MapView>
      </View>
      {__DEV__ ? (
        <Text style={styles.hint}>
          On Android, set your Google Maps API key in app.json →
          android.config.googleMaps.apiKey for embedded tiles.
        </Text>
      ) : null}

      <Text style={styles.section}>Current weather</Text>
      {loadingWeather ? (
        <ActivityIndicator color="#1c6b2d" />
      ) : weatherErr ? (
        <Text style={styles.error}>{weatherErr}</Text>
      ) : weather ? (
        <View style={styles.card}>
          <Text style={styles.line}>
            {weather.location_name ?? "Location"} — {weather.description}
          </Text>
          <Text style={styles.line}>
            {weather.temp_c.toFixed(1)} °C · humidity {weather.humidity} % · wind{" "}
            {weather.wind_speed_ms.toFixed(1)} m/s
          </Text>
        </View>
      ) : null}

      <Text style={styles.section}>AI advice (weather + location)</Text>
      {soilSummary ? (
        <Text style={styles.soilHint}>
          Soil context from photo analysis is sent to the AI.
        </Text>
      ) : null}
      <TouchableOpacity
        style={[styles.btn, loadingInsight && styles.disabled]}
        onPress={fetchInsight}
        disabled={loadingInsight}
      >
        {loadingInsight ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>Get farming advice</Text>
        )}
      </TouchableOpacity>
      {insightErr ? <Text style={styles.error}>{insightErr}</Text> : null}
      {insight ? (
        <View style={styles.card}>
          <Text style={styles.bold}>Weather summary (server)</Text>
          <Text style={styles.body}>{insight.weather_summary}</Text>
          <Text style={[styles.bold, styles.mt]}>Advice</Text>
          <Text style={styles.body}>{insight.advisory_text}</Text>
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    paddingBottom: 40,
    backgroundColor: "#f4f7f4",
  },
  centered: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 24,
    backgroundColor: "#f4f7f4",
  },
  muted: { marginTop: 8, color: "#666" },
  coords: { fontSize: 14, color: "#333", marginBottom: 8 },
  mapWrap: {
    height: 220,
    borderRadius: 12,
    overflow: "hidden",
    marginBottom: 8,
  },
  map: { flex: 1 },
  hint: { fontSize: 12, color: "#666", marginBottom: 16 },
  section: {
    fontSize: 17,
    fontWeight: "700",
    color: "#1c6b2d",
    marginTop: 8,
    marginBottom: 8,
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
  },
  line: { fontSize: 15, color: "#222", marginBottom: 4 },
  error: { color: "#b00020", marginVertical: 8 },
  btn: {
    backgroundColor: "#1c6b2d",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 8,
  },
  btnText: { color: "#fff", fontWeight: "600", fontSize: 16 },
  outlineBtn: {
    borderWidth: 2,
    borderColor: "#1c6b2d",
    padding: 12,
    borderRadius: 12,
    marginBottom: 12,
  },
  outlineBtnText: {
    color: "#1c6b2d",
    fontWeight: "600",
    textAlign: "center",
  },
  disabled: { opacity: 0.7 },
  soilHint: { fontSize: 13, color: "#555", marginBottom: 8 },
  bold: { fontWeight: "700", color: "#1c6b2d" },
  body: { fontSize: 15, color: "#222", marginTop: 6, lineHeight: 22 },
  mt: { marginTop: 12 },
});
