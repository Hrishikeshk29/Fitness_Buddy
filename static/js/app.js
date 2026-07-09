/* =============================================================================
   FITNESS BUDDY – APP.JS
   Global JS: dark mode, form enhancements, shared utilities
   ============================================================================= */

// ── Dark / Light Mode Toggle ─────────────────────────────────────────────────
(function () {
  const html = document.documentElement;
  const toggle = document.getElementById("themeToggle");
  const icon = document.getElementById("themeIcon");

  // Restore saved preference
  const saved = localStorage.getItem("fbTheme") || "light";
  html.setAttribute("data-theme", saved);
  if (icon) icon.className = saved === "dark" ? "bi bi-sun-fill" : "bi bi-moon-fill";

  if (toggle) {
    toggle.addEventListener("click", () => {
      const current = html.getAttribute("data-theme");
      const next = current === "dark" ? "light" : "dark";
      html.setAttribute("data-theme", next);
      localStorage.setItem("fbTheme", next);
      if (icon) icon.className = next === "dark" ? "bi bi-sun-fill" : "bi bi-moon-fill";
    });
  }
})();

// ── Auto-dismiss flash messages ───────────────────────────────────────────────
document.querySelectorAll(".alert").forEach((el) => {
  setTimeout(() => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
    if (bsAlert) bsAlert.close();
  }, 5000);
});

// ── Quick Action Buttons (dashboard) ────────────────────────────────────────
document.querySelectorAll(".quick-action-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const action = btn.dataset.action;
    const resultDiv = document.getElementById("quickActionResult");
    const resultText = document.getElementById("resultText");
    const resultBadge = document.getElementById("resultBadge");

    // Show loading
    resultDiv?.classList.remove("d-none");
    if (resultText) resultText.innerHTML = '<span class="text-muted"><em>🤖 AI agents working…</em></span>';
    if (resultBadge) resultBadge.textContent = "Processing…";

    // Disable all quick action buttons while loading
    document.querySelectorAll(".quick-action-btn").forEach(b => b.disabled = true);

    try {
      const res = await fetch("/api/quick-action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action }),
      });
      const data = await res.json();

      if (resultText) resultText.textContent = data.response || "No response received.";
      if (resultBadge) {
        const agentsLabel = (data.agents_used || []).join(", ") || "AI";
        resultBadge.textContent = "🤖 " + agentsLabel;
      }

      // Scroll result into view
      resultDiv?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } catch (err) {
      if (resultText) resultText.textContent = "Failed to connect to AI service. Please check your configuration.";
    } finally {
      document.querySelectorAll(".quick-action-btn").forEach(b => b.disabled = false);
    }
  });
});

// ── Close quick action result ────────────────────────────────────────────────
function closeQuickAction() {
  document.getElementById("quickActionResult")?.classList.add("d-none");
}
window.closeQuickAction = closeQuickAction;

// ── Bootstrap form validation ────────────────────────────────────────────────
document.querySelectorAll(".needs-validation").forEach((form) => {
  form.addEventListener("submit", (e) => {
    if (!form.checkValidity()) {
      e.preventDefault();
      e.stopPropagation();
    }
    form.classList.add("was-validated");
  });
});
