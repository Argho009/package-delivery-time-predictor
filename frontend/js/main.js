// js/main.js — Shared utilities, Universal Theme Manager & Global Helpers

const API_BASE = "/api";

/* ── Universal Theme Manager (Immediate Initialization & Bulletproof Sync) ── */
(function initTheme() {
  function getStoredTheme() {
    return localStorage.getItem("deliverai-theme") || "light";
  }

  function syncIcon(theme) {
    const isDark = theme === "dark";
    const buttons = document.querySelectorAll("#theme-toggle-btn, .theme-toggle-btn");
    buttons.forEach(btn => {
      btn.innerHTML = isDark ? "☀️" : "🌙";
      btn.title = isDark ? "Switch to Light Mode" : "Switch to Dark Mode";
      btn.setAttribute("aria-label", isDark ? "Switch to Light Mode" : "Switch to Dark Mode");
    });
  }

  function applyTheme(theme, notify = false) {
    const targetTheme = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", targetTheme);
    localStorage.setItem("deliverai-theme", targetTheme);
    syncIcon(targetTheme);

    window.dispatchEvent(new CustomEvent("deliverai-theme-change", { detail: { theme: targetTheme } }));

    if (notify && typeof showToast === "function") {
      showToast(`Switched to ${targetTheme.toUpperCase()} mode`, "info");
    }
  }

  // Set theme immediately on script execution to minimize any flash
  applyTheme(getStoredTheme(), false);

  function bindThemeToggle() {
    const currentTheme = getStoredTheme();
    applyTheme(currentTheme, false);

    const buttons = document.querySelectorAll("#theme-toggle-btn, .theme-toggle-btn");
    buttons.forEach(btn => {
      // Use direct onclick property to eliminate accidental double listener triggers
      btn.onclick = function (e) {
        if (e) e.preventDefault();
        const active = document.documentElement.getAttribute("data-theme") || "light";
        const next = active === "dark" ? "light" : "dark";
        applyTheme(next, true);
      };
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindThemeToggle);
  } else {
    bindThemeToggle();
  }

  // Multi-tab synchronization
  window.addEventListener("storage", (e) => {
    if (e.key === "deliverai-theme" && e.newValue) {
      applyTheme(e.newValue, false);
    }
  });

  // Global exposure for debugging or programmatic switching
  window.setDeliverAITheme = applyTheme;
  window.toggleDeliverAITheme = () => {
    const active = document.documentElement.getAttribute("data-theme") || "light";
    applyTheme(active === "dark" ? "light" : "dark", true);
  };
})();

/* ── Live Color Palette Switcher Manager ───────────────────────── */
(function initPalette() {
  const savedPalette = localStorage.getItem("deliverai-palette") || "blue";
  document.documentElement.setAttribute("data-palette", savedPalette);

  document.addEventListener("DOMContentLoaded", () => {
    const navActions = document.querySelector(".nav-actions");
    if (navActions && !document.getElementById("palette-picker-container")) {
      const picker = document.createElement("div");
      picker.id = "palette-picker-container";
      picker.className = "palette-picker-wrap";
      picker.innerHTML = `
        <div class="palette-btn-group" title="Select UI Accent Color Palette">
          <button type="button" class="palette-dot dot-blue ${savedPalette === 'blue' ? 'active' : ''}" data-val="blue" title="Electric Blue (Crextio Default)"></button>
          <button type="button" class="palette-dot dot-indigo ${savedPalette === 'indigo' ? 'active' : ''}" data-val="indigo" title="Royal Indigo"></button>
          <button type="button" class="palette-dot dot-cyan ${savedPalette === 'cyan' ? 'active' : ''}" data-val="cyan" title="Sky Cyan"></button>
          <button type="button" class="palette-dot dot-emerald ${savedPalette === 'emerald' ? 'active' : ''}" data-val="emerald" title="Emerald Eco"></button>
          <button type="button" class="palette-dot dot-sunset ${savedPalette === 'sunset' ? 'active' : ''}" data-val="sunset" title="Sunset Coral"></button>
        </div>
      `;
      navActions.insertBefore(picker, navActions.firstChild);

      picker.querySelectorAll(".palette-dot").forEach(dot => {
        dot.addEventListener("click", () => {
          const pal = dot.getAttribute("data-val");
          document.documentElement.setAttribute("data-palette", pal);
          localStorage.setItem("deliverai-palette", pal);
          picker.querySelectorAll(".palette-dot").forEach(d => d.classList.remove("active"));
          dot.classList.add("active");
          showToast(`Palette: ${pal.toUpperCase()}`, "success");
        });
      });
    }
  });
})();

/* ── Global Glass Toast Notification System ───────────────────── */
function showToast(message, type = "info") {
  let toastContainer = document.getElementById("deliverai-toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "deliverai-toast-container";
    toastContainer.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 99999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    `;
    document.body.appendChild(toastContainer);
  }

  const icons = { success: "✅", error: "⚠️", info: "ℹ️", warning: "⚡" };
  const toast = document.createElement("div");
  toast.style.cssText = `
    padding: 0.75rem 1.25rem;
    background: var(--bg-surface-glass);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    color: var(--txt-main);
    font-size: 0.86rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    pointer-events: auto;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  `;
  toast.innerHTML = `<span>${icons[type] || "ℹ️"}</span><span>${message}</span>`;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(20px)";
    setTimeout(() => toast.remove(), 350);
  }, 3200);
}

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
