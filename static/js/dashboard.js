/* =============================================================================
   FITNESS BUDDY – DASHBOARD.JS
   Weight chart and dashboard-specific interactions
   ============================================================================= */

// ── Weight Progress Chart ─────────────────────────────────────────────────────
(function () {
  const canvas = document.getElementById("weightChart");
  if (!canvas) return;
  if (typeof weightData === "undefined" || !weightData.values || !weightData.values.length) return;

  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  const gridColor = isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)";
  const textColor = isDark ? "#8b96a5" : "#57606a";

  new Chart(canvas, {
    type: "line",
    data: {
      labels: weightData.labels,
      datasets: [
        {
          label: "Weight (kg)",
          data: weightData.values,
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59,130,246,0.08)",
          borderWidth: 2.5,
          pointBackgroundColor: "#3b82f6",
          pointBorderColor: "#fff",
          pointBorderWidth: 2,
          pointRadius: 5,
          tension: 0.35,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(0,0,0,0.75)",
          titleColor: "#fff",
          bodyColor: "#e5e7eb",
          borderColor: "rgba(255,255,255,0.1)",
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: (ctx) => ` ${ctx.parsed.y} kg`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: gridColor },
          ticks: { color: textColor, maxTicksLimit: 8, font: { size: 11 } },
        },
        y: {
          grid: { color: gridColor },
          ticks: {
            color: textColor,
            font: { size: 11 },
            callback: (v) => v + " kg",
          },
        },
      },
    },
  });
})();
