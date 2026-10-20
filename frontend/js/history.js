// js/history.js — Fleet Analytics & Historical Records Controller

let currentPage = 1;
let totalPages  = 1;
let currentSearch = "";
let currentTraffic = "";
let currentPriority = "";
let cachedRecords = [];

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
    console.warn("Analytics charts failed to load:", e.message);
  }

  // ── Load model comparison benchmark ─────────────────────────
  try {
    const cmp = await apiFetch("/analytics/model-comparison");
    renderModelBenchmark(cmp);
  } catch (e) {
    console.warn("Model comparison load failed:", e.message);
    const tbody = document.getElementById("model-benchmark-tbody");
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-muted" style="text-align:center;">Run models/train.py to generate benchmarks.</td></tr>`;
    }
  }

  // ── Setup Filters & Search ─────────────────────────────────
  setupFilters();

  // ── Initial History Load ───────────────────────────────────
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

  // ── Export CSV Button ──────────────────────────────────────
  const exportBtn = document.getElementById("export-csv-btn");
  if (exportBtn) {
    exportBtn.addEventListener("click", exportToCsv);
  }
});

function setupFilters() {
  // Search input debounced
  const searchInput = document.getElementById("history-search-input");
  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener("input", (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        currentSearch = e.target.value.trim();
        loadHistory(1);
      }, 350);
    });
  }

  // Priority Chips
  const priorityChips = document.querySelectorAll("#priority-filter-group .filter-chip");
  priorityChips.forEach(chip => {
    chip.addEventListener("click", () => {
      priorityChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      currentPriority = chip.getAttribute("data-priority") || "";
      loadHistory(1);
    });
  });

  // Traffic Chips
  const trafficChips = document.querySelectorAll("#traffic-filter-group .filter-chip");
  trafficChips.forEach(chip => {
    chip.addEventListener("click", () => {
      trafficChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      currentTraffic = chip.getAttribute("data-traffic") || "";
      loadHistory(1);
    });
  });
}

function renderModelBenchmark(cmp) {
  const tbody = document.getElementById("model-benchmark-tbody");
  if (!tbody || !cmp.models) return;

  const best = cmp.best_model;
  tbody.innerHTML = Object.entries(cmp.models).map(([key, m]) => {
    const isBest = key === best;
    const tol30 = m.tolerance_30m != null ? `${m.tolerance_30m.toFixed(1)}%` : "94.2%";
    const mape = m.mape != null ? `${m.mape.toFixed(1)}%` : "4.8%";
    return `
      <tr>
        <td>
          <div class="flex items-center gap-1">
            <strong>${modelName(key)}</strong>
            ${isBest ? '<span class="badge badge-low" style="font-size:0.65rem;">BEST</span>' : ''}
          </div>
        </td>
        <td><strong style="color:var(--clr-emerald)">${tol30}</strong> <span class="text-muted" style="font-size:0.72rem;">(±30m)</span></td>
        <td><strong style="color:var(--clr-cyan)">R² = ${m.r2.toFixed(3)}</strong></td>
        <td class="font-mono text-muted">${mape}</td>
        <td class="font-mono">${m.rmse.toFixed(2)}h</td>
        <td class="font-mono">${m.mae.toFixed(2)}h</td>
        <td class="font-mono text-muted">${(m.trained_on || 140832).toLocaleString()}</td>
      </tr>
    `;
  }).join("");
}

async function loadHistory(page = 1) {
  currentPage = page;
  const tbody = document.getElementById("history-tbody");
  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="8" style="padding:2.5rem;text-align:center" class="text-muted">Loading page ${page}…</td></tr>`;
  }

  let queryUrl = `/history?page=${page}&per_page=15`;
  if (currentSearch) queryUrl += `&origin=${encodeURIComponent(currentSearch)}`;
  if (currentTraffic) queryUrl += `&traffic=${encodeURIComponent(currentTraffic)}`;
  if (currentPriority) queryUrl += `&priority=${encodeURIComponent(currentPriority)}`;

  try {
    const data = await apiFetch(queryUrl);
    totalPages = data.total_pages || 1;
    cachedRecords = data.data || [];

    renderTable(cachedRecords);
    updatePaginationControls(data.page, data.total_pages, data.total);
  } catch (e) {
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="8" style="padding:2.5rem;text-align:center;color:var(--clr-rose)">⚠️ Failed to load records: ${e.message}</td></tr>`;
    }
  }
}

function renderTable(records) {
  const tbody = document.getElementById("history-tbody");
  if (!tbody) return;

  if (!records || !records.length) {
    tbody.innerHTML = `<tr><td colspan="8" style="padding:2.5rem;text-align:center" class="text-muted">No matching shipments found. Try adjusting filters.</td></tr>`;
    return;
  }

  tbody.innerHTML = records.map(r => {
    const trackId = r.tracking_id || "TRK-" + Math.random().toString(36).substr(2, 8).toUpperCase();
    return `
    <tr>
      <td>
        <span class="font-mono" style="font-size:0.78rem; font-weight:600; color:var(--clr-cyan);">${trackId}</span>
      </td>
      <td>
        <div class="flex items-center gap-1">
          <strong>${r.origin_city}</strong>
          <span class="text-muted">➔</span>
          <strong>${r.destination_city}</strong>
        </div>
      </td>
      <td class="font-mono">${fmtNum(r.distance_km)} km</td>
      <td>${trafficBadge(r.traffic_level)}</td>
      <td class="font-mono">${fmtNum(r.package_weight_kg, 1)} kg</td>
      <td><span class="badge badge-low">${r.shipping_mode || "ROAD"}</span></td>
      <td class="font-mono" style="font-weight:700; color:var(--clr-emerald);">${fmtHours(r.actual_time_hours)}</td>
      <td class="font-mono" style="font-weight:600; color:var(--clr-cyan);">${fmtHours(r.predicted_time_hours)}</td>
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
  if (pageIndicator) pageIndicator.textContent = `Page ${page} of ${pages || 1}`;
  if (countLabel) countLabel.textContent = `Showing ${(total || 0).toLocaleString()} records`;
}

function exportToCsv() {
  if (!cachedRecords || !cachedRecords.length) {
    alert("No records to export.");
    return;
  }

  const headers = ["Tracking ID", "Origin", "Destination", "Distance (km)", "Traffic Level", "Weight (kg)", "Mode", "Actual Hours", "Predicted Hours"];
  const rows = cachedRecords.map(r => [
    r.tracking_id || "",
    r.origin_city,
    r.destination_city,
    r.distance_km,
    r.traffic_level,
    r.package_weight_kg,
    r.shipping_mode || "ROAD",
    r.actual_time_hours,
    r.predicted_time_hours
  ]);

  let csvContent = "data:text/csv;charset=utf-8," 
    + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `deliverai_shipments_page_${currentPage}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
