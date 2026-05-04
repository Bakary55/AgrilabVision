import { useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { useAuth, type RegisterPayload } from "../context/AuthContext";

type Mode = "login" | "register";

export function AuthScreen() {
  const { login, register, forgotPassword, resetPassword } = useAuth();
  const [mode, setMode] = useState<Mode | "forgot" | "reset">("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [age, setAge] = useState("");
  const [userType, setUserType] =
    useState<RegisterPayload["user_type"]>("farmer");
  const [showPassword, setShowPassword] = useState(false);
  const [resetToken, setResetToken] = useState("");
  const [newPassword, setNewPassword] = useState("");

  function switchMode(next: Mode | "forgot" | "reset") {
    setMode(next);
    setError(null);
    setSuccess(null);
  }

  async function onLogin() {
    setError(null);
    setSuccess(null);
    if (!email.trim() || !password) {
      setError("Email and password are required.");
      return;
    }
    setLoading(true);
    try {
      await login(email.trim(), password);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  async function onRegister() {
    setError(null);
    setSuccess(null);
    const ageNum = parseInt(age, 10);
    if (
      !firstName.trim() ||
      !lastName.trim() ||
      !email.trim() ||
      !password ||
      Number.isNaN(ageNum) ||
      ageNum < 13
    ) {
      setError(
        "Fill all fields. Age must be at least 13."
      );
      return;
    }
    setLoading(true);
    try {
      await register({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        age: ageNum,
        user_type: userType,
        password,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  async function onForgotPassword() {
    setError(null);
    setSuccess(null);
    if (!email.trim()) {
      setError("Email is required.");
      return;
    }
    setLoading(true);
    try {
      const message = await forgotPassword(email.trim());
      setSuccess(message);
      setMode("reset");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Forgot password failed.");
    } finally {
      setLoading(false);
    }
  }

  async function onResetPassword() {
    setError(null);
    setSuccess(null);
    if (!resetToken.trim() || !newPassword) {
      setError("Reset token and new password are required.");
      return;
    }
    setLoading(true);
    try {
      const message = await resetPassword(resetToken, newPassword);
      setSuccess(message);
      setPassword("");
      setNewPassword("");
      setResetToken("");
      setMode("login");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Reset password failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <ScrollView
        contentContainerStyle={styles.scroll}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.brand}>AgrilabVision</Text>
        <Text style={styles.sub}>Sign in or create an account</Text>

        <View style={styles.row}>
          <TouchableOpacity
            style={[styles.chip, mode === "login" && styles.chipOn]}
            onPress={() => {
              switchMode("login");
            }}
          >
            <Text
              style={mode === "login" ? styles.chipTextOn : styles.chipText}
            >
              Sign in
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.chip, mode === "register" && styles.chipOn]}
            onPress={() => {
              switchMode("register");
            }}
          >
            <Text
              style={
                mode === "register" ? styles.chipTextOn : styles.chipText
              }
            >
              Create account
            </Text>
          </TouchableOpacity>
        </View>

        {mode === "register" ? (
          <>
            <Text style={styles.label}>First name</Text>
            <TextInput
              style={styles.input}
              value={firstName}
              onChangeText={setFirstName}
              autoCapitalize="words"
              editable={!loading}
            />
            <Text style={styles.label}>Last name</Text>
            <TextInput
              style={styles.input}
              value={lastName}
              onChangeText={setLastName}
              autoCapitalize="words"
              editable={!loading}
            />
            <Text style={styles.label}>Age</Text>
            <TextInput
              style={styles.input}
              value={age}
              onChangeText={setAge}
              keyboardType="number-pad"
              editable={!loading}
            />
            <Text style={styles.label}>User type</Text>
            <View style={styles.typeRow}>
              {(
                ["farmer", "student", "researcher"] as const
              ).map((t) => (
                <TouchableOpacity
                  key={t}
                  style={[
                    styles.typeChip,
                    userType === t && styles.typeChipOn,
                  ]}
                  onPress={() => setUserType(t)}
                  disabled={loading}
                >
                  <Text
                    style={
                      userType === t ? styles.typeChipTextOn : styles.typeChipText
                    }
                  >
                    {t.charAt(0).toUpperCase() + t.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
            <Text style={styles.hint}>
              Password: 8+ chars, uppercase, lowercase, number, special
              character.
            </Text>
          </>
        ) : null}

        <Text style={styles.label}>Email</Text>
        <TextInput
          style={styles.input}
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
          autoCorrect={false}
          editable={!loading}
        />

        {mode === "login" || mode === "register" ? (
          <>
            <View style={styles.labelRow}>
              <Text style={styles.labelPlain}>Password</Text>
              <TouchableOpacity
                onPress={() => setShowPassword((v) => !v)}
                disabled={loading}
                hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
              >
                <Text style={styles.showPwd}>
                  {showPassword ? "Hide" : "Show"}
                </Text>
              </TouchableOpacity>
            </View>
            <TextInput
              style={styles.input}
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPassword}
              editable={!loading}
              autoCapitalize="none"
              autoCorrect={false}
            />
            <Text style={styles.hint}>
              Password rules: at least 8 characters, 1 uppercase, 1 lowercase, 1 number, and 1 special character.
            </Text>
          </>
        ) : null}

        {mode === "forgot" ? (
          <Text style={styles.hint}>
            Enter your account email to request a password reset.
          </Text>
        ) : null}

        {mode === "reset" ? (
          <>
            <Text style={styles.label}>Reset token</Text>
            <TextInput
              style={styles.input}
              value={resetToken}
              onChangeText={setResetToken}
              editable={!loading}
              autoCapitalize="none"
              autoCorrect={false}
            />
            <View style={styles.labelRow}>
              <Text style={styles.labelPlain}>New password</Text>
              <TouchableOpacity
                onPress={() => setShowPassword((v) => !v)}
                disabled={loading}
                hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
              >
                <Text style={styles.showPwd}>
                  {showPassword ? "Hide" : "Show"}
                </Text>
              </TouchableOpacity>
            </View>
            <TextInput
              style={styles.input}
              value={newPassword}
              onChangeText={setNewPassword}
              secureTextEntry={!showPassword}
              editable={!loading}
              autoCapitalize="none"
              autoCorrect={false}
            />
            <Text style={styles.hint}>
              Password rules: at least 8 characters, 1 uppercase, 1 lowercase, 1 number, and 1 special character.
            </Text>
          </>
        ) : null}

        {error ? <Text style={styles.error}>{error}</Text> : null}
        {success ? <Text style={styles.success}>{success}</Text> : null}

        {mode === "login" ? (
          <TouchableOpacity
            style={styles.linkBtn}
            onPress={() => switchMode("forgot")}
            disabled={loading}
          >
            <Text style={styles.linkText}>Forgot password?</Text>
          </TouchableOpacity>
        ) : null}

        {mode === "forgot" || mode === "reset" ? (
          <TouchableOpacity
            style={styles.linkBtn}
            onPress={() => switchMode("login")}
            disabled={loading}
          >
            <Text style={styles.linkText}>Back to sign in</Text>
          </TouchableOpacity>
        ) : null}

        <TouchableOpacity
          style={[styles.submit, loading && styles.submitDisabled]}
          onPress={
            mode === "login"
              ? onLogin
              : mode === "register"
              ? onRegister
              : mode === "forgot"
              ? onForgotPassword
              : onResetPassword
          }
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.submitText}>
              {mode === "login"
                ? "Sign in"
                : mode === "register"
                ? "Create account"
                : mode === "forgot"
                ? "Send reset request"
                : "Reset password"}
            </Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: "#f4f7f4" },
  scroll: { padding: 24, paddingBottom: 48 },
  brand: {
    fontSize: 28,
    fontWeight: "700",
    color: "#1c6b2d",
    marginTop: 24,
    marginBottom: 8,
  },
  sub: { fontSize: 16, color: "#444", marginBottom: 24 },
  row: { flexDirection: "row", gap: 10, marginBottom: 20 },
  chip: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#1c6b2d",
    alignItems: "center",
  },
  chipOn: { backgroundColor: "#1c6b2d" },
  chipText: { color: "#1c6b2d", fontWeight: "600" },
  chipTextOn: { color: "#fff", fontWeight: "600" },
  labelRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 4,
    marginBottom: 6,
  },
  labelPlain: {
    fontSize: 14,
    color: "#333",
    fontWeight: "600",
  },
  label: {
    fontSize: 14,
    color: "#333",
    marginBottom: 6,
    marginTop: 4,
    fontWeight: "600",
  },
  showPwd: {
    fontSize: 14,
    color: "#1565c0",
    fontWeight: "600",
  },
  input: {
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#c8d9c9",
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    marginBottom: 4,
  },
  typeRow: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 8 },
  typeChip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#1c6b2d",
  },
  typeChipOn: { backgroundColor: "#e8f5e9" },
  typeChipText: { color: "#1c6b2d", fontSize: 13 },
  typeChipTextOn: { color: "#1c6b2d", fontWeight: "700", fontSize: 13 },
  hint: { fontSize: 12, color: "#666", marginBottom: 8, marginTop: 4 },
  error: { color: "#b00020", marginTop: 12, marginBottom: 4 },
  success: { color: "#1b5e20", marginTop: 12, marginBottom: 4 },
  linkBtn: { marginTop: 10, alignSelf: "flex-start" },
  linkText: { color: "#1565c0", fontWeight: "600" },
  submit: {
    backgroundColor: "#1c6b2d",
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 16,
  },
  submitDisabled: { opacity: 0.7 },
  submitText: { color: "#fff", fontSize: 17, fontWeight: "600" },
});
