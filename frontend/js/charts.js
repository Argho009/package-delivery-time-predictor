// js/charts.js — Chart.js chart renderers (shared across pages)

// ── Global Chart.js defaults ────────────────────────────────────
Chart.defaults.color = "#94a3b8";
Chart.defaults.borderColor = "rgba(255,255,255,0.06)";
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size   = 12;

const CHART_PALETTE = [
  "#3b82f6", "#8b5cf6", "#10b981", "#f59e0b",
  "#ef4444", "#06b6d4", "#ec4899", "#84cc16",
];

// ── Traffic impact bar chart ────────────────────────────────────
function renderTrafficChart(canvasId, trafficData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !trafficData.length) return;

  const ORDER  = ["LOW", "MODERATE", "HIGH", "SEVERE"];
  const sorted = ORDER.map(lvl => trafficData.find(r => r.traffic_level === lvl))
                      .filter(Boolean);

  const colors = {
    LOW:      "#10b981",
    MODERATE: "#f59e0b",
    HIGH:     "#ef4444",
    SEVERE:   "#dc2626",
  };

  new Chart(canvas, {
    type: "bar",
    data: {
      labels: sorted.map(r => r.traffic_level),
      datasets: [{
        label: "Avg Delivery Time (hours)",
        data:  sorted.map(r => r.avg_hours),
        backgroundColor: sorted.map(r => colors[r.traffic_level] + "88"),
        borderColor:     sorted.map(r => colors[r.traffic_level]),
        borderWidth: 1.5,
        borderRadius: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.parsed.y.toFixed(2)} hours (${sorted[ctx.dataIndex].count} deliveries)`,
          },
        },
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: "rgba(255,255,255,0.04)" },
          ticks: { callback: v => `${v}h` },
        },
      },
    },
  });
}

// ── Weather impact bar chart ────────────────────────────────────
function renderWeatherChart(canvasId, weatherData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !weatherData.length) return;

  const colors = {
    CLEAR:      "#fbbf24",
    CLOUDY:     "#94a3b8",
    RAIN:       "#60a5fa",
    HEAVY_RAIN: "#3b82f6",
    SNOW:       "#e2e8f0",
    FOG:        "#78716c",
    STORM:      "#7c3aed",
  };

  const icons = {
    CLEAR:"☀️",CLOUDY:"☁️",RAIN:"🌧️",HEAVY_RAIN:"⛈️",
    SNOW:"❄️",FOG:"🌫️",STORM:"⚡"
  };

  new Chart(canvas, {
    type: "bar",
    data: {
      labels: weatherData.map(r => `${icons[r.weather_condition] || ""} ${r.weather_condition.replace("_"," ")}`),
      datasets: [{
        label: "Avg Delivery Time (hours)",
        data:  weatherData.map(r => r.avg_hours),
        backgroundColor: weatherData.map(r => (colors[r.weather_condition] || "#3b82f6") + "88"),
        borderColor:     weatherData.map(r => colors[r.weather_condition] || "#3b82f6"),
        borderWidth: 1.5,
        borderRadius: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.parsed.y.toFixed(2)} hours (${weatherData[ctx.dataIndex].count} deliveries)`,
          },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxRotation: 30 } },
        y: {
          grid: { color: "rgba(255,255,255,0.04)" },
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
          <tr style="${key === best ? 'background:rgba(59,130,246,0.06)' : ''}">
            <td class="fw-600">${modelName(key)}</td>
            <td class="text-mono">${m.rmse.toFixed(4)}</td>
            <td class="text-mono">${m.mae.toFixed(4)}</td>
            <td class="text-mono ${m.r2 > 0.8 ? 'text-success' : m.r2 > 0.6 ? 'text-warning' : 'text-danger'}">${m.r2.toFixed(4)}</td>
            <td class="text-mono">${(m.trained_on || 0).toLocaleString()}</td>
            <td>${key === best ? '<span class="badge badge-low">🏆 BEST</span>' : '<span class="badge badge-moderate">Active</span>'}</td>
          </tr>`).join("")}
        </tbody>
      </table>
    </div>
    <p class="fs-sm text-muted mt-3">
      RMSE = Root Mean Square Error · MAE = Mean Absolute Error · R² closer to 1.0 = better fit
    </p>`;
}
