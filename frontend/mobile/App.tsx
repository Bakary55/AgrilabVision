import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { ActivityIndicator, View } from "react-native";
import { StatusBar } from "expo-status-bar";
import { AuthProvider, useAuth } from "./src/context/AuthContext";
import { RootStackParamList } from "./src/navigation/types";
import { AccountScreen } from "./src/screens/AccountScreen";
import { AnalyzeScreen } from "./src/screens/AnalyzeScreen";
import { AuthScreen } from "./src/screens/AuthScreen";
import { HomeScreen } from "./src/screens/HomeScreen";
import { MapWeatherScreen } from "./src/screens/MapWeatherScreen";

const Stack = createNativeStackNavigator<RootStackParamList>();

const screenOptions = {
  headerStyle: { backgroundColor: "#1c6b2d" },
  headerTintColor: "#fff",
  headerTitleStyle: { fontWeight: "600" as const },
};

function RootNavigator() {
  const { token, ready } = useAuth();

  if (!ready) {
    return (
      <View
        style={{
          flex: 1,
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#f4f7f4",
        }}
      >
        <ActivityIndicator size="large" color="#1c6b2d" />
      </View>
    );
  }

  return (
    <Stack.Navigator screenOptions={screenOptions}>
      {token == null ? (
        <Stack.Screen
          name="Auth"
          component={AuthScreen}
          options={{ headerShown: false }}
        />
      ) : (
        <>
          <Stack.Screen
            name="Home"
            component={HomeScreen}
            options={{ title: "AgrilabVision" }}
          />
          <Stack.Screen
            name="Account"
            component={AccountScreen}
            options={{ title: "My account" }}
          />
          <Stack.Screen
            name="Analyze"
            component={AnalyzeScreen}
            options={{ title: "Soil analysis" }}
          />
          <Stack.Screen
            name="MapWeather"
            component={MapWeatherScreen}
            options={{ title: "Map & weather" }}
          />
        </>
      )}
    </Stack.Navigator>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <NavigationContainer>
        <StatusBar style="light" />
        <RootNavigator />
      </NavigationContainer>
    </AuthProvider>
  );
}
