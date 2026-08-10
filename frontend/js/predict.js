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

    // Destination Weather
    const resWeather = document.getElementById("res-weather");
    const resTemp = document.getElementById("res-temp");
    if (resWeather) resWeather.textContent = `${weather.condition} (${weather.description})`;
    if (resTemp) resTemp.textContent = `${weather.temperature_celsius}°C • Wind: ${weather.wind_speed_kmh} km/h`;

    // Model breakdown
    const mRf  = document.getElementById("m-rf");
    const mXgb = document.getElementById("m-xgb");
    const mLr  = document.getElementById("m-lr");

    if (mRf)  mRf.textContent  = fmtHours(predictions.random_forest);
    if (mXgb) mXgb.textContent = fmtHours(predictions.xgboost);
    if (mLr)  mLr.textContent  = fmtHours(predictions.linear_regression);
  }
});
