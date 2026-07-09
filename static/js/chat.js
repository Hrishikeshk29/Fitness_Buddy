/* =============================================================================
   FITNESS BUDDY – CHAT.JS
   Powers the real-time chat interface and agent interaction display
   ============================================================================= */

const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const typingIndicator = document.getElementById("typingIndicator");
const activeAgentsRow = document.getElementById("activeAgentsRow");
const activeAgentBadges = document.getElementById("activeAgentBadges");

// ── Scroll to bottom ─────────────────────────────────────────────────────────
function scrollToBottom(smooth = true) {
  if (chatMessages) {
    chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: smooth ? "smooth" : "instant" });
  }
}
scrollToBottom(false);

// ── Auto-resize textarea ─────────────────────────────────────────────────────
chatInput?.addEventListener("input", () => {
  chatInput.style.height = "auto";
  chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + "px";
});

// ── Send on Enter (Shift+Enter = new line) ───────────────────────────────────
chatInput?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
sendBtn?.addEventListener("click", sendMessage);

// ── Format AI response text ─────────────────────────────────────────────────
function formatResponse(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
}

// ── Append a message bubble ──────────────────────────────────────────────────
function appendMessage(role, content, agentsUsed = []) {
  const wrap = document.createElement("div");
  wrap.className = `message ${role === "user" ? "user-message" : "assistant-message"}`;

  const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  if (role === "assistant") {
    wrap.innerHTML = `
      <div class="message-avatar">🤖</div>
      <div class="message-bubble">
        ${formatResponse(content)}
        ${agentsUsed.length ? `<div class="agent-tag"><i class="bi bi-cpu me-1"></i>${agentsUsed.join(", ")}</div>` : ""}
      </div>
      <div class="message-time">${timeStr}</div>`;
  } else {
    wrap.innerHTML = `
      <div class="message-bubble user-bubble">${content.replace(/\n/g, "<br>")}</div>
      <div class="message-avatar user-avatar-msg">${window.CURRENT_USER_INITIAL || "U"}</div>
      <div class="message-time">${timeStr}</div>`;
  }

  // Insert before typing indicator
  chatMessages.insertBefore(wrap, typingIndicator);
  scrollToBottom();
}

// ── Show / hide typing indicator ────────────────────────────────────────────
function showTyping(agentsHint = "") {
  typingIndicator?.classList.remove("d-none");
  scrollToBottom();
}
function hideTyping() {
  typingIndicator?.classList.add("d-none");
}

// ── Update active agents display ────────────────────────────────────────────
function showActiveAgents(agents) {
  if (!agents || agents.length === 0) {
    activeAgentsRow?.classList.add("d-none");
    return;
  }
  activeAgentsRow?.classList.remove("d-none");
  if (activeAgentBadges) {
    const colors = {
      WorkoutPlanning: "primary",
      Nutrition: "warning",
      Motivation: "danger",
      HabitTracking: "success",
      ProgressEvaluation: "purple",
      UserProfile: "info",
      Orchestrator: "secondary",
    };
    activeAgentBadges.innerHTML = agents.map(a => {
      const key = Object.keys(colors).find(k => a.includes(k)) || "secondary";
      return `<span class="badge bg-${colors[key] || "secondary"} me-1">${a.replace("Agent", "")}</span>`;
    }).join("");
  }
}

// ── Core send function ───────────────────────────────────────────────────────
async function sendMessage() {
  const message = chatInput?.value.trim();
  if (!message) return;

  // Clear input & reset height
  chatInput.value = "";
  chatInput.style.height = "auto";
  sendBtn.disabled = true;

  // Append user message
  appendMessage("user", message);
  showTyping();
  hideAgents();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    hideTyping();
    appendMessage("assistant", data.response || "Sorry, I couldn't generate a response.", data.agents_used || []);
    showActiveAgents(data.agents_used || []);

    // Hide agents row after 6s
    setTimeout(hideAgents, 6000);
  } catch (err) {
    hideTyping();
    appendMessage("assistant", `⚠️ Connection error. Please ensure your IBM API credentials are configured in the .env file.\n\nError: ${err.message}`);
  } finally {
    sendBtn.disabled = false;
    chatInput?.focus();
  }
}

function hideAgents() {
  activeAgentsRow?.classList.add("d-none");
}

// ── Suggested prompt chips ───────────────────────────────────────────────────
function sendSuggestion(text) {
  if (chatInput) {
    chatInput.value = text;
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + "px";
    chatInput.focus();
    sendMessage();
  }
}
window.sendSuggestion = sendSuggestion;

// ── Clear chat ───────────────────────────────────────────────────────────────
document.getElementById("clearChatBtn")?.addEventListener("click", async () => {
  if (!confirm("Clear all chat history? This cannot be undone.")) return;
  try {
    await fetch("/api/chat/clear", { method: "POST" });
    // Remove all messages except typing indicator
    const msgs = chatMessages.querySelectorAll(".message:not(#typingIndicator)");
    msgs.forEach(m => m.remove());
  } catch (e) {
    console.error("Clear failed", e);
  }
});

// ── Weekly Report ────────────────────────────────────────────────────────────
document.getElementById("weeklyReportBtn")?.addEventListener("click", async () => {
  showTyping();
  try {
    const res = await fetch("/api/weekly-report");
    const data = await res.json();
    hideTyping();
    appendMessage("assistant", data.report || "Could not generate report.", data.agents_used || []);
    showActiveAgents(data.agents_used || []);
    setTimeout(hideAgents, 8000);
  } catch (err) {
    hideTyping();
    appendMessage("assistant", "⚠️ Could not generate weekly report. Please try again.");
  }
});
