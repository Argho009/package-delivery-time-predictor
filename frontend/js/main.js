// js/main.js — Shared utilities used across all pages

const API_BASE = "http://localhost:5000/api";

/* ── Fetch wrapper ─────────────────────────────────────────────── */
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const defaults = {
    headers: { "Content-Type": "application/json" },
  };
  const res = await fetch(url, { ...defaults, ...options });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

/* ── Badge helpers ─────────────────────────────────────────────── */
const TRAFFIC_ICONS = {
  LOW: "🟢", MODERATE: "🟡", HIGH: "🔴", SEVERE: "🚨"
};
const WEATHER_ICONS = {
  CLEAR: "☀️", CLOUDY: "☁️", RAIN: "🌧️", HEAVY_RAIN: "⛈️",
  SNOW: "❄️", FOG: "🌫️", STORM: "⚡"
};
const PRIORITY_ICONS = {
  STANDARD: "📦", EXPRESS: "🚀", OVERNIGHT: "⚡"
};

function trafficBadge(level) {
  if (!level) return "—";
  const cls = level.toLowerCase().replace("_", "-");
  return `<span class="badge badge-${cls}">${TRAFFIC_ICONS[level] || ""} ${level}</span>`;
}

function weatherBadge(cond) {
  if (!cond) return "—";
  const cls = cond.toLowerCase().replace("_", "-");
  return `<span class="badge badge-${cls}">${WEATHER_ICONS[cond] || ""} ${cond.replace("_", " ")}</span>`;
}

function priorityBadge(p) {
  if (!p) return "—";
  return `<span class="badge badge-${p.toLowerCase()}">${PRIORITY_ICONS[p] || ""} ${p}</span>`;
}

/* ── Number formatters ─────────────────────────────────────────── */
function fmtHours(h) {
  if (h == null) return "—";
  const hrs  = Math.floor(h);
  const mins = Math.round((h - hrs) * 60);
  if (hrs === 0)  return `${mins}m`;
  if (mins === 0) return `${hrs}h`;
  return `${hrs}h ${mins}m`;
}

function fmtNum(n, decimals = 1) {
  if (n == null) return "—";
  return Number(n).toLocaleString("en-IN", { maximumFractionDigits: decimals });
}

function fmtDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString("en-IN", {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

/* ── Alert renderer ────────────────────────────────────────────── */
function showAlert(container, message, type = "error") {
  const icons = { error: "⚠️", success: "✅", info: "ℹ️", warning: "⚡" };
  container.innerHTML = `
    <div class="alert alert-${type}">
      ${icons[type] || ""} ${message}
    </div>`;
  container.classList.remove("d-none");
}

function clearAlert(container) {
  container.innerHTML = "";
  container.classList.add("d-none");
}

/* ── Set active nav link ───────────────────────────────────────── */
function setActiveNav() {
  const page = window.location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav-link").forEach(link => {
    const href = link.getAttribute("href");
    if (href && href.includes(page)) link.classList.add("active");
    else link.classList.remove("active");
  });
}

document.addEventListener("DOMContentLoaded", setActiveNav);

/* ── Counter animation ─────────────────────────────────────────── */
function animateCounter(el, target, duration = 1200, decimals = 0) {
  const start = performance.now();
  const from  = 0;
  function update(now) {
    const elapsed = Math.min((now - start) / duration, 1);
    const eased   = 1 - Math.pow(1 - elapsed, 3);
    const val     = from + (target - from) * eased;
    el.textContent = decimals > 0
      ? val.toFixed(decimals)
      : Math.round(val).toLocaleString("en-IN");
    if (elapsed < 1) requestAnimationFrame(update);
    else el.textContent = decimals > 0
      ? target.toFixed(decimals)
      : target.toLocaleString("en-IN");
  }
  requestAnimationFrame(update);
}

/* ── Model display names ────────────────────────────────────────── */
const MODEL_DISPLAY = {
  xgboost:            "XGBoost",
  random_forest:      "Random Forest",
  linear_regression:  "Linear Regression",
};

function modelName(key) {
  return MODEL_DISPLAY[key] || key;
}
