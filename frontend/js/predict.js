// js/predict.js — Prediction page logic

document.addEventListener("DOMContentLoaded", () => {
  const form            = document.getElementById("predict-form");
  const submitBtn       = document.getElementById("predict-btn");
  const alertBox        = document.getElementById("pred-alert");
  const placeholderView = document.getElementById("placeholder-view");
  const outputView      = document.getElementById("output-view");

  if (!form || !submitBtn) return;

  // ── Submit handler ──────────────────────────────────────────
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (alertBox) clearAlert(alertBox);

    submitBtn.disabled = true;
    submitBtn.innerHTML = `🔮 Calculating Estimate…`;

    const payload = {
      origin:             form.origin.value.trim(),
      destination:        form.destination.value.trim(),
      package_weight_kg:  parseFloat(form.package_weight_kg.value),
      package_type:       form.package_type.value,
      priority:           form.priority.value,
      shipping_mode:      form.shipping_mode ? form.shipping_mode.value : "ROAD",
    };

    try {
      const data = await apiFetch("/predict", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      renderResult(data);

      if (placeholderView) placeholderView.classList.add("d-none");
      if (outputView) outputView.classList.remove("d-none");
    } catch (err) {
      if (alertBox) showAlert(alertBox, err.message, "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `🔮 Calculate Delivery Estimate`;
    }
  });

  let mapInstance = null;

  // ── Render prediction result ────────────────────────────────
  function renderResult(data) {
    const { route, weather, predictions } = data;
    const rec = predictions.recommended_model;
    const recHours = predictions.recommended_hours;

    // Main time display
    const resTime = document.getElementById("res-time");
    const resModel = document.getElementById("res-model");
    const resConf = document.getElementById("res-conf");

    if (resTime) resTime.textContent = fmtHours(recHours);
    if (resModel) resModel.textContent = `Recommended: ${modelName(rec)}`;
    if (resConf) resConf.textContent = `${fmtHours(predictions.confidence_low)} – ${fmtHours(predictions.confidence_high)} (95% range)`;

    // Route & Traffic
    const resDist = document.getElementById("res-dist");
    const resTraffic = document.getElementById("res-traffic");
    if (resDist) resDist.textContent = `${fmtNum(route.distance_km)} km`;
    if (resTraffic) resTraffic.textContent = `Traffic: ${route.traffic_level} (${Math.round(route.traffic_duration_min)}m drive)`;

    // Overall Route Weather
    const resWeather = document.getElementById("res-weather");
    const resTemp = document.getElementById("res-temp");
    if (resWeather) resWeather.textContent = `${weather.condition}`;
    if (resTemp) resTemp.textContent = `Avg Temp: ${weather.avg_temperature_celsius || weather.temperature_celsius}°C • Max Wind: ${weather.wind_speed_kmh} km/h`;

    // Render Side-by-Side Weather Checkpoint Cards
    const cpContainer = document.getElementById("weather-checkpoints");
    if (cpContainer && weather.checkpoints) {
      const cp = weather.checkpoints;
      cpContainer.innerHTML = `
        <div class="grid-3">
          <div class="checkpoint-card">
            <div class="checkpoint-tag">📍 Origin</div>
            <div class="checkpoint-city">${cp.origin.location_name}</div>
            <div class="checkpoint-temp">${cp.origin.temperature_celsius}°C</div>
            <div class="checkpoint-cond">${cp.origin.weather_condition} • ${cp.origin.wind_speed_kmh} km/h</div>
          </div>
          <div class="checkpoint-card">
            <div class="checkpoint-tag">🛣️ Midpoint</div>
            <div class="checkpoint-city">${cp.midpoint.location_name}</div>
            <div class="checkpoint-temp">${cp.midpoint.temperature_celsius}°C</div>
            <div class="checkpoint-cond">${cp.midpoint.weather_condition} • ${cp.midpoint.wind_speed_kmh} km/h</div>
          </div>
          <div class="checkpoint-card">
            <div class="checkpoint-tag">🏁 Destination</div>
            <div class="checkpoint-city">${cp.destination.location_name}</div>
            <div class="checkpoint-temp">${cp.destination.temperature_celsius}°C</div>
            <div class="checkpoint-cond">${cp.destination.weather_condition} • ${cp.destination.wind_speed_kmh} km/h</div>
          </div>
        </div>
      `;
    }

    // Model breakdown
    const mRf  = document.getElementById("m-rf");
    const mXgb = document.getElementById("m-xgb");
    const mLr  = document.getElementById("m-lr");

    if (mRf)  mRf.textContent  = fmtHours(predictions.random_forest);
    if (mXgb) mXgb.textContent = fmtHours(predictions.xgboost);
    if (mLr)  mLr.textContent  = fmtHours(predictions.linear_regression);

    // Render 50-75 km Segment Breakdown Table & Sum
    const segTable = document.getElementById("segment-table");
    const segSum   = document.getElementById("seg-total-sum");
    const totalSumHours = data.total_segmented_hours || predictions.recommended_hours;

    if (segSum) segSum.textContent = `Total Sum: ${fmtHours(totalSumHours)}`;

    if (segTable && data.segments && data.segments.length > 0) {
      let rows = data.segments.map(s => {
        const w = s.weather || {};
        return `
          <div style="display:flex; align-items:center; justify-content:space-between; padding:0.4rem 0.2rem; border-bottom:1px solid rgba(0,0,0,0.06); font-size:0.82rem;">
            <div>
              <strong>Leg ${s.leg}:</strong> ${s.start_name} → ${s.end_name}
              <span class="text-muted">(${s.distance_km} km)</span>
            </div>
            <div style="text-align:right;">
              <span style="font-weight:600; color:var(--clr-primary-dark);">${fmtHours(s.predicted_hours)}</span>
              <span class="text-muted" style="font-size:0.75rem; margin-left:0.4rem;">${w.weather_condition || ''} ${w.temperature_celsius ? w.temperature_celsius + '°C' : ''}</span>
            </div>
          </div>
        `;
      }).join("");

      segTable.innerHTML = rows;
    } else if (segTable) {
      segTable.innerHTML = `<div class="text-muted" style="font-size:0.82rem;">Single direct segment delivery.</div>`;
    }

    // Initialize / Update Leaflet Map
    if (window.L && document.getElementById("route-map")) {
      if (mapInstance) {
        mapInstance.remove();
        mapInstance = null;
      }

      const mapElem = document.getElementById("route-map");
      mapInstance = L.map(mapElem);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      }).addTo(mapInstance);

      if (route.geometry && route.geometry.length > 0) {
        const polyline = L.polyline(route.geometry, {
          color: '#2196F3',
          weight: 5,
          opacity: 0.85
        }).addTo(mapInstance);

        mapInstance.fitBounds(polyline.getBounds(), { padding: [30, 30] });
      }

      // Draw route line and plot markers only for major ~50km checkpoints
      const allWaypoints = route.sampled_waypoints && route.sampled_waypoints.length > 0
        ? route.sampled_waypoints
        : (weather.checkpoints ? Object.values(weather.checkpoints) : []);

      const waypointsToPlot = allWaypoints.filter((wp, idx) => {
        if (idx === 0 || idx === allWaypoints.length - 1) return true;
        if (wp.is_major_marker) return true;
        if (wp.km_offset && Math.round(wp.km_offset) % 50 === 0) return true;
        return false;
      });

      waypointsToPlot.forEach((wp, idx) => {
        if (wp && wp.lat != null && wp.lon != null) {
          const title = wp.index === 0 ? `📍 Origin (${wp.name})`
            : idx === waypointsToPlot.length - 1 ? `🏁 Destination (${wp.name})`
            : `🛣️ Checkpoint ~${Math.round(wp.km_offset)} km (${wp.name || 'En route'})`;

          const offsetInfo = wp.km_offset != null ? `<br>Cumulative Distance: ${wp.km_offset} km` : '';

          L.marker([wp.lat, wp.lon])
            .addTo(mapInstance)
            .bindPopup(`<b>${title}</b>${offsetInfo}`);
        }
      });

      // Force map to recalculate layout after visibility change
      setTimeout(() => {
        if (mapInstance) {
          mapInstance.invalidateSize();
          if (route.geometry && route.geometry.length > 0) {
            const polyline = L.polyline(route.geometry);
            mapInstance.fitBounds(polyline.getBounds(), { padding: [30, 30] });
          }
        }
      }, 300);
    }
  }
});
