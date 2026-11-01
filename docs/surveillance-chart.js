(() => {
  "use strict";

  const root = document.querySelector("[data-surveillance-chart]");
  if (!root) return;

  const canvas = root.querySelector("canvas");
  const fallback = root.querySelector(".chart-fallback");
  const message = root.querySelector(".chart-message");
  const tooltip = root.querySelector(".chart-tooltip");
  const reset = root.querySelector("[data-reset-zoom]");
  const toggles = root.querySelector(".chart-toggles");
  const ctx = canvas.getContext("2d");
  const colors = ["#006d77", "#d1495b"];
  let data;
  let view = [0, 1];
  let dragging = null;
  let enabled = [];

  const format = new Intl.NumberFormat("nl-NL", { maximumFractionDigits: 0 });
  const margins = { left: 58, right: 18, top: 24, bottom: 38 };

  function visibleRows() {
    const count = data.observations.length;
    const start = Math.max(0, Math.floor(view[0] * (count - 1)));
    const end = Math.min(count, Math.ceil(view[1] * (count - 1)) + 1);
    return { rows: data.observations.slice(start, end), start };
  }

  function resize() {
    const ratio = window.devicePixelRatio || 1;
    const width = Math.max(320, root.clientWidth);
    const height = Math.min(480, Math.max(300, width * 0.52));
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    draw();
  }

  function bounds(rows, seriesIndex) {
    const key = data.series[seriesIndex].key;
    const values = rows.map(row => row[key]).filter(Number.isFinite);
    const max = Math.max(...values, 1);
    return [0, max * 1.08];
  }

  function draw() {
    if (!data) return;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    ctx.clearRect(0, 0, width, height);
    const plot = {
      x: margins.left, y: margins.top,
      width: width - margins.left - margins.right,
      height: height - margins.top - margins.bottom,
    };
    const { rows } = visibleRows();
    if (rows.length < 2) return;

    ctx.strokeStyle = "#d9e1e5";
    ctx.fillStyle = "#52616b";
    ctx.font = "12px system-ui, sans-serif";
    for (let tick = 0; tick <= 4; tick += 1) {
      const y = plot.y + plot.height * tick / 4;
      ctx.beginPath(); ctx.moveTo(plot.x, y); ctx.lineTo(plot.x + plot.width, y); ctx.stroke();
    }
    const dateTicks = [0, Math.floor((rows.length - 1) / 2), rows.length - 1];
    dateTicks.forEach((index, position) => {
      const x = plot.x + plot.width * index / (rows.length - 1);
      ctx.textAlign = position === 0 ? "left" : position === 2 ? "right" : "center";
      ctx.fillText(rows[index].date, x, height - 12);
    });

    data.series.forEach((series, seriesIndex) => {
      if (!enabled[seriesIndex]) return;
      const [, max] = bounds(rows, seriesIndex);
      ctx.strokeStyle = colors[seriesIndex];
      ctx.lineWidth = 2;
      ctx.beginPath();
      let open = false;
      rows.forEach((row, index) => {
        const value = row[series.key];
        if (!Number.isFinite(value)) { open = false; return; }
        const x = plot.x + plot.width * index / (rows.length - 1);
        const y = plot.y + plot.height * (1 - value / max);
        if (!open) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        open = true;
      });
      ctx.stroke();
      ctx.fillStyle = colors[seriesIndex];
      ctx.textAlign = seriesIndex === 0 ? "left" : "right";
      ctx.fillText(`max ${format.format(max)} ${series.unit}`, seriesIndex === 0 ? plot.x : plot.x + plot.width, plot.y - 7);
    });
  }

  function pointerIndex(event) {
    const rect = canvas.getBoundingClientRect();
    const { rows, start } = visibleRows();
    const fraction = Math.max(0, Math.min(1, (event.clientX - rect.left - margins.left) / (canvas.clientWidth - margins.left - margins.right)));
    return Math.min(data.observations.length - 1, start + Math.round(fraction * (rows.length - 1)));
  }

  canvas.addEventListener("pointermove", event => {
    if (dragging !== null) {
      const delta = (event.clientX - dragging) / canvas.clientWidth * (view[1] - view[0]);
      const width = view[1] - view[0];
      view[0] = Math.max(0, Math.min(1 - width, view[0] - delta));
      view[1] = view[0] + width;
      dragging = event.clientX; draw(); return;
    }
    const row = data.observations[pointerIndex(event)];
    const values = data.series.map((series, index) => enabled[index] && Number.isFinite(row[series.key])
      ? `${series.label}: ${format.format(row[series.key])} ${series.unit}` : null).filter(Boolean);
    tooltip.textContent = `${row.date} · ${values.join(" · ")}`;
  });
  canvas.addEventListener("pointerdown", event => { dragging = event.clientX; canvas.setPointerCapture(event.pointerId); });
  canvas.addEventListener("pointerup", () => { dragging = null; });
  canvas.addEventListener("wheel", event => {
    event.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const anchor = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
    const oldWidth = view[1] - view[0];
    const newWidth = Math.max(0.04, Math.min(1, oldWidth * (event.deltaY > 0 ? 1.18 : 0.82)));
    const center = view[0] + anchor * oldWidth;
    view[0] = Math.max(0, Math.min(1 - newWidth, center - anchor * newWidth));
    view[1] = view[0] + newWidth; draw();
  }, { passive: false });
  reset.addEventListener("click", () => { view = [0, 1]; draw(); });

  fetch("data/current-surveillance.json")
    .then(response => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); })
    .then(value => {
      data = value; enabled = data.series.map(() => true);
      data.series.forEach((series, index) => {
        const label = document.createElement("label");
        label.innerHTML = `<input type=\"checkbox\" checked> <span style=\"color:${colors[index]}\">●</span> ${series.label}${series.status === "calculated" ? " (berekend)" : ""}`;
        label.querySelector("input").addEventListener("change", event => { enabled[index] = event.target.checked; draw(); });
        toggles.appendChild(label);
      });
      root.classList.add("chart-ready"); fallback.hidden = true; message.hidden = true; resize();
    })
    .catch(error => { message.textContent = `Interactieve grafiek niet beschikbaar (${error.message}); de SVG-versie staat hieronder.`; });
  window.addEventListener("resize", resize);
})();
