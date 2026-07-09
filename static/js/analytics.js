/* =============================================================================
   FITNESS BUDDY – ANALYTICS.JS
   Charts for the analytics page: weight, workouts, habits
   ============================================================================= */

// NOTE: progressRecords, workoutLogs, habitLogs are injected by the template
// as plain `const` variables — do NOT use window.* to reference them.

const isDark = document.documentElement.getAttribute("data-theme") === "dark";
const gridColor = isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)";
const tickColor = isDark ? "#8b96a5" : "#57606a";

// ── Weight Progress Chart ────────────────────────────────────────────────────
(function () {
  const canvas = document.getElementById("weightProgressChart");
  if (!canvas) return;
  if (typeof progressRecords === "undefined" || !progressRecords.length) return;

  const labels  = progressRecords.map(r => r.date  || "");
  const weights = progressRecords.map(r => r.weight || 0);
  const bmis    = progressRecords.map(r => r.bmi    || 0);

  new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Weight (kg)",
          data: weights,
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59,130,246,0.1)",
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          borderWidth: 2.5,
          yAxisID: "y",
        },
        {
          label: "BMI",
          data: bmis,
          borderColor: "#8b5cf6",
          backgroundColor: "rgba(139,92,246,0.05)",
          fill: false,
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 2,
          borderDash: [5, 3],
          yAxisID: "y1",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { position: "top", labels: { color: tickColor, font: { size: 12 } } },
      },
      scales: {
        x:  { grid: { color: gridColor }, ticks: { color: tickColor, font: { size: 11 }, maxTicksLimit: 10 } },
        y:  { grid: { color: gridColor }, ticks: { color: tickColor, font: { size: 11 }, callback: v => v + " kg" }, position: "left" },
        y1: { grid: { display: false },   ticks: { color: "#8b5cf6",  font: { size: 11 }, callback: v => "BMI " + v }, position: "right" },
      },
    },
  });
})();

// ── Workout Activity Bar Chart ────────────────────────────────────────────────
(function () {
  const canvas = document.getElementById("workoutActivityChart");
  if (!canvas) return;
  if (typeof workoutLogs === "undefined" || !workoutLogs.length) return;

  // Aggregate total duration per day (all logs, not only completed flag)
  const map = {};
  workoutLogs.forEach(l => {
    if (l.date) {
      map[l.date] = (map[l.date] || 0) + (l.duration || 30);
    }
  });

  const labels = Object.keys(map).sort();
  const values = labels.map(k => map[k]);

  if (!labels.length) return;

  new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Duration (min)",
        data: values,
        backgroundColor: "rgba(16,185,129,0.7)",
        borderColor: "#10b981",
        borderWidth: 1.5,
        borderRadius: 5,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y} min` } },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: tickColor, font: { size: 10 }, maxTicksLimit: 12 } },
        y: { grid: { color: gridColor }, ticks: { color: tickColor, font: { size: 11 }, callback: v => v + " min" } },
      },
    },
  });
})();

// ── Habit Trend Chart (Water + Sleep) ────────────────────────────────────────
(function () {
  const canvas = document.getElementById("habitTrendChart");
  if (!canvas) return;
  if (typeof habitLogs === "undefined" || !habitLogs.length) return;

  const labels = habitLogs.map(h => h.date || "");
  const water  = habitLogs.map(h => h.water_intake  || 0);
  const sleep  = habitLogs.map(h => h.sleep_hours   || 0);

  new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Water (L)",
          data: water,
          borderColor: "#06b6d4",
          backgroundColor: "rgba(6,182,212,0.1)",
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          borderWidth: 2,
          yAxisID: "y",
        },
        {
          label: "Sleep (hrs)",
          data: sleep,
          borderColor: "#8b5cf6",
          backgroundColor: "rgba(139,92,246,0.05)",
          fill: false,
          tension: 0.4,
          pointRadius: 4,
          borderWidth: 2,
          yAxisID: "y1",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { position: "top", labels: { color: tickColor, font: { size: 12 } } },
      },
      scales: {
        x:  { grid: { display: false }, ticks: { color: tickColor, font: { size: 10 }, maxTicksLimit: 12 } },
        y:  { grid: { color: gridColor }, ticks: { color: "#06b6d4", font: { size: 11 }, callback: v => v + "L"  }, position: "left"  },
        y1: { grid: { display: false },   ticks: { color: "#8b5cf6", font: { size: 11 }, callback: v => v + "h"  }, position: "right" },
      },
    },
  });
})();
