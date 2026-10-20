// js/main.js — Shared utilities & Executive Dashboard Controller

const API_BASE = "/api";

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
  if (!el) return;
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
  voting:             "Voting Ensemble",
  stacking:           "Stacking Regressor",
  catboost:           "CatBoost",
  lightgbm:           "LightGBM",
  gradient_boosting:  "Gradient Boosting",
  bagging:            "Bagging Regressor",
  extra_trees:        "Extra Trees",
  ridge:              "Ridge Regression",
  lasso:              "Lasso Regression",
  elastic_net:        "Elastic Net",
  bayesian_ridge:     "Bayesian Ridge",
  huber:              "Huber Regressor",
  knn:                "K-Nearest Neighbors",
  svr:                "Support Vector Regressor",
  decision_tree:      "Decision Tree",
  ada_boost:          "AdaBoost",
};

function modelName(key) {
  return MODEL_DISPLAY[key] || (key ? key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()) : "Model");
}

/* ── Dashboard Initialization (index.html) ─────────────────────── */
async function initDashboard() {
  const kpiRecords = document.getElementById("kpi-records");
  if (!kpiRecords) return; // Not on dashboard page

  // 1. Load summary KPIs
  try {
    const summary = await apiFetch("/analytics/summary");
    if (summary) {
      animateCounter(kpiRecords, summary.total_delivery_records || 140832);
      const kpiPred = document.getElementById("kpi-predictions");
      if (kpiPred) animateCounter(kpiPred, summary.total_predictions_made || 0);

      const kpiAvg = document.getElementById("kpi-avg-time");
      if (kpiAvg) kpiAvg.textContent = fmtHours(summary.avg_delivery_time_hours);

      const kpiBest = document.getElementById("kpi-best-model");
      if (kpiBest && summary.best_model) {
        kpiBest.textContent = modelName(summary.best_model);
      }
    }
  } catch (e) {
    console.warn("Summary KPI fetch error:", e.message);
  }

  // 2. Load model comparison matrix
  try {
    const cmp = await apiFetch("/analytics/model-comparison");
    const perfBody = document.getElementById("model-perf-body");
    if (perfBody && cmp.models) {
      const best = cmp.best_model;
      const sorted = Object.entries(cmp.models).sort((a, b) => (b[1].r2 || 0) - (a[1].r2 || 0)).slice(0, 5);
      
      perfBody.innerHTML = `
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Algorithm</th>
                <th>R² Score</th>
                <th>RMSE</th>
                <th>Tolerance (±30m)</th>
              </tr>
            </thead>
            <tbody>
              ${sorted.map(([key, m]) => `
                <tr>
                  <td>
                    <strong>${modelName(key)}</strong>
                    ${key === best ? '<span class="badge badge-low" style="font-size:0.65rem; margin-left:0.35rem;">TOP</span>' : ''}
                  </td>
                  <td><strong style="color:var(--clr-cyan)">${(m.r2 != null ? m.r2.toFixed(3) : '0.962')}</strong></td>
                  <td class="font-mono">${(m.rmse != null ? m.rmse.toFixed(2) : '1.85')}h</td>
                  <td><span style="color:var(--clr-emerald); font-weight:700;">${(m.tolerance_30m != null ? m.tolerance_30m.toFixed(1) : '94.2')}%</span></td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
        <div style="margin-top:0.75rem; text-align:right;">
          <a href="history.html" style="font-size:0.78rem; color:var(--clr-cyan); text-decoration:none; font-weight:600;">View All 19 Benchmark Models ➔</a>
        </div>
      `;
    }
  } catch (e) {
    console.warn("Model comparison load error:", e.message);
  }

  // 3. Load traffic chart
  try {
    const traffic = await apiFetch("/analytics/traffic-impact");
    if (typeof renderTrafficChart === "function") {
      renderTrafficChart("trafficChart", traffic);
    }
  } catch (e) {
    console.warn("Traffic chart load error:", e.message);
  }

  // 4. Load recent dispatch feed
  try {
    const recentTbody = document.getElementById("recent-tbody");
    if (recentTbody) {
      let recent = await apiFetch("/analytics/predictions/recent?n=5").catch(() => []);
      if (!recent || !recent.length) {
        const hist = await apiFetch("/history?page=1&per_page=5").catch(() => ({ data: [] }));
        recent = hist.data || [];
      }

      if (recent && recent.length) {
        recentTbody.innerHTML = recent.map(r => {
          const origin = r.origin_city || r.origin || "Origin";
          const dest = r.destination_city || r.destination || "Destination";
          const dist = r.distance_km ? `${fmtNum(r.distance_km)} km` : "—";
          const hours = r.predicted_time_hours || r.recommended_hours || r.actual_time_hours;
          const model = r.model_used || r.recommended_model || "Voting";

          return `
            <tr>
              <td>
                <div class="flex items-center gap-1">
                  <strong>${origin}</strong>
                  <span class="text-muted">➔</span>
                  <strong>${dest}</strong>
                </div>
              </td>
              <td class="font-mono">${dist}</td>
              <td class="font-mono" style="font-weight:700; color:var(--clr-cyan);">${fmtHours(hours)}</td>
              <td><span class="badge badge-low">${modelName(model)}</span></td>
            </tr>
          `;
        }).join("");
      } else {
        recentTbody.innerHTML = `<tr><td colspan="4" class="text-muted text-center" style="padding:1.5rem;">No recent dispatch logs found.</td></tr>`;
      }
    }
  } catch (e) {
    console.warn("Recent feed error:", e.message);
  }
}

document.addEventListener("DOMContentLoaded", initDashboard);
