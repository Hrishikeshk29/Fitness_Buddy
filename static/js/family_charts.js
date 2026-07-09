/* =============================================================================
   FITNESS BUDDY – FAMILY_CHARTS.JS
   Family Health Dashboard: 4 comparison charts + AI insights trigger
   ============================================================================= */

// familyData is injected by the template as a const array of member objects

const isDark = document.documentElement.getAttribute("data-theme") === "dark";
const grid   = isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)";
const tick   = isDark ? "#8b96a5" : "#57606a";

// Palette per member (cycles)
const COLORS = [
  "#3b82f6","#10b981","#f59e0b","#ef4444",
  "#8b5cf6","#06b6d4","#f97316","#ec4899",
];

const names = (typeof familyData !== "undefined") ? familyData.map(m => m.name) : [];

// ── Shared chart defaults ────────────────────────────────────────────────────
const barDefaults = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: tick, font: { size: 11 } } },
    y: { grid: { color: grid },    ticks: { color: tick, font: { size: 11 } } },
  },
};

// ── 1. BMI Comparison ────────────────────────────────────────────────────────
(function () {
  const canvas = document.getElementById("bmiChart");
  if (!canvas || !names.length) return;

  const bmis = familyData.map(m => m.bmi || 0);
  const bgColors = familyData.map((_, i) => COLORS[i % COLORS.length] + "cc");
  const borderColors = familyData.map((_, i) => COLORS[i % COLORS.length]);

  new Chart(canvas, {
    type: "bar",
    data: {
      labels: names,
      datasets: [{
        label: "BMI",
        data: bmis,
        backgroundColor: bgColors,
        borderColor: borderColors,
        borderWidth: 2,
        borderRadius: 8,
      }],
    },
    options: {
      ...barDefaults,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` BMI ${ctx.parsed.y}` } },
        annotation: {}, // placeholder
      },
      scales: {
        ...barDefaults.scales,
        y: {
          ...barDefaults.scales.y,
          min: 10,
          ticks: { color: tick, font: { size: 11 }, callback: v => v + "" },
        },
      },
    },
  });

  // Draw reference lines via plugin-free approach — overlay text
  const ctx = canvas.getContext("2d");
})();

// ── 2. Fitness Score Comparison ──────────────────────────────────────────────
(function () {
  const canvas = document.getElementById("fitnessScoreChart");
  if (!canvas || !names.length) return;

  const scores = familyData.map(m => m.fitness_score || 0);

  new Chart(canvas, {
    type: "bar",
    data: {
      labels: names,
      datasets: [{
        label: "Fitness Score",
        data: scores,
        backgroundColor: familyData.map((_, i) => COLORS[i % COLORS.length] + "bb"),
        borderColor: familyData.map((_, i) => COLORS[i % COLORS.length]),
        borderWidth: 2,
        borderRadius: 8,
      }],
    },
    options: {
      ...barDefaults,
      scales: {
        ...barDefaults.scales,
        y: { ...barDefaults.scales.y, min: 0, max: 100, ticks: { color: tick, font: { size: 11 }, callback: v => v + "/100" } },
      },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` Score: ${ctx.parsed.y}/100` } },
      },
    },
  });
})();

// ── 3. Workout Completion % ──────────────────────────────────────────────────
(function () {
  const canvas = document.getElementById("workoutCompletionChart");
  if (!canvas || !names.length) return;

  const rates = familyData.map(m => m.workout_completion_rate || 0);

  new Chart(canvas, {
    type: "bar",
    data: {
      labels: names,
      datasets: [{
        label: "Completion %",
        data: rates,
        backgroundColor: familyData.map((_, i) => COLORS[i % COLORS.length] + "aa"),
        borderColor: familyData.map((_, i) => COLORS[i % COLORS.length]),
        borderWidth: 2,
        borderRadius: 8,
      }],
    },
    options: {
      ...barDefaults,
      scales: {
        ...barDefaults.scales,
        y: { ...barDefaults.scales.y, min: 0, max: 100, ticks: { color: tick, font: { size: 11 }, callback: v => v + "%" } },
      },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y}% completion` } },
      },
    },
  });
})();

// ── 4. Weight Progress (multi-line) ──────────────────────────────────────────
(function () {
  const canvas = document.getElementById("weightProgressChart");
  if (!canvas || !names.length) return;

  // Collect all unique date labels across all members
  const allDates = [...new Set(
    familyData.flatMap(m => (m.weight_history || []).map(h => h.date))
  )].sort();

  if (!allDates.length) return;

  const datasets = familyData.map((m, i) => {
    const histMap = {};
    (m.weight_history || []).forEach(h => { histMap[h.date] = h.weight; });
    const data = allDates.map(d => histMap[d] || null);
    const color = COLORS[i % COLORS.length];
    return {
      label: m.name,
      data,
      borderColor: color,
      backgroundColor: color + "15",
      fill: false,
      tension: 0.4,
      pointRadius: 5,
      pointBorderColor: "#fff",
      pointBorderWidth: 2,
      borderWidth: 2.5,
      spanGaps: true,
    };
  });

  new Chart(canvas, {
    type: "line",
    data: { labels: allDates, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { position: "top", labels: { color: tick, font: { size: 11 }, boxWidth: 12 } },
        tooltip: { callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y} kg` } },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: tick, font: { size: 10 } } },
        y: { grid: { color: grid }, ticks: { color: tick, font: { size: 11 }, callback: v => v + " kg" } },
      },
    },
  });
})();

// ── AI Insights Generation ───────────────────────────────────────────────────
function generateInsights() {
  const placeholder  = document.getElementById("insightsPlaceholder");
  const result       = document.getElementById("insightsResult");
  const loading      = document.getElementById("insightsLoading");
  const insightsText = document.getElementById("insightsText");
  const agentBadges  = document.getElementById("agentBadges");
  const btn          = document.getElementById("generateInsightsBtn");

  // Show loading, hide others
  placeholder?.classList.add("d-none");
  result?.classList.add("d-none");
  loading?.classList.remove("d-none");
  if (btn) btn.disabled = true;

  // Animate agent working chips sequentially
  ["aw1","aw2","aw3","aw4"].forEach((id, i) => {
    const el = document.getElementById(id);
    if (el) {
      el.classList.remove("agent-active");
      setTimeout(() => el.classList.add("agent-active"), i * 600);
    }
  });

  fetch("/api/family-insights", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
    .then(r => r.json())
    .then(data => {
      loading?.classList.add("d-none");
      result?.classList.remove("d-none");
      agentBadges?.classList.remove("d-none");

      // Format the text
      const raw = data.insights || "No insights generated.";
      if (insightsText) {
        insightsText.innerHTML = raw
          .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
          .replace(/\*(.*?)\*/g, "<em>$1</em>")
          .replace(/^(#{1,3})\s(.+)$/gm, (_, h, t) => `<h6 class="fw-bold mt-3 mb-1">${t}</h6>`)
          .replace(/^[-•]\s(.+)$/gm, "<li class='mb-1'>$1</li>")
          .replace(/(<li[\s\S]*?<\/li>)/g, "<ul class='ps-3 mb-2'>$1</ul>")
          .replace(/\n\n/g, "<br>")
          .replace(/\n/g, "<br>");
      }
    })
    .catch(err => {
      loading?.classList.add("d-none");
      result?.classList.remove("d-none");
      if (insightsText) {
        insightsText.innerHTML = `<div class="alert alert-warning mb-0">
          <i class="bi bi-exclamation-triangle me-2"></i>
          Could not generate insights. Please check your IBM API credentials.
          <br><small class="text-muted">${err.message}</small>
        </div>`;
      }
    })
    .finally(() => {
      if (btn) btn.disabled = false;
    });
}

document.getElementById("generateInsightsBtn")?.addEventListener("click", generateInsights);
document.getElementById("regenerateBtn")?.addEventListener("click", generateInsights);
