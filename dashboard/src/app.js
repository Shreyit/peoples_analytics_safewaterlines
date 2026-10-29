"use strict";
(() => {
  const D = window.DASHBOARD_DATA;
  if (!D) { document.body.textContent = "The aggregate data snapshot could not be loaded. Rebuild the dashboard and open dist/index.html."; return; }
  const $ = id => document.getElementById(id);
  const esc = value => String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const pct = value => Number(value).toFixed(1) + "%";
  const mean = value => Number(value).toFixed(2);
  const state = {page: "overview", department: "all", tenure: "all", dimension: "FAI", groupBy: "tenure"};
  const all = D.cohorts["all|all"];
  const item = code => all.items[code.replace(/[1-5]$/, "")].find(q => q.code === code);

  function kpi(label, value, note, suffix = "") {
    return `<div class="kpi"><div class="kpi-label">${esc(label)}</div><div class="kpi-value">${esc(value)}${suffix ? `<small>${esc(suffix)}</small>` : ""}</div><div class="kpi-note">${esc(note)}</div></div>`;
  }
  function stack(q) {
    const names = ["Almost never / Rarely", "Sometimes", "Usually / Almost always"];
    const classes = ["unfav", "sometimes", "fav"];
    return `<div class="stack" role="img" aria-label="${esc(q.counts.map((n, i) => names[i] + ': ' + n + ' (' + pct(q.shares[i]) + ')').join('; '))}">${q.shares.map((v, i) => `<span class="${classes[i]}" style="width:${v}%" title="${esc(names[i])}: ${q.counts[i]} / ${q.n} · ${pct(v)}"></span>`).join("")}</div>`;
  }
  function setOptions(id, values) {
    for (const value of values) { const opt = document.createElement("option"); opt.value = value; opt.textContent = value === "Other" ? "Other departments" : value; $(id).append(opt); }
  }
  function cohort() { return D.cohorts[state.department + "|" + state.tenure]; }

  function renderOverview() {
    const c = cohort(), ready = c.status === "ready";
    $("scope-label").textContent = ready ? `${state.department === "all" && state.tenure === "all" ? "Full study" : "Selected scope"} · ${c.n} responses` : c.status === "empty" ? "No matching responses" : "Selected scope · fewer than 10 responses";
    $("overview-kpis").innerHTML = ready ?
      kpi("Response records", c.n, "Eligible workforce / participation rate unavailable") +
      kpi("Favourable answers", pct(c.favourable), `4–5 across ${c.validAnswers.toLocaleString("en-GB")} valid rating answers`) +
      kpi("Culture mean", mean(c.culture), "25-item descriptive working summary", "/ 5") +
      kpi("Comment contributors", c.commentContributors, `${pct(c.commentContributors / c.n * 100)} supplied at least one nonblank comment`) :
      kpi("Response records", c.status === "empty" ? "0" : "<10", "Scores withheld below the reporting threshold") +
      kpi("Favourable answers", "—", "Not shown for this scope") + kpi("Culture mean", "—", "Not shown for this scope") + kpi("Comment contributors", "—", "Not shown for this scope");

    const dimList = ready ? c.dimensions : all.dimensions.map(d => ({...d, mean: null, favourable: null}));
    $("dimension-scorecard").innerHTML = dimList.map(d => `<button class="dimension-row" data-dim="${d.code}" aria-pressed="${d.code === state.dimension}" title="Inspect ${esc(d.label)} questions"><span class="dimension-main"><span class="dimension-label">${esc(d.label)}</span><span class="mean-track"><span class="mean-fill" style="width:${d.mean == null ? 0 : (d.mean - 1) / 4 * 100}%"></span></span></span><span class="mean-number">${d.mean == null ? "—" : mean(d.mean)}</span><span class="fav-number">${d.favourable == null ? "—" : pct(d.favourable)}</span></button>`).join("");
    $("selected-dimension").textContent = all.dimensions.find(d => d.code === state.dimension).label;
    const groups = ready ? c.groups[state.groupBy] : [];
    $("group-chart").style.gridTemplateRows = groups.length ? `repeat(${groups.length},minmax(0,1fr))` : "1fr";
    $("group-chart").innerHTML = groups.length ? groups.map(g => `<div class="group-row"><span class="group-label" title="${esc(g.label)}">${esc(g.label)} <span class="count">(${g.n == null ? "n<10" : "n=" + g.n})</span></span><span class="group-bar"><span style="width:${g.mean == null ? 0 : (g.mean - 1) / 4 * 100}%"></span></span><span class="group-value ${g.mean == null ? "suppressed" : ""}">${g.mean == null ? "Withheld" : mean(g.mean)}</span></div>`).join("") : `<div class="empty-message">${c.status === "empty" ? "No responses match these filters." : "A minimum of 10 responses is needed to display scores."}</div>`;
    if (ready) {
      $("question-rows").innerHTML = c.items[state.dimension].map(q => `<div class="question-row" role="row"><span class="question-label" role="cell" title="${esc(q.question)}" tabindex="0"><span class="item-code">${q.code}</span><span class="item-label">${esc(q.label)}</span></span><span role="cell">${stack(q)}</span><span class="metric" role="cell">${mean(q.mean)}</span><span class="metric favourable-metric" role="cell">${pct(q.shares[2])}</span><span class="metric" role="cell">${q.n}</span></div>`).join("");
    } else {
      $("question-rows").innerHTML = `<div class="empty-message">${c.status === "empty" ? "No matching responses." : "Rating diagnostics are withheld for scopes below 10 response records."}</div>`;
    }
    $("question-rows").style.gridTemplateRows = ready ? "repeat(5,minmax(0,1fr))" : "1fr";
    $("missing-label").textContent = ready ? "No missing rating answers" : "Change or reset the filters";
  }

  function focusBar(code, label) {
    const q = item(code);
    return `<div class="focus-bar-row"><span class="focus-bar-label" tabindex="0" title="${esc(q.question)}">${esc(label)}</span>${stack(q)}<span class="focus-bar-value">${pct(q.shares[2])}</span></div>`;
  }
  function renderFocus() {
    const f = D.focus, p = f.priorities;
    $("focus-kpis").innerHTML = kpi("Intend to stay 3–5 years", pct(p.stayAll), `Anonymous respondents ${pct(p.stayAnonymous)} · n = ${p.anonymousN}`) +
      kpi("Fairness share of outcome link", p.fairnessShare.toFixed(0), `Largest block · relative weights, R² ${p.r2.toFixed(2)}`, "%") +
      kpi("Leaders act on feedback", pct(item("CRE5").shares[2]), `Top actionable link · ${p.listenHrPct.toFixed(0)}% top HR request`) +
      kpi("Own team favourable, cross-team 1–3", f.pair.gap, `Out of 327 · ${f.pair.reverse} the reverse · targeted fix`);
    const p1 = [["RES4", "Efforts recognised"], ["CAM5", "Successes celebrated"], ["FAI3", "Consistent decisions"],
                ["FAI5", "Understanding decisions"], ["FAI1", "Fair rewards & recognition"], ["FAI2", "Equal growth opportunities"]];
    $("fairness-chart").innerHTML = p1.map(([code, label]) => focusBar(code, label)).join("");
    $("fairness-note").textContent = `Fairness: ${p.fairnessShare.toFixed(0)}% of the explained link to staying`;
    $("fairness-any").textContent = f.fairAnyN;
    const max = Math.max(...p.hrChoice.map(h => h.n));
    $("listen-chart").innerHTML = p.hrChoice.map(h => `<div class="voice-row"><span class="voice-label">${esc(h.label)}</span><span class="voice-track"><span class="${h.listen ? "listen" : ""}" style="width:${h.n / max * 100}%"></span></span><span class="voice-value ${h.listen ? "listen" : ""}" title="${pct(h.n / 327 * 100)} of respondents">${h.n}</span></div>`).join("");
    $("listen-note").textContent = `Leaders act on feedback: ${pct(item("CRE5").shares[2])} favourable`;
    $("cross-chart").innerHTML = focusBar("CAM1", "Help within own team") + focusBar("CAM2", "Teams work well together") + focusBar("CAM4", "Support from other teams");
    $("paired-note").innerHTML = `<strong>${f.pair.gap}</strong> rate own team 4–5 but cross-team 1–3 · ${f.pair.reverse} the reverse`;
    $("cs-note").textContent = `Customer Service cross-team ${p.customerServiceCross.toFixed(0)}%`;
  }

  function showPage(page, focusTab = false) {
    state.page = page === "focus" ? "focus" : "overview";
    for (const name of ["overview", "focus"]) {
      const active = state.page === name;
      $(name).hidden = !active;
      $("tab-" + name).setAttribute("aria-selected", String(active));
      $("tab-" + name).tabIndex = active ? 0 : -1;
    }
    $("overview-controls").hidden = state.page !== "overview";
    $("focus-controls").hidden = state.page !== "focus";
    $("footer-page").textContent = state.page === "overview" ? "01 / 02" : "02 / 02";
    $("footer-scope").textContent = state.page === "overview" ? "Favourable = 4–5 of valid answers. Culture mean is a descriptive working measure." : "Full study. Priority order from notebook Step 7 (four sources of evidence). Associations are not causal; comment coding is not independently validated.";
    if (focusTab) $("tab-" + state.page).focus();
    history.replaceState(null, "", "#" + state.page);
  }
  function viewportNote() { $("small-viewport").hidden = window.innerWidth >= 1120 && window.innerHeight >= 640; }

  setOptions("department", D.filters.departments); setOptions("tenure", D.filters.tenures);
  $("department").addEventListener("change", e => { state.department = e.target.value; renderOverview(); });
  $("tenure").addEventListener("change", e => { state.tenure = e.target.value; renderOverview(); });
  $("group-by").addEventListener("change", e => { state.groupBy = e.target.value; renderOverview(); });
  $("reset").addEventListener("click", () => { state.department = "all"; state.tenure = "all"; $("department").value = "all"; $("tenure").value = "all"; renderOverview(); });
  $("dimension-scorecard").addEventListener("click", e => { const button = e.target.closest("[data-dim]"); if (button) { state.dimension = button.dataset.dim; renderOverview(); } });
  document.querySelectorAll("[data-page]").forEach(button => button.addEventListener("click", () => showPage(button.dataset.page)));
  document.querySelector(".page-tabs").addEventListener("keydown", e => { if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(e.key)) { e.preventDefault(); showPage(e.key === "Home" ? "overview" : e.key === "End" ? "focus" : state.page === "overview" ? "focus" : "overview", true); } });
  $("method-button").addEventListener("click", () => $("method-dialog").showModal());
  $("close-method").addEventListener("click", () => $("method-dialog").close());
  $("method-dialog").addEventListener("click", e => { if (e.target === $("method-dialog")) { const r = e.target.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) e.target.close(); } });
  $("fullscreen").addEventListener("click", async () => { try { if (document.fullscreenElement) await document.exitFullscreen(); else await document.documentElement.requestFullscreen(); } catch { $("fullscreen").title = "Use your browser’s full-screen control"; } });
  document.addEventListener("fullscreenchange", () => { const label = document.fullscreenElement ? "Exit full screen" : "Enter full screen"; $("fullscreen").title = label; $("fullscreen").setAttribute("aria-label", label); });
  window.addEventListener("resize", viewportNote);
  renderOverview(); renderFocus(); showPage(location.hash === "#focus" ? "focus" : "overview"); viewportNote();
  window.__DASHBOARD_READY__ = true;
  window.__DASHBOARD_STATE__ = () => ({...state});
})();
