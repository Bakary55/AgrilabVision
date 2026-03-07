const API_BASE_URL = "http://127.0.0.1:8000";

const statusMessage = document.getElementById("statusMessage");
const registerForm = document.getElementById("registerForm");
const loginForm = document.getElementById("loginForm");
const registerMessage = document.getElementById("registerMessage");
const loginMessage = document.getElementById("loginMessage");
const logoutBtn = document.getElementById("logoutBtn");
const profileBox = document.getElementById("profile");
const sampleForm = document.getElementById("sampleForm");
const sampleMessage = document.getElementById("sampleMessage");
const samplesList = document.getElementById("samplesList");
const refreshSamplesBtn = document.getElementById("refreshSamplesBtn");
const recommendationBox = document.getElementById("recommendationBox");
const aiForm = document.getElementById("aiForm");
const aiMessage = document.getElementById("aiMessage");
const aiResult = document.getElementById("aiResult");

const samplesCache = {};

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.style.color = isError ? "#b00020" : "#1c6b2d";
}

function getToken() {
  return localStorage.getItem("access_token");
}

function setToken(token) {
  if (token) {
    localStorage.setItem("access_token", token);
  } else {
    localStorage.removeItem("access_token");
  }
}

function showMessage(el, message, isError = false) {
  el.textContent = message;
  el.style.color = isError ? "#b00020" : "#1c6b2d";
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const errorMsg = data.detail || "Request failed.";
    throw new Error(errorMsg);
  }
  return data;
}

async function checkStatus() {
  try {
    const data = await fetchJson(`${API_BASE_URL}/`);
    setStatus(`API status: ${data.status}`);
  } catch (error) {
    setStatus("API not reachable. Start the FastAPI server.", true);
  }
}

async function handleRegister(event) {
  event.preventDefault();
  showMessage(registerMessage, "");

  const formData = new FormData(registerForm);
  const payload = Object.fromEntries(formData.entries());
  payload.age = Number(payload.age);

  try {
    const user = await fetchJson(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    showMessage(registerMessage, `Welcome ${user.first_name}! You can now log in.`);
    registerForm.reset();
  } catch (error) {
    showMessage(registerMessage, error.message, true);
  }
}

async function handleLogin(event) {
  event.preventDefault();
  showMessage(loginMessage, "");

  const formData = new FormData(loginForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const data = await fetchJson(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    setToken(data.access_token);
    showMessage(loginMessage, "Login successful.");
    loginForm.reset();
    await loadProfile();
  } catch (error) {
    showMessage(loginMessage, error.message, true);
  }
}

function logout() {
  setToken(null);
  profileBox.textContent = "Not logged in.";
  logoutBtn.classList.add("hidden");
  showMessage(loginMessage, "Logged out.");
}

async function loadProfile() {
  const token = getToken();
  if (!token) {
    profileBox.textContent = "Not logged in.";
    logoutBtn.classList.add("hidden");
    return;
  }

  try {
    const user = await fetchJson(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    profileBox.textContent = `${user.first_name} ${user.last_name} (${user.user_type}) - ${user.email}`;
    logoutBtn.classList.remove("hidden");
  } catch (error) {
    logout();
  }
}

async function handleCreateSample(event) {
  event.preventDefault();
  showMessage(sampleMessage, "");

  const formData = new FormData(sampleForm);
  const payload = Object.fromEntries(formData.entries());
  payload.ph = Number(payload.ph);
  payload.moisture = Number(payload.moisture);
  payload.organic_matter = Number(payload.organic_matter);
  payload.clay = Number(payload.clay);
  payload.phosphate = Number(payload.phosphate);

  try {
    await fetchJson(`${API_BASE_URL}/soil-samples`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    showMessage(sampleMessage, "Sample saved.");
    sampleForm.reset();
    await loadSamples();
  } catch (error) {
    showMessage(sampleMessage, error.message, true);
  }
}

function getFertilityLabel(score) {
  if (score >= 75) return "High";
  if (score >= 50) return "Moderate";
  return "Low";
}

function renderSamples(samples) {
  if (!samples.length) {
    samplesList.textContent = "No samples found.";
    return;
  }

  samplesList.innerHTML = "";
  samples.forEach((sample) => {
    samplesCache[sample.id] = sample;
    const item = document.createElement("div");
    item.className = "sample-item";
    item.innerHTML = `
      <strong>Sample #${sample.id}</strong>
      <span>Farmer: ${sample.farmer_name || "N/A"}</span>
      <span>Location: ${sample.location || "N/A"}</span>
      <span>pH: ${sample.ph} | Moisture: ${sample.moisture}% | Clay: ${sample.clay}%</span>
      <div class="sample-actions">
        <button class="secondary" data-id="${sample.id}">View Recommendation</button>
      </div>
    `;
    const btn = item.querySelector("button");
    btn.addEventListener("click", () => loadRecommendation(sample));
    samplesList.appendChild(item);
  });
}

async function loadSamples() {
  try {
    const samples = await fetchJson(`${API_BASE_URL}/soil-samples`);
    renderSamples(samples);
  } catch (error) {
    samplesList.textContent = "Failed to load samples.";
  }
}

async function loadRecommendation(sample) {
  recommendationBox.textContent = "Loading recommendation...";
  try {
    const data = await fetchJson(
      `${API_BASE_URL}/soil-samples/${sample.id}/recommendation`
    );
    const fertilityLabel = getFertilityLabel(data.fertility_score);
    recommendationBox.innerHTML = `
      <strong>Moisture Level:</strong> ${sample.moisture}%<br />
      <strong>Soil Type:</strong> ${data.soil_type}<br />
      <strong>Fertility Score:</strong> ${data.fertility_score} (${fertilityLabel})<br />
      <strong>Recommended Crops:</strong> ${data.recommended_crops.join(", ")}<br />
      <strong>Fertilizer:</strong> ${data.fertilizer_suggestion}<br />
      <strong>Irrigation:</strong> ${data.irrigation_suggestion}<br />
      <strong>Notes:</strong> ${data.notes.join(" | ")}
    `;
  } catch (error) {
    recommendationBox.textContent = error.message;
  }
}

async function handleAiAnalysis(event) {
  event.preventDefault();
  showMessage(aiMessage, "");
  aiResult.textContent = "Analyzing photo...";

  const formData = new FormData(aiForm);
  const imageFile = formData.get("image");
  if (!imageFile || imageFile.size === 0) {
    showMessage(aiMessage, "Please select a soil photo.", true);
    aiResult.textContent = "No AI analysis yet.";
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/ai/soil-analyze`, {
      method: "POST",
      body: formData,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.detail || "AI analysis failed.");
    }

    aiResult.innerHTML = `
      <strong>Soil Type:</strong> ${data.soil_type}<br />
      <strong>Moisture:</strong> ${data.moisture_estimate}<br />
      <strong>Recommended Crops:</strong> ${data.recommended_crops.join(", ")}<br />
      <strong>Fertilizer (per crop):</strong> ${data.fertilizer_recommendations.join(" | ")}<br />
      <strong>Notes:</strong> ${data.notes.join(" | ")}
    `;
    showMessage(aiMessage, "Analysis completed.");
  } catch (error) {
    showMessage(aiMessage, error.message, true);
    aiResult.textContent = "No AI analysis yet.";
  }
}

registerForm.addEventListener("submit", handleRegister);
loginForm.addEventListener("submit", handleLogin);
logoutBtn.addEventListener("click", logout);
sampleForm.addEventListener("submit", handleCreateSample);
refreshSamplesBtn.addEventListener("click", loadSamples);
aiForm.addEventListener("submit", handleAiAnalysis);

checkStatus();
loadProfile();
loadSamples();
