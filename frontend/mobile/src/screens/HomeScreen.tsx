import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { useAuth } from "../context/AuthContext";
import { RootStackParamList } from "../navigation/types";

type Props = {
  navigation: NativeStackNavigationProp<RootStackParamList, "Home">;
};

export function HomeScreen({ navigation }: Props) {
  const { user, logout } = useAuth();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>AgrilabVision</Text>
      {user ? (
        <Text style={styles.welcome}>
          Hello, {user.first_name} ({user.user_type})
        </Text>
      ) : null}
      <Text style={styles.sub}>
        AI soil photo analysis, map, weather, and location-aware farming tips.
      </Text>
      <TouchableOpacity
        style={styles.primary}
        onPress={() => navigation.navigate("Analyze")}
      >
        <Text style={styles.primaryText}>Analyze a soil photo</Text>
      </TouchableOpacity>
      <TouchableOpacity
        style={styles.secondary}
        onPress={() => navigation.navigate("MapWeather", {})}
      >
        <Text style={styles.secondaryText}>Map, weather & AI advice</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.logout} onPress={() => void logout()}>
        <Text style={styles.logoutText}>Log out</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    justifyContent: "center",
    backgroundColor: "#f4f7f4",
  },
  title: {
    fontSize: 28,
    fontWeight: "700",
    color: "#1c6b2d",
    marginBottom: 12,
  },
  welcome: {
    fontSize: 15,
    color: "#1c6b2d",
    fontWeight: "600",
    marginBottom: 8,
  },
  sub: {
    fontSize: 16,
    color: "#333",
    marginBottom: 32,
    lineHeight: 22,
  },
  primary: {
    backgroundColor: "#1c6b2d",
    paddingVertical: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  primaryText: {
    color: "#fff",
    textAlign: "center",
    fontSize: 17,
    fontWeight: "600",
  },
  secondary: {
    borderWidth: 2,
    borderColor: "#1c6b2d",
    paddingVertical: 16,
    borderRadius: 12,
  },
  secondaryText: {
    color: "#1c6b2d",
    textAlign: "center",
    fontSize: 17,
    fontWeight: "600",
  },
  logout: {
    marginTop: 24,
    paddingVertical: 12,
  },
  logoutText: {
    color: "#666",
    textAlign: "center",
    fontSize: 16,
  },
});
