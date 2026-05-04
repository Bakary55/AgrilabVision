import * as ImagePicker from "expo-image-picker";
import { Alert, Image, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { useAuth } from "../context/AuthContext";

export function AccountScreen() {
  const { user, profilePhotoUri, saveProfilePhoto, clearProfilePhoto } = useAuth();

  async function pickProfilePhoto() {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) {
      Alert.alert("Permission denied", "Allow photo access to set a profile picture.");
      return;
    }
    const picked = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      quality: 0.85,
    });
    if (picked.canceled || !picked.assets?.[0]) return;
    await saveProfilePhoto(picked.assets[0].uri);
  }

  return (
    <View style={styles.container}>
      <View style={styles.avatarWrap}>
        {profilePhotoUri ? (
          <Image source={{ uri: profilePhotoUri }} style={styles.avatarImg} />
        ) : (
          <Text style={styles.avatarFallback}>
            {user?.first_name?.[0]?.toUpperCase() ?? "U"}
          </Text>
        )}
      </View>

      <Text style={styles.name}>
        {user?.first_name} {user?.last_name}
      </Text>
      <Text style={styles.meta}>{user?.email}</Text>
      <Text style={styles.meta}>Role: {user?.user_type}</Text>

      <TouchableOpacity style={styles.primaryBtn} onPress={() => void pickProfilePhoto()}>
        <Text style={styles.primaryBtnText}>
          {profilePhotoUri ? "Change profile photo" : "Add profile photo"}
        </Text>
      </TouchableOpacity>

      {profilePhotoUri ? (
        <TouchableOpacity style={styles.secondaryBtn} onPress={() => void clearProfilePhoto()}>
          <Text style={styles.secondaryBtnText}>Remove photo</Text>
        </TouchableOpacity>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    alignItems: "center",
    backgroundColor: "#f4f7f4",
  },
  avatarWrap: {
    width: 110,
    height: 110,
    borderRadius: 55,
    backgroundColor: "#dcebdc",
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
    marginTop: 18,
    marginBottom: 16,
  },
  avatarImg: {
    width: "100%",
    height: "100%",
  },
  avatarFallback: {
    fontSize: 42,
    fontWeight: "700",
    color: "#1c6b2d",
  },
  name: {
    fontSize: 22,
    fontWeight: "700",
    color: "#1c6b2d",
  },
  meta: {
    fontSize: 15,
    color: "#555",
    marginTop: 6,
  },
  primaryBtn: {
    marginTop: 26,
    backgroundColor: "#1c6b2d",
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 10,
    width: "100%",
  },
  primaryBtnText: {
    color: "#fff",
    textAlign: "center",
    fontWeight: "600",
    fontSize: 16,
  },
  secondaryBtn: {
    marginTop: 12,
    borderWidth: 1,
    borderColor: "#1c6b2d",
    paddingVertical: 12,
    borderRadius: 10,
    width: "100%",
  },
  secondaryBtnText: {
    color: "#1c6b2d",
    textAlign: "center",
    fontWeight: "600",
    fontSize: 15,
  },
});
