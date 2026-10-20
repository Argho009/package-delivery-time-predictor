// js/charts.js — High-Performance Chart.js renderers with instance lifecycle management

// ── Global Chart.js defaults ────────────────────────────────────
Chart.defaults.color = "#94A3B8";
Chart.defaults.borderColor = "rgba(148, 163, 184, 0.12)";
Chart.defaults.font.family = "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif";
Chart.defaults.font.size   = 12;

const CHART_PALETTE = [
  "#2196F3", "#0D47A1", "#10b981", "#f59e0b",
  "#ef4444", "#06b6d4", "#ec4899", "#84cc16",
];

// Active Chart instances cache to prevent canvas collision / memory leaks
const _chartInstances = {};

function _destroyChart(canvasId) {
  if (_chartInstances[canvasId]) {
    try {
      _chartInstances[canvasId].destroy();
    } catch (e) {
      console.warn("Chart destroy warning:", e);
    }
    delete _chartInstances[canvasId];
  }
}

// ── Traffic impact bar chart ────────────────────────────────────
function renderTrafficChart(canvasId, trafficData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !trafficData || !trafficData.length) return;

  _destroyChart(canvasId);

  const ORDER  = ["LOW", "MODERATE", "HIGH", "SEVERE"];
  const sorted = ORDER.map(lvl => trafficData.find(r => r.traffic_level === lvl))
                      .filter(Boolean);

  const colors = {
    LOW:      "#10b981",
    MODERATE: "#f59e0b",
    HIGH:     "#ef4444",
    SEVERE:   "#0D47A1",
  };

  _chartInstances[canvasId] = new Chart(canvas, {
    type: "bar",
    data: {
      labels: sorted.map(r => r.traffic_level),
      datasets: [{
        label: "Avg Delivery Time (hours)",
        data:  sorted.map(r => r.avg_hours),
        backgroundColor: sorted.map(r => (colors[r.traffic_level] || "#2196F3") + "33"),
        borderColor:     sorted.map(r => colors[r.traffic_level] || "#2196F3"),
        borderWidth: 2,
        borderRadius: 8,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 800,
        easing: "easeOutQuart",
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(13, 71, 161, 0.95)",
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: ctx => `${ctx.parsed.y.toFixed(2)} hours (${sorted[ctx.dataIndex].count} deliveries)`,
          },
        },
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: "rgba(13, 71, 161, 0.06)" },
          ticks: { callback: v => `${v}h` },
        },
      },
    },
  });
}

// ── Weather impact bar chart ────────────────────────────────────
function renderWeatherChart(canvasId, weatherData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !weatherData || !weatherData.length) return;

  _destroyChart(canvasId);

  const colors = {
    CLEAR:      "#fbbf24",
    CLOUDY:     "#64748b",
    RAIN:       "#60a5fa",
    HEAVY_RAIN: "#2196F3",
    SNOW:       "#93c5fd",
    FOG:        "#94a3b8",
    STORM:      "#0D47A1",
  };

  const icons = {
    CLEAR:"☀️",CLOUDY:"☁️",RAIN:"🌧️",HEAVY_RAIN:"⛈️",
    SNOW:"❄️",FOG:"🌫️",STORM:"⚡"
  };

  _chartInstances[canvasId] = new Chart(canvas, {
    type: "bar",
    data: {
      labels: weatherData.map(r => `${icons[r.weather_condition] || ""} ${r.weather_condition.replace("_"," ")}`),
      datasets: [{
        label: "Avg Delivery Time (hours)",
        data:  weatherData.map(r => r.avg_hours),
        backgroundColor: weatherData.map(r => (colors[r.weather_condition] || "#2196F3") + "33"),
        borderColor:     weatherData.map(r => colors[r.weather_condition] || "#2196F3"),
        borderWidth: 2,
        borderRadius: 8,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 800,
        easing: "easeOutQuart",
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(13, 71, 161, 0.95)",
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: ctx => `${ctx.parsed.y.toFixed(2)} hours (${weatherData[ctx.dataIndex].count} deliveries)`,
          },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxRotation: 30 } },
        y: {
          grid: { color: "rgba(13, 71, 161, 0.06)" },
          ticks: { callback: v => `${v}h` },
        },
      },
    },
  });
}

// ── Model Comparison radar / table ──────────────────────────────
function renderModelComparison(containerId, cmpData) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const best = cmpData.best_model;
  const models = cmpData.models;

  container.innerHTML = `
    <div style="overflow-x:auto">
      <table>
        <thead>
          <tr>
            <th>Model</th>
            <th>RMSE (hours)</th>
            <th>MAE (hours)</th>
            <th>R² Score</th>
            <th>Training Samples</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${Object.entries(models).map(([key, m]) => `
          <tr style="${key === best ? 'background:rgba(33, 150, 243, 0.08)' : ''}">
            <td class="fw-600">${modelName(key)}</td>
            <td class="text-mono">${m.rmse.toFixed(4)}</td>
            <td class="text-mono">${m.mae.toFixed(4)}</td>
            <td class="text-mono" style="font-weight:700; color:${m.r2 > 0.8 ? 'var(--clr-success)' : m.r2 > 0.6 ? 'var(--clr-warning)' : 'var(--clr-danger)'}">${m.r2.toFixed(4)}</td>
            <td class="text-mono">${(m.trained_on || 0).toLocaleString()}</td>
            <td>${key === best ? '<span class="badge badge-low">🏆 BEST</span>' : '<span class="badge badge-mod">Active</span>'}</td>
          </tr>`).join("")}
        </tbody>
      </table>
    </div>
    <p class="text-muted" style="font-size:0.82rem; margin-top:0.75rem;">
      RMSE = Root Mean Square Error · MAE = Mean Absolute Error · R² closer to 1.0 = higher accuracy
    </p>`;
}

