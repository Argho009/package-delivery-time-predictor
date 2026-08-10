// js/history.js — Analytics & History page logic

let currentPage = 1;
let totalPages  = 1;

document.addEventListener("DOMContentLoaded", async () => {

  // ── Load charts ────────────────────────────────────────────
  try {
    const [traffic, weather] = await Promise.all([
      apiFetch("/analytics/traffic-impact"),
      apiFetch("/analytics/weather-impact"),
    ]);
    renderTrafficChart("trafficBarChart", traffic);
    renderWeatherChart("weatherBarChart", weather);
  } catch (e) {
    console.warn("Charts failed:", e.message);
  }

  // ── Load model comparison benchmark ─────────────────────────
  try {
    const cmp = await apiFetch("/analytics/model-comparison");
    renderModelBenchmark(cmp);
  } catch (e) {
    console.warn("Model comparison load failed:", e.message);
    const tbody = document.getElementById("model-benchmark-tbody");
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-muted" style="text-align:center;">Run models/train.py to generate benchmarks.</td></tr>`;
    }
  }

  // ── Load history table ─────────────────────────────────────
  await loadHistory(1);

  // ── Pagination buttons ─────────────────────────────────────
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");

  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      if (currentPage > 1) loadHistory(currentPage - 1);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      if (currentPage < totalPages) loadHistory(currentPage + 1);
    });
  }
});


function renderModelBenchmark(cmp) {
  const tbody = document.getElementById("model-benchmark-tbody");
  if (!tbody || !cmp.models) return;

  const best = cmp.best_model;
  tbody.innerHTML = Object.entries(cmp.models).map(([key, m]) => {
    const isBest = key === best;
    return `
      <tr>
        <td><strong>${modelName(key)}</strong> ${isBest ? '<span class="badge badge-low" style="margin-left:0.5rem">BEST</span>' : ''}</td>
        <td><strong style="color:var(--clr-primary-dark)">R² = ${m.r2.toFixed(3)}</strong></td>
        <td class="text-mono">${m.rmse.toFixed(2)}h</td>
        <td class="text-mono">${m.mae.toFixed(2)}h</td>
        <td class="text-mono">${(m.trained_on || 112665).toLocaleString()}</td>
      </tr>
    `;
  }).join("");
}


async function loadHistory(page) {
  currentPage = page;
  const tbody = document.getElementById("history-tbody");
  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="8" style="padding:2rem;text-align:center" class="text-muted">Loading page ${page}…</td></tr>`;
  }

  try {
    const data = await apiFetch(`/history?page=${page}&per_page=15`);
    totalPages = data.total_pages;

    renderTable(data.data);
    updatePaginationControls(data.page, data.total_pages, data.total);
  } catch (e) {
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="8" style="padding:2rem;text-align:center;color:var(--clr-danger)">⚠️ Failed to load records: ${e.message}</td></tr>`;
    }
  }
}


function renderTable(records) {
  const tbody = document.getElementById("history-tbody");
  if (!tbody) return;

  if (!records || !records.length) {
    tbody.innerHTML = `<tr><td colspan="8" style="padding:2rem;text-align:center" class="text-muted">No records found</td></tr>`;
    return;
  }

  tbody.innerHTML = records.map(r => {
    return `
    <tr>
      <td class="text-mono" style="font-size:0.8rem">${r.tracking_id || "—"}</td>
      <td>
        <strong>${r.origin_city}</strong>
        <span class="text-muted">→</span>
        <strong>${r.destination_city}</strong>
      </td>
      <td class="text-mono">${fmtNum(r.distance_km)} km</td>
      <td>${trafficBadge(r.traffic_level)}</td>
      <td class="text-mono">${fmtNum(r.package_weight_kg, 1)} kg</td>
      <td><span class="badge badge-mod">${r.shipping_mode || "ROAD"}</span></td>
      <td class="text-mono" style="font-weight:600; color:var(--clr-primary-dark);">${fmtHours(r.actual_time_hours)}</td>
      <td class="text-mono">${fmtHours(r.predicted_time_hours)}</td>
    </tr>`;
  }).join("");
}


function updatePaginationControls(page, pages, total) {
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const pageIndicator = document.getElementById("page-indicator");
  const countLabel = document.getElementById("records-count-label");

  if (prevBtn) prevBtn.disabled = (page <= 1);
  if (nextBtn) nextBtn.disabled = (page >= pages);
  if (pageIndicator) pageIndicator.textContent = `Page ${page} of ${pages.toLocaleString()}`;
  if (countLabel) countLabel.textContent = `Showing ${(total || 140832).toLocaleString()} records`;
}
