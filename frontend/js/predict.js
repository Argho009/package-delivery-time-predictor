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

    const selectedModeEl = document.getElementById("selected-shipping-mode");
    const shippingMode = selectedModeEl ? selectedModeEl.value : (form.shipping_mode ? form.shipping_mode.value : "ROAD");

    const payload = {
      origin:             form.origin.value.trim(),
      destination:        form.destination.value.trim(),
      package_weight_kg:  parseFloat(form.package_weight_kg.value),
      package_type:       form.package_type ? form.package_type.value : "MEDIUM",
      priority:           form.priority ? form.priority.value : "STANDARD",
      shipping_mode:      shippingMode,
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
      submitBtn.innerHTML = `<span>⚡</span><span>Calculate Delivery Prediction</span>`;
    }
  });

  // ── Multi-Modal Availability Scanner ─────────────────────────
  let modalCheckTimeout = null;

  async function checkModalAvailability() {
    const origInput = document.getElementById("orig-input");
    const destInput = document.getElementById("dest-input");
    const weightInput = document.getElementById("weight-input");
    if (!origInput || !destInput) return;

    const orig = origInput.value.trim();
    const dest = destInput.value.trim();
    const weight = weightInput ? weightInput.value : 5.0;
    if (!orig || !dest || orig.length < 2 || dest.length < 2) return;

    const scanBadge = document.getElementById("modal-scanning-badge");
    if (scanBadge) scanBadge.textContent = "Scanning direct routes…";

    try {
      const data = await apiFetch(`/routes/modal-availability?origin=${encodeURIComponent(orig)}&destination=${encodeURIComponent(dest)}&weight=${weight}`);
      if (data && data.options) {
        updateModalCards(data.options);
      }
    } catch (e) {
      console.warn("Modal availability check failed:", e);
    } finally {
      if (scanBadge) scanBadge.textContent = "Direct routes verified";
    }
  }

  function debounceModalCheck() {
    clearTimeout(modalCheckTimeout);
    modalCheckTimeout = setTimeout(checkModalAvailability, 350);
  }

  function updateModalCards(opts) {
    // Road
    if (opts.road) {
      const timeEl = document.getElementById("card-road-time");
      const badgeEl = document.getElementById("card-road-badge");
      if (timeEl && opts.road.estimated_hours) timeEl.textContent = `~${opts.road.estimated_hours}h`;
      if (badgeEl) badgeEl.textContent = opts.road.badge || "Direct Highway";
    }
    // Rail
    if (opts.rail) {
      const card = document.getElementById("mode-card-rail");
      const timeEl = document.getElementById("card-rail-time");
      const badgeEl = document.getElementById("card-rail-badge");
      const subEl = document.getElementById("card-rail-subtext");
      if (timeEl && opts.rail.estimated_hours) timeEl.textContent = `~${opts.rail.estimated_hours}h`;
      if (badgeEl) {
        badgeEl.textContent = opts.rail.badge || "Rail Network";
        badgeEl.className = `multimodal-badge ${opts.rail.direct_available ? 'badge-direct-ok' : 'badge-direct-info'}`;
      }
      if (subEl && opts.rail.co2_savings_pct) {
        subEl.textContent = `🌿 Saves ${opts.rail.co2_savings_pct}% CO2 vs Road`;
      }
    }
    // Air
    if (opts.air) {
      const card = document.getElementById("mode-card-air");
      const timeEl = document.getElementById("card-air-time");
      const badgeEl = document.getElementById("card-air-badge");
      const subEl = document.getElementById("card-air-subtext");
      if (timeEl) timeEl.textContent = opts.air.estimated_hours ? `~${opts.air.estimated_hours}h` : "N/A";
      if (badgeEl) {
        badgeEl.textContent = opts.air.badge || "Flight Transit";
        badgeEl.className = `multimodal-badge ${opts.air.direct_available ? 'badge-direct-ok' : 'badge-direct-no'}`;
      }
      if (card) {
        if (!opts.air.direct_available) {
          card.classList.add("disabled");
          // If Air was selected, auto-switch to ROAD
          const modeInput = document.getElementById("selected-shipping-mode");
          if (modeInput && modeInput.value === "AIR") {
            selectShippingMode("ROAD");
          }
        } else {
          card.classList.remove("disabled");
        }
      }
      if (subEl) {
        if (opts.air.direct_available && opts.air.time_saved_vs_road_hours > 0) {
          subEl.textContent = `⚡ Saves ~${opts.air.time_saved_vs_road_hours}h vs Road!`;
        } else {
          subEl.textContent = opts.air.description || "Flight unavailable";
        }
      }
    }
  }

  function selectShippingMode(mode) {
    const hidden = document.getElementById("selected-shipping-mode");
    if (hidden) hidden.value = mode;

    document.querySelectorAll(".multimodal-card").forEach(c => {
      c.classList.toggle("active", c.dataset.mode === mode);
    });
  }

  window.selectAndPredictMode = function(mode) {
    selectShippingMode(mode);
    if (form) {
      form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
    }
  };

  // ── Multi-Modal Card Clicks ──────────────────────────────────
  document.querySelectorAll(".multimodal-card").forEach(card => {
    card.addEventListener("click", () => {
      if (card.classList.contains("disabled")) return;
      selectShippingMode(card.dataset.mode);
    });
  });

  // ── Preset Chips ─────────────────────────────────────────────
  document.querySelectorAll(".preset-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const orig = chip.dataset.orig;
      const dest = chip.dataset.dest;
      const origInput = document.getElementById("orig-input");
      const destInput = document.getElementById("dest-input");
      if (origInput) origInput.value = orig;
      if (destInput) destInput.value = dest;
      debounceModalCheck();
    });
  });

  // ── Swap Route Button ────────────────────────────────────────
  const swapBtn = document.getElementById("swap-route-btn");
  if (swapBtn) {
    swapBtn.addEventListener("click", () => {
      const origInput = document.getElementById("orig-input");
      const destInput = document.getElementById("dest-input");
      if (origInput && destInput) {
        const tmp = origInput.value;
        origInput.value = destInput.value;
        destInput.value = tmp;
        debounceModalCheck();
      }
    });
  }

  // ── Input Listeners for Real-time Route Scanning ─────────────
  const origInput = document.getElementById("orig-input");
  const destInput = document.getElementById("dest-input");
  if (origInput) origInput.addEventListener("input", debounceModalCheck);
  if (destInput) destInput.addEventListener("input", debounceModalCheck);

  // ── Quick Weight Chips ───────────────────────────────────────
  const weightSlider = document.getElementById("weight-slider");
  const weightInput = document.getElementById("weight-input");
  const weightDisplay = document.getElementById("weight-display");

  document.querySelectorAll(".quick-weight-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".quick-weight-chip").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      const w = parseFloat(chip.dataset.weight);
      if (weightSlider) weightSlider.value = w;
      if (weightInput) weightInput.value = w;
      if (weightDisplay) weightDisplay.textContent = `${w.toFixed(1)} kg`;
      debounceModalCheck();
    });
  });

  // ── Weight Slider Sync ───────────────────────────────────────
  if (weightSlider && weightInput) {
    weightSlider.addEventListener("input", (e) => {
      const val = parseFloat(e.target.value);
      weightInput.value = val;
      if (weightDisplay) weightDisplay.textContent = `${val.toFixed(1)} kg`;
      // Update active chip state
      document.querySelectorAll(".quick-weight-chip").forEach(c => {
        c.classList.toggle("active", Math.abs(parseFloat(c.dataset.weight) - val) < 0.2);
      });
      debounceModalCheck();
    });
  }

  // ── Advanced Cargo Accordion Toggle ──────────────────────────
  const advToggle = document.getElementById("advanced-cargo-toggle");
  const advContent = document.getElementById("advanced-cargo-content");
  const advArrow = document.getElementById("advanced-cargo-arrow");
  if (advToggle && advContent) {
    advToggle.addEventListener("click", () => {
      const isHidden = advContent.classList.contains("d-none");
      advContent.classList.toggle("d-none", !isHidden);
      if (advArrow) advArrow.textContent = isHidden ? "▴" : "▾";
    });
  }

  // ── View Mode Switcher (Simple vs Studio) ────────────────────
  const btnSimple = document.getElementById("btn-mode-simple");
  const btnStudio = document.getElementById("btn-mode-studio");
  const btnSwitchToStudio = document.getElementById("btn-switch-to-studio");
  const simpleResultsView = document.getElementById("simple-results-view");
  const studioCockpitView = document.getElementById("studio-cockpit-view");

  function setViewMode(mode) {
    const isSimple = (mode === "simple");
    if (btnSimple) btnSimple.classList.toggle("active", isSimple);
    if (btnStudio) btnStudio.classList.toggle("active", !isSimple);

    if (simpleResultsView) simpleResultsView.classList.toggle("d-none", !isSimple);
    if (studioCockpitView) studioCockpitView.classList.toggle("d-none", isSimple);

    if (advContent) {
      advContent.classList.toggle("d-none", isSimple);
      if (advArrow) advArrow.textContent = isSimple ? "▾" : "▴";
    }

    if (!isSimple && mapInstance) {
      setTimeout(() => mapInstance.invalidateSize(), 80);
    }
    localStorage.setItem("deliverai-view-mode", mode);
  }

  if (btnSimple) btnSimple.addEventListener("click", () => setViewMode("simple"));
  if (btnStudio) btnStudio.addEventListener("click", () => setViewMode("studio"));
  if (btnSwitchToStudio) btnSwitchToStudio.addEventListener("click", () => setViewMode("studio"));

  // Initial scan and mode
  const savedMode = localStorage.getItem("deliverai-view-mode") || "simple";
  setViewMode(savedMode);
  setTimeout(checkModalAvailability, 400);

  // ── Tab Switcher ─────────────────────────────────────────────
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      const targetId = btn.dataset.tab;
      const pane = document.getElementById(targetId);
      if (pane) pane.classList.add("active");
      if (targetId === "tab-map" && mapInstance) {
        setTimeout(() => mapInstance.invalidateSize(), 50);
      }
    });
  });

  // ── Theme Toggle ─────────────────────────────────────────────
  const themeBtn = document.getElementById("theme-toggle-btn");
  if (themeBtn) {
    const savedTheme = localStorage.getItem("deliverai-theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    themeBtn.textContent = savedTheme === "light" ? "🌙" : "☀️";

    themeBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("deliverai-theme", next);
      themeBtn.textContent = next === "light" ? "🌙" : "☀️";
    });
  }

  let mapInstance = null;
  let currentPredictionData = null;
  let baselineRecHours = null;
  let transitMarker = null;
  let transitAnimId = null;

  // ── Render prediction result ────────────────────────────────
  function renderResult(data) {
    currentPredictionData = data;
    const { route, weather, predictions } = data;
    const rec = predictions.recommended_model;
    const recHours = predictions.recommended_hours;
    baselineRecHours = recHours;

    // Synchronize active shipment context with AI Copilot
    if (typeof Copilot !== "undefined" && Copilot.setShipmentContext) {
      Copilot.setShipmentContext({
        origin: route.origin_address || (form.origin ? form.origin.value : "Origin"),
        destination: route.destination_address || (form.destination ? form.destination.value : "Destination"),
        distance_km: route.distance_km,
        traffic_level: route.traffic_level,
        traffic_duration_min: route.traffic_duration_min,
        recommended_model: predictions.recommended_model,
        recommended_hours: predictions.recommended_hours,
        min_hours: predictions.min_hours != null ? predictions.min_hours : predictions.confidence_low,
        max_hours: predictions.max_hours != null ? predictions.max_hours : predictions.confidence_high,
        weather: weather,
        package_weight_kg: form.package_weight_kg ? form.package_weight_kg.value : 5.0,
        package_type: form.package_type ? form.package_type.value : "MEDIUM",
        priority: form.priority ? form.priority.value : "STANDARD",
        shipping_mode: form.shipping_mode ? form.shipping_mode.value : "ROAD",
        carbon_kg: data.sustainability ? data.sustainability.carbon_kg : null,
      });
    }

    // Main time display
    const resTime = document.getElementById("res-time");
    const resModel = document.getElementById("res-model");
    const resConf = document.getElementById("res-conf");

    const minH = predictions.min_hours != null ? predictions.min_hours : predictions.confidence_low;
    const maxH = predictions.max_hours != null ? predictions.max_hours : predictions.confidence_high;

    if (resTime) resTime.textContent = fmtHours(recHours);
    if (resModel) resModel.textContent = `Recommended: ${modelName(rec)}`;
    if (resConf) resConf.innerHTML = `Min: <strong>${fmtHours(minH)}</strong> &bull; Max: <strong>${fmtHours(maxH)}</strong> (Delivery Window)`;

    renderExplanation(data.explanation);
    renderSustainability(data.sustainability);
    setupWhatIf(data);
    setupWaybillModal(data);
    renderSLMRouter(data.slm_router, data);
    renderSimpleResults(data);

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

    // Calculate checkpoint travel speeds (km/h) in place of wind speed
    const totalDist = route.distance_km || 1.0;
    const totalHours = predictions.recommended_hours || 1.0;
    const overallSpeed = totalDist / totalHours;

    let speedOrigin = overallSpeed;
    let speedMidpoint = overallSpeed;
    let speedDest = overallSpeed;

    if (data.segments && data.segments.length > 0) {
      const segs = data.segments;
      const midIdx = Math.floor(segs.length / 2);
      
      let dist1 = 0, hours1 = 0;
      let dist2 = 0, hours2 = 0;
      
      for (let i = 0; i < segs.length; i++) {
        if (i < midIdx) {
          dist1 += segs[i].distance_km || 0;
          hours1 += segs[i].predicted_hours || 0;
        } else {
          dist2 += segs[i].distance_km || 0;
          hours2 += segs[i].predicted_hours || 0;
        }
      }
      
      speedOrigin = overallSpeed;
      if (hours1 > 0) speedMidpoint = dist1 / hours1;
      if (hours2 > 0) speedDest = dist2 / hours2;
    }

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
            <div class="checkpoint-cond">${cp.origin.weather_condition} • ${speedOrigin.toFixed(1)} km/h</div>
          </div>
          <div class="checkpoint-card">
            <div class="checkpoint-tag">🛣️ Midpoint</div>
            <div class="checkpoint-city">${cp.midpoint.location_name}</div>
            <div class="checkpoint-temp">${cp.midpoint.temperature_celsius}°C</div>
            <div class="checkpoint-cond">${cp.midpoint.weather_condition} • ${speedMidpoint.toFixed(1)} km/h</div>
          </div>
          <div class="checkpoint-card">
            <div class="checkpoint-tag">🏁 Destination</div>
            <div class="checkpoint-city">${cp.destination.location_name}</div>
            <div class="checkpoint-temp">${cp.destination.temperature_celsius}°C</div>
            <div class="checkpoint-cond">${cp.destination.weather_condition} • ${speedDest.toFixed(1)} km/h</div>
          </div>
        </div>
      `;
    }

    // Model breakdown — show per-model hours and highlight MIN/MAX/REC
    const mRf  = document.getElementById("m-rf");
    const mXgb = document.getElementById("m-xgb");
    const mLr  = document.getElementById("m-lr");

    function getModelBadge(val, modelKey) {
      if (val == null) return '';
      let badge = '';
      if (Math.abs(val - minH) < 0.01) {
        badge += ' <span class="badge badge-low" style="font-size:0.65rem; padding:1px 4px;">MIN</span>';
      }
      if (Math.abs(val - maxH) < 0.01) {
        badge += ' <span class="badge badge-high" style="font-size:0.65rem; padding:1px 4px;">MAX</span>';
      }
      if (modelKey === rec && !badge.includes("MIN") && !badge.includes("MAX")) {
        badge += ' <span class="badge badge-low" style="font-size:0.65rem; padding:1px 4px;">REC</span>';
      }
      return badge;
    }

    if (mRf)  mRf.innerHTML  = `${fmtHours(predictions.random_forest)}${getModelBadge(predictions.random_forest, 'random_forest')}`;
    if (mXgb) mXgb.innerHTML = `${fmtHours(predictions.xgboost)}${getModelBadge(predictions.xgboost, 'xgboost')}`;
    if (mLr)  mLr.innerHTML  = `${fmtHours(predictions.linear_regression)}${getModelBadge(predictions.linear_regression, 'linear_regression')}`;

    // Show ensemble dominant model and weights if available
    const ensembleBadge = document.getElementById("ensemble-badge");
    if (ensembleBadge && predictions.dominant_model) {
      const weights = predictions.model_weights || {};
      const wXgb = weights.xgboost ? (weights.xgboost * 100).toFixed(1) : '';
      const wRf  = weights.random_forest ? (weights.random_forest * 100).toFixed(1) : '';
      const wLr  = weights.linear_regression ? (weights.linear_regression * 100).toFixed(1) : '';
      ensembleBadge.innerHTML = `
        <div style="font-size:0.72rem; color:var(--clr-text-muted); margin-top:0.35rem; text-align:center;">
          Ensemble: XGB ${wXgb}% &bull; RF ${wRf}% &bull; LR ${wLr}%<br>
          <span style="color:var(--clr-primary-dark); font-weight:700;">Dominant: ${predictions.dominant_model.replace('_',' ').toUpperCase()}</span>
        </div>`;
    }

    // Render 25 km Segment Breakdown Table & Sum with SLM Model Assignments
    const segTable = document.getElementById("segment-table");
    const segSum   = document.getElementById("seg-total-sum");
    const totalSumHours = data.total_segmented_hours || predictions.recommended_hours;

    if (segSum) segSum.textContent = `Total Sum: ${fmtHours(totalSumHours)}`;

    if (segTable && data.segments && data.segments.length > 0) {
      const modelBadgeColor = {
        xgboost: '#6366f1',
        random_forest: '#10b981',
        linear_regression: '#f59e0b',
        catboost: '#e11d48',
        lightgbm: '#0284c7',
        bagging: '#d97706',
        knn: '#8b5cf6',
        voting: '#059669',
        hist_gradient_boosting: '#475569',
      };
      const modelShort = {
        xgboost: 'XGB',
        random_forest: 'RF',
        linear_regression: 'LR',
        catboost: 'CatBoost GPU',
        lightgbm: 'LightGBM',
        bagging: 'Bagging',
        knn: 'KNN',
        voting: 'Voting',
        hist_gradient_boosting: 'HistGB',
      };

      const slmLegMap = {};
      if (data.slm_router && data.slm_router.leg_assignments) {
        data.slm_router.leg_assignments.forEach(la => {
          slmLegMap[la.leg] = la;
        });
      }

      let rows = data.segments.map(s => {
        const w = s.weather || {};
        const slmLeg = slmLegMap[s.leg] || {};
        const assignedModel = slmLeg.assigned_model || s.dominant_model || 'voting';
        const color = modelBadgeColor[assignedModel] || '#6366f1';
        const short = modelShort[assignedModel] || assignedModel.toUpperCase();
        const reason = slmLeg.routing_reason || 'Corridor optimization';

        return `
          <div style="display:flex; align-items:center; justify-content:space-between; padding:0.45rem 0.25rem; border-bottom:1px solid rgba(0,0,0,0.06); font-size:0.82rem;" title="SLM Leg Decision: ${assignedModel} — ${reason}">
            <div>
              <strong>Leg ${s.leg}:</strong> <span style="font-weight:600; color:var(--clr-primary-dark);">${s.start_name}</span> &rarr; <span style="font-weight:600; color:var(--clr-primary-dark);">${s.end_name}</span>
              <span class="text-muted">(${s.distance_km} km)</span>
              <span style="background:${color}18; color:${color}; border:1px solid ${color}44; border-radius:4px; font-size:0.68rem; font-weight:700; padding:1px 6px; margin-left:4px;" title="SLM model for leg: ${reason}">🤖 ${short}</span>
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
            : `🛣️ ${wp.name || 'Checkpoint'} (~${Math.round(wp.km_offset)} km)`;

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

      // Initialize route transit simulation
      setupTransitSimulation(route);
    }
  }

  // ── Render Explainable AI Factor Attribution ────────────────
  function renderExplanation(explanation) {
    if (!explanation) return;
    const baseElem = document.getElementById("xai-base-time");
    const sumElem  = document.getElementById("xai-summary");
    const listElem = document.getElementById("xai-factors-list");

    if (baseElem && explanation.base_hours != null) {
      baseElem.textContent = `Baseline: ${explanation.base_hours.toFixed(2)}h`;
    }
    if (sumElem) {
      sumElem.textContent = explanation.summary || "Attribution completed.";
    }

    if (listElem && explanation.factors) {
      const maxImpact = Math.max(...explanation.factors.map(f => f.abs_impact || 0.1), 1.0);
      listElem.innerHTML = explanation.factors.map(f => {
        const pct = Math.min(Math.round((f.abs_impact / maxImpact) * 100), 100);
        const sign = f.impact_hours > 0 ? "+" : "";
        const dirClass = f.direction === "increase" ? "increase" : "decrease";
        return `
          <div class="factor-item">
            <span class="factor-name" title="${f.feature}">${f.feature}</span>
            <div class="factor-bar-wrapper">
              <div class="factor-bar ${dirClass}" style="width: ${pct}%;"></div>
            </div>
            <span class="factor-val ${dirClass}">${sign}${f.impact_hours.toFixed(2)}h</span>
          </div>
        `;
      }).join("");
    }
  }

  // ── Render Sustainability / Carbon Footprint ────────────────
  function renderSustainability(sustainability) {
    if (!sustainability) return;
    const co2Elem = document.getElementById("eco-co2");
    const treesElem = document.getElementById("eco-trees");
    const badgeElem = document.getElementById("eco-rating-badge");
    const tipElem = document.getElementById("eco-tip");

    if (co2Elem) co2Elem.textContent = `${sustainability.co2_kg} kg`;
    if (treesElem) treesElem.textContent = `${sustainability.trees_offset_needed} trees/yr`;
    if (badgeElem) {
      badgeElem.textContent = sustainability.rating || "B";
      badgeElem.style.background = sustainability.badge_color || "#10b981";
    }
    if (tipElem) tipElem.textContent = sustainability.tip || "";
  }

  // ── Setup Live What-If Scenario Simulator ───────────────────
  function setupWhatIf(data) {
    const whatifContainer = document.getElementById("whatif-container");
    if (!whatifContainer) return;

    let simState = {
      traffic_level: data.route.traffic_level || "MODERATE",
      priority: (data.package && data.package.priority) || "STANDARD",
      shipping_mode: (data.package && data.package.shipping_mode) || "ROAD",
    };

    function updateActiveButtons() {
      whatifContainer.querySelectorAll(".whatif-btn").forEach(btn => {
        const field = btn.getAttribute("data-field");
        const val = btn.getAttribute("data-value");
        if (simState[field] === val) {
          btn.classList.add("active");
        } else {
          btn.classList.remove("active");
        }
      });
    }

    updateActiveButtons();

    whatifContainer.querySelectorAll(".whatif-btn").forEach(btn => {
      btn.onclick = async () => {
        const field = btn.getAttribute("data-field");
        const val = btn.getAttribute("data-value");
        if (simState[field] === val) return;

        simState[field] = val;
        updateActiveButtons();

        try {
          const payload = {
            distance_km: data.route.distance_km,
            traffic_duration_min: data.route.traffic_duration_min,
            traffic_level: simState.traffic_level,
            package_weight_kg: data.package.weight_kg,
            package_type: data.package.type,
            priority: simState.priority,
            shipping_mode: simState.shipping_mode,
            recalc_traffic: field === "traffic_level",
          };

          const res = await apiFetch("/predict/what-if", {
            method: "POST",
            body: JSON.stringify(payload),
          });

          const newHours = res.predictions.recommended_hours;
          const delta = newHours - baselineRecHours;
          const resTime = document.getElementById("res-time");
          const resModel = document.getElementById("res-model");
          const resConf = document.getElementById("res-conf");

          if (resTime) resTime.textContent = fmtHours(newHours);
          if (resModel) resModel.textContent = `Simulated: ${modelName(res.predictions.recommended_model)}`;
          if (resConf) {
            resConf.innerHTML = `Min: <strong>${fmtHours(res.predictions.min_hours)}</strong> &bull; Max: <strong>${fmtHours(res.predictions.max_hours)}</strong> (Simulated Window)`;
          }

          const mRf = document.getElementById("m-rf");
          const mXgb = document.getElementById("m-xgb");
          const mLr = document.getElementById("m-lr");
          if (mRf) mRf.textContent = fmtHours(res.predictions.random_forest);
          if (mXgb) mXgb.textContent = fmtHours(res.predictions.xgboost);
          if (mLr) mLr.textContent = fmtHours(res.predictions.linear_regression);

          const deltaBox = document.getElementById("whatif-delta-box");
          const deltaText = document.getElementById("whatif-delta-text");
          if (deltaBox && deltaText) {
            deltaBox.classList.remove("d-none");
            if (Math.abs(delta) < 0.05) {
              deltaText.innerHTML = `⚡ Simulation matches baseline runtime.`;
            } else if (delta < 0) {
              deltaText.innerHTML = `⚡ <strong>${fmtHours(Math.abs(delta))} faster</strong> than initial estimate!`;
            } else {
              deltaText.innerHTML = `⏳ <strong>+${fmtHours(delta)} slower</strong> than initial estimate.`;
            }
          }

          renderExplanation(res.explanation);
          renderSustainability(res.sustainability);
        } catch (e) {
          console.error("What-if simulation failed:", e);
        }
      };
    });

    const resetBtn = document.getElementById("whatif-reset-btn");
    if (resetBtn) {
      resetBtn.onclick = () => {
        simState = {
          traffic_level: data.route.traffic_level || "MODERATE",
          priority: (data.package && data.package.priority) || "STANDARD",
          shipping_mode: (data.package && data.package.shipping_mode) || "ROAD",
        };
        updateActiveButtons();
        const deltaBox = document.getElementById("whatif-delta-box");
        if (deltaBox) deltaBox.classList.add("d-none");
        renderResult(data);
      };
    }
  }

  // ── Setup Waybill Modal ─────────────────────────────────────
  function setupWaybillModal(data) {
    const modal = document.getElementById("waybill-modal");
    const openBtn = document.getElementById("view-waybill-btn");
    const closeBtn1 = document.getElementById("close-waybill-btn");
    const closeBtn2 = document.getElementById("close-waybill-btn-2");

    if (!modal) return;

    function populateModal() {
      const trackId = (data.request_id || "TRK-" + Math.floor(100000 + Math.random() * 900000)).substring(0, 14).toUpperCase();
      const setTxt = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
      setTxt("wb-tracking-id", trackId);
      setTxt("wb-priority", data.package.priority);
      setTxt("wb-origin", data.origin.resolved || data.origin.input);
      setTxt("wb-dest", data.destination.resolved || data.destination.input);
      setTxt("wb-dist", `${data.route.distance_km} km`);
      setTxt("wb-weight", `${data.package.weight_kg} kg (${data.package.type})`);
      setTxt("wb-mode", data.package.shipping_mode);
      setTxt("wb-time", fmtHours(data.predictions.recommended_hours));
      setTxt("wb-eta", fmtHours(data.predictions.recommended_hours));
      setTxt("wb-conf", `Verified Window: ${fmtHours(data.predictions.min_hours)} – ${fmtHours(data.predictions.max_hours)}`);
      setTxt("wb-timestamp", `Generated: ${new Date().toLocaleString()}`);
    }

    if (openBtn) {
      openBtn.onclick = () => {
        populateModal();
        modal.classList.remove("d-none");
      };
    }
    if (closeBtn1) closeBtn1.onclick = () => modal.classList.add("d-none");
    if (closeBtn2) closeBtn2.onclick = () => modal.classList.add("d-none");
    modal.onclick = (e) => {
      if (e.target === modal) modal.classList.add("d-none");
    };
  }

  // ── Setup Route Transit Animation ───────────────────────────
  function setupTransitSimulation(route) {
    const simBtn = document.getElementById("simulate-transit-btn");
    const statusElem = document.getElementById("sim-status");
    if (!simBtn || !route.geometry || route.geometry.length === 0 || !mapInstance) return;

    simBtn.onclick = () => {
      if (transitAnimId) {
        cancelAnimationFrame(transitAnimId);
        transitAnimId = null;
      }
      if (transitMarker) {
        mapInstance.removeLayer(transitMarker);
        transitMarker = null;
      }

      const geom = route.geometry;
      simBtn.disabled = true;
      simBtn.innerHTML = `🚚 Simulating…`;
      if (statusElem) statusElem.textContent = "Transit in progress: 0%";

      const customIcon = L.divIcon({
        className: 'transit-vehicle-marker',
        html: `<div style="font-size:1.6rem; filter:drop-shadow(0 2px 5px rgba(0,0,0,0.4)); transform:scaleX(-1);">🚚</div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });

      transitMarker = L.marker(geom[0], { icon: customIcon }).addTo(mapInstance);

      const totalSteps = geom.length;
      const durationMs = Math.min(Math.max(totalSteps * 15, 3000), 7000);
      const startTime = performance.now();

      function animate(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / durationMs, 1.0);
        const idx = Math.min(Math.floor(progress * (totalSteps - 1)), totalSteps - 1);

        transitMarker.setLatLng(geom[idx]);
        if (statusElem) {
          statusElem.textContent = `Transit: ${Math.round(progress * 100)}% (En route)`;
        }

        if (progress < 1.0) {
          transitAnimId = requestAnimationFrame(animate);
        } else {
          transitMarker.setLatLng(geom[totalSteps - 1]);
          if (statusElem) statusElem.textContent = `✅ Delivered to Destination!`;
          simBtn.disabled = false;
          simBtn.innerHTML = `🚚 Simulate Transit`;
          transitAnimId = null;
        }
      }

      transitAnimId = requestAnimationFrame(animate);
    };
  }

  // ── Render SLM Dynamic Route & Weather Model Decision ─────────
  function renderSLMRouter(slm, data) {
    const slmContainer = document.getElementById("slm-router-container");
    if (!slmContainer) return;
    if (!slm) {
      slmContainer.classList.add("d-none");
      return;
    }
    slmContainer.classList.remove("d-none");

    const sourceBadge = document.getElementById("slm-source-badge");
    const chosenTag   = document.getElementById("slm-chosen-model-tag");
    const reasonText  = document.getElementById("slm-reasoning-text");
    const inputRoute  = document.getElementById("slm-input-route");
    const inputWeather= document.getElementById("slm-input-weather");
    const inputLegs   = document.getElementById("slm-input-legs");

    if (sourceBadge) {
      const src = slm.source || "DeliverAI SLM Router";
      sourceBadge.textContent = src;
      if (src.toLowerCase().includes("lm studio")) {
        sourceBadge.style.background = "rgba(16, 185, 129, 0.15)";
        sourceBadge.style.color = "#059669";
        sourceBadge.style.border = "1px solid rgba(16, 185, 129, 0.35)";
      } else {
        sourceBadge.style.background = "rgba(99, 102, 241, 0.15)";
        sourceBadge.style.color = "#4f46e5";
        sourceBadge.style.border = "1px solid rgba(99, 102, 241, 0.3)";
      }
    }

    if (chosenTag) {
      chosenTag.textContent = modelName(slm.chosen_model || "voting");
    }

    if (reasonText) {
      reasonText.textContent = slm.reason || "Evaluated highway corridor, local weather, and 25km intervals to optimize delivery accuracy.";
    }

    if (inputRoute && data.route) {
      const orig = (data.origin && data.origin.input) || "Origin";
      const dest = (data.destination && data.destination.input) || "Destination";
      inputRoute.textContent = `${orig} ➔ ${dest} (${fmtNum(data.route.distance_km)} km)`;
    }

    if (inputWeather && data.weather) {
      const cond = data.weather.condition || "CLEAR";
      const temp = data.weather.temperature_celsius != null ? `${data.weather.temperature_celsius}°C` : "";
      inputWeather.textContent = `${cond} ${temp ? `(${temp})` : ""}`;
    }

    if (inputLegs) {
      const legCount = slm.legs_evaluated || (data.segments ? data.segments.length : 1);
      inputLegs.textContent = `${legCount} Legs @ ~25 km`;
    }
  }

  // ── Render Simple Mode Results (For Everyday Users) ─────────
  function renderSimpleResults(data) {
    const { route, weather, predictions, multimodal_options, sustainability, package: pkg } = data;
    const recHours = predictions.recommended_hours || 1.0;
    const currentMode = (pkg && pkg.shipping_mode) ? pkg.shipping_mode.toUpperCase() : "ROAD";

    // 1. Calculate Estimated Scheduled Arrival Time
    const arrivalDate = new Date(Date.now() + recHours * 3600 * 1000);
    const dayStr = arrivalDate.toLocaleDateString("en-IN", { weekday: "short", month: "short", day: "numeric" });
    const timeStr = arrivalDate.toLocaleTimeString("en-IN", { hour: "numeric", minute: "2-digit", hour12: true });
    const arrivalEl = document.getElementById("simple-arrival-text");
    if (arrivalEl) {
      arrivalEl.textContent = `Expected by ${dayStr} at ~${timeStr}`;
    }

    // Carbon pill
    const carbPill = document.getElementById("simple-carbon-pill");
    if (carbPill && sustainability) {
      carbPill.textContent = `${sustainability.rating} • ${sustainability.rating_label} (${sustainability.co2_kg} kg CO2)`;
      carbPill.style.color = sustainability.badge_color || "#10b981";
      carbPill.style.borderColor = sustainability.badge_color || "#10b981";
    }

    // 2. Render 3-Way Direct Transport Comparison Cards
    const compGrid = document.getElementById("simple-comparison-grid");
    if (compGrid && multimodal_options && multimodal_options.options) {
      const opts = multimodal_options.options;
      const modes = [
        { key: "road", name: "Road Express", icon: "🚚", data: opts.road },
        { key: "rail", name: "Rail Freight", icon: "🚆", data: opts.rail },
        { key: "air", name: "Flight Cargo", icon: "✈️", data: opts.air },
      ];

      compGrid.innerHTML = modes.map(m => {
        const d = m.data;
        if (!d) return "";
        const isSelected = (currentMode === d.shipping_mode);
        const isAvail = d.direct_available;
        const hText = d.estimated_hours ? `${fmtHours(d.estimated_hours)}` : "—";
        const badgeClass = isAvail ? (isSelected ? "badge-direct-ok" : "badge-direct-info") : "badge-direct-no";
        
        let subInfo = d.description || "";
        if (m.key === "air" && isAvail && d.time_saved_vs_road_hours > 0) {
          subInfo = `⚡ Saves ~${d.time_saved_vs_road_hours}h vs Road!`;
        } else if (m.key === "rail" && isAvail && d.co2_savings_pct > 0) {
          subInfo = `🌿 Cuts CO2 by ${d.co2_savings_pct}%`;
        }

        return `
          <div class="mode-comparison-card ${isSelected ? 'current-active' : ''} ${!isAvail ? 'disabled' : ''}" data-switch-mode="${d.shipping_mode}">
            <div>
              <div class="mode-comparison-title">
                <span>${m.icon}</span>
                <span>${m.name}</span>
                ${isSelected ? '<span class="badge badge-low" style="font-size:0.65rem; margin-left:auto;">ACTIVE</span>' : ''}
              </div>
              <div class="mode-comparison-time">${hText}</div>
              <span class="multimodal-badge ${badgeClass}">${d.badge || ''}</span>
            </div>
            <div style="font-size:0.73rem; color:var(--txt-muted); margin-top:0.4rem; line-height:1.3;">
              ${subInfo}
            </div>
            ${!isSelected && isAvail ? `
              <button type="button" class="btn-secondary-action mt-2 w-full justify-center" style="font-size:0.74rem; padding:0.35rem 0.5rem;" onclick="event.stopPropagation(); selectAndPredictMode('${d.shipping_mode}')">
                Switch to ${m.name}
              </button>
            ` : ''}
          </div>
        `;
      }).join("");
    }

    // 3. Plain English Summary
    const sumEl = document.getElementById("simple-summary-text");
    if (sumEl) {
      const orig = (data.origin && (data.origin.resolved || data.origin.input)) || "Origin";
      const dest = (data.destination && (data.destination.resolved || data.destination.input)) || "Destination";
      const dist = route.distance_km || 100;
      const hours = fmtHours(recHours);
      const modeName = currentMode === "AIR" ? "Air Cargo Express" : (currentMode === "RAIL" ? "Indian Railways Freight" : "National Highway Road");
      
      let modeNote = "";
      if (currentMode === "AIR") {
        modeNote = `Because Air Cargo is selected, high-speed line-haul between airport hubs significantly compresses the delivery time.`;
      } else if (currentMode === "RAIL") {
        modeNote = `Using Rail transport leverages the electrified broad-gauge network, providing the most sustainable transit with up to 73% lower carbon emissions.`;
      } else {
        modeNote = `Road freight provides flexible point-to-point delivery directly along the highway corridor with current traffic conditions factored in.`;
      }

      sumEl.innerHTML = `
        Your parcel dispatch from <strong>${orig}</strong> to <strong>${dest}</strong> (${Math.round(dist)} km) is scheduled via <strong>${modeName}</strong>.<br>
        Estimated delivery is <strong>${hours}</strong>, arriving approximately <strong>${dayStr} at ${timeStr}</strong>.<br><br>
        ${modeNote}
      `;
    }
  }
});


