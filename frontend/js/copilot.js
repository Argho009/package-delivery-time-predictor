/**
 * frontend/js/copilot.js — DeliverAI AI Logistics Copilot & Dedicated LLM Controller
 * Manages the floating drawer widget and full-page copilot workspace.
 */

const Copilot = (function () {
  let activeShipmentContext = null;
  let conversationHistory = [];
  let isSending = false;
  let llmStatus = { online: false, gpu: { detected: false } };

  // Helper to format basic markdown to HTML
  function formatMarkdown(text) {
    if (!text) return "";
    let html = text
      .replace(/^### (.*$)/gim, "<h3>$1</h3>")
      .replace(/^## (.*$)/gim, "<h3>$1</h3>")
      .replace(/^# (.*$)/gim, "<h3>$1</h3>")
      .replace(/\*\*(.*?)\*\*/gim, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/gim, "<em>$1</em>")
      .replace(/^\s*• (.*$)/gim, "<li>$1</li>")
      .replace(/^\s*\d+\. (.*$)/gim, "<li>$1</li>")
      .replace(/\n\n/gim, "<br/>");

    // Wrap list items in <ul> if any
    if (html.includes("<li>")) {
      html = html.replace(/(<li>.*<\/li>)/gis, "<ul>$1</ul>");
    }
    return html;
  }

  async function checkStatus() {
    try {
      const res = await fetch("/api/copilot/status");
      if (res.ok) {
        llmStatus = await res.json();
        updateStatusIndicators();
      }
    } catch (e) {
      console.warn("Copilot status check failed:", e);
    }
  }

  function updateStatusIndicators() {
    const pulseDot = document.getElementById("copilot-status-dot");
    const subTitle = document.getElementById("copilot-drawer-subtitle");
    const gpuNameEl = document.getElementById("copilot-gpu-name");
    const llmEngineEl = document.getElementById("copilot-engine-status");

    if (pulseDot) {
      pulseDot.style.backgroundColor = llmStatus.online ? "#10b981" : "#f59e0b";
    }

    if (subTitle) {
      if (llmStatus.online) {
        const prov = llmStatus.provider || "LM Studio";
        subTitle.textContent = `🟢 ${prov} GPU Active (${llmStatus.active_model})`;
      } else if (llmStatus.gpu && llmStatus.gpu.detected) {
        subTitle.textContent = `⚡ NVIDIA RTX 3050 GPU Ready • Built-In AI Engine`;
      } else {
        subTitle.textContent = `DeliverAI Logistics Intelligence Engine`;
      }
    }

    if (gpuNameEl && llmStatus.gpu) {
      gpuNameEl.textContent = llmStatus.gpu.detected ? llmStatus.gpu.name : "Direct CPU Mode";
    }

    if (llmEngineEl) {
      if (llmStatus.online) {
        const prov = llmStatus.provider || "LM Studio";
        llmEngineEl.innerHTML = `<span class="badge badge-success">🟢 ${prov} Online (${llmStatus.active_model})</span>`;
      } else {
        llmEngineEl.innerHTML = `<span class="badge badge-warning">Built-In Logistics AI (LM Studio Port 1234 Paused)</span>`;
      }
    }
  }

  function setShipmentContext(ctx) {
    activeShipmentContext = ctx;
    const ctxBar = document.getElementById("copilot-active-context");
    if (ctxBar && ctx) {
      const origin = ctx.origin || "Origin";
      const dest = ctx.destination || "Destination";
      const dist = ctx.distance_km ? `${Number(ctx.distance_km).toFixed(1)} km` : "";
      const hours = ctx.recommended_hours ? `${Number(ctx.recommended_hours).toFixed(1)}h` : "";
      ctxBar.innerHTML = `📍 <strong>${origin} ➔ ${dest}</strong> ${dist ? `(${dist} • ${hours})` : ""}`;
      ctxBar.classList.remove("d-none");
    }
  }

  async function sendMessage(text, containerId = "copilot-chat-messages") {
    if (!text || !text.trim() || isSending) return;
    const query = text.trim();
    isSending = true;

    // Append user message
    appendMessage("user", query, containerId);

    // Append typing indicator
    const typingId = "typing-" + Date.now();
    appendTypingIndicator(typingId, containerId);

    try {
      const res = await fetch("/api/copilot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: query,
          shipment_context: activeShipmentContext,
          history: conversationHistory,
        }),
      });

      removeTypingIndicator(typingId);

      if (res.ok) {
        const data = await res.json();
        const reply = data.reply || "Sorry, I couldn't generate a response.";
        conversationHistory.push({ role: "user", content: query });
        conversationHistory.push({ role: "assistant", content: reply });
        appendMessage("bot", reply, containerId);
      } else {
        appendMessage("bot", "⚠️ Error processing request. Please try again.", containerId);
      }
    } catch (err) {
      removeTypingIndicator(typingId);
      appendMessage("bot", "⚠️ Network connection error to Copilot service.", containerId);
    } finally {
      isSending = false;
    }
  }

  function appendMessage(role, content, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const msgDiv = document.createElement("div");
    msgDiv.className = `copilot-msg ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "copilot-avatar";
    avatar.textContent = role === "user" ? "👤" : "🤖";

    const bubble = document.createElement("div");
    bubble.className = "copilot-bubble";
    bubble.innerHTML = formatMarkdown(content);

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
  }

  function appendTypingIndicator(id, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const div = document.createElement("div");
    div.id = id;
    div.className = "copilot-msg bot";
    div.innerHTML = `
      <div class="copilot-avatar">🤖</div>
      <div class="copilot-bubble" style="color:var(--txt-muted); font-style:italic; display:flex; align-items:center; gap:0.4rem;">
        <span>⚡</span> <span>Thinking &amp; analyzing logistics telemetry...</span>
      </div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function initDrawer() {
    const trigger = document.getElementById("copilot-trigger-btn");
    const drawer = document.getElementById("copilot-drawer");
    const closeBtn = document.getElementById("copilot-close-btn");
    const input = document.getElementById("copilot-input");
    const sendBtn = document.getElementById("copilot-send-btn");
    const chips = document.querySelectorAll(".copilot-chip");

    if (trigger && drawer) {
      trigger.addEventListener("click", () => {
        drawer.classList.add("open");
        if (input) input.focus();
      });
    }

    if (closeBtn && drawer) {
      closeBtn.addEventListener("click", () => {
        drawer.classList.remove("open");
      });
    }

    if (sendBtn && input) {
      sendBtn.addEventListener("click", () => {
        sendMessage(input.value);
        input.value = "";
      });
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          sendMessage(input.value);
          input.value = "";
        }
      });
    }

    chips.forEach((chip) => {
      chip.addEventListener("click", () => {
        const prompt = chip.getAttribute("data-prompt") || chip.textContent;
        sendMessage(prompt);
      });
    });

    checkStatus();
  }

  function initStudio() {
    const studioInput = document.getElementById("studio-copilot-input");
    const studioSendBtn = document.getElementById("studio-copilot-send-btn");
    const studioChips = document.querySelectorAll(".studio-chip");

    if (studioSendBtn && studioInput) {
      studioSendBtn.addEventListener("click", () => {
        sendMessage(studioInput.value, "studio-chat-messages");
        studioInput.value = "";
      });
      studioInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          sendMessage(studioInput.value, "studio-chat-messages");
          studioInput.value = "";
        }
      });
    }

    studioChips.forEach((chip) => {
      chip.addEventListener("click", () => {
        const prompt = chip.getAttribute("data-prompt") || chip.textContent;
        sendMessage(prompt, "studio-chat-messages");
      });
    });

    checkStatus();
  }

  return {
    initDrawer,
    initStudio,
    setShipmentContext,
    sendMessage,
    checkStatus,
  };
})();

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("copilot-trigger-btn")) {
    Copilot.initDrawer();
  }
  if (document.getElementById("studio-chat-messages")) {
    Copilot.initStudio();
  }
});
