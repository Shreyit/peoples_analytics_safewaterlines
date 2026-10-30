"use strict";
// Survey assistant panel. Talks to dashboard/assistant/server.py; the dashboard itself still works offline without it.
(() => {
  const $ = id => document.getElementById(id);
  const esc = value => String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const panel = $("assistant"), log = $("assistant-log"), form = $("assistant-form"), input = $("assistant-input");
  const history = [];
  const served = location.protocol.startsWith("http");
  let ready = false, busy = false;

  // Minimal formatting: paragraphs, "- " bullets, **bold**, and a styled Source line.
  function format(text) {
    const inline = s => esc(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    return text.trim().split(/\n{2,}/).map(block => {
      const lines = block.split("\n");
      if (lines.every(l => /^\s*[-*•]\s+/.test(l))) return "<ul>" + lines.map(l => `<li>${inline(l.replace(/^\s*[-*•]\s+/, ""))}</li>`).join("") + "</ul>";
      if (/^source:/i.test(block)) return `<p class="assistant-source">${inline(block)}</p>`;
      return `<p>${lines.map(inline).join("<br>")}</p>`;
    }).join("");
  }
  function add(role, text, outcome = "") {
    const div = document.createElement("div");
    div.className = `assistant-msg ${role} ${outcome}`;
    div.innerHTML = role === "user" ? `<p>${esc(text)}</p>` : format(text);
    log.append(div); log.scrollTop = log.scrollHeight;
    return div;
  }
  function setStatus(text, ok) {
    $("assistant-status").textContent = text;
    $("assistant-status").className = "assistant-status " + (ok ? "ok" : "warn");
    input.disabled = !ok; $("assistant-send").disabled = !ok;
  }

  async function checkStatus() {
    if (!served) return setStatus("Start the assistant server, then open http://127.0.0.1:8765 (see dashboard/README.md).", false);
    try {
      const s = await (await fetch("/api/status", {cache: "no-store"})).json();
      ready = s.ready;
      setStatus(s.ready ? (s.offline ? "Offline test mode · nothing is sent to Vertex AI" : `Gemini on Vertex AI · ${s.model}`) : s.hint, s.ready);
    } catch { setStatus("The assistant server is not responding. Restart it and reload this page.", false); }
  }

  async function ask(question) {
    if (!ready || busy || !question.trim()) return;
    busy = true; input.value = ""; $("assistant-suggestions").hidden = true;
    add("user", question);
    const pending = add("model", "Reading the reports…", "pending");
    try {
      const r = await (await fetch("/api/ask", {method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question, history})})).json();
      pending.remove();
      add("model", r.answer || "Something went wrong. Please try again.", r.outcome || "error");
      if (r.outcome === "answered") history.push({role: "user", text: question}, {role: "model", text: r.answer});
    } catch {
      pending.remove(); add("model", "The assistant server is not responding.", "error");
    } finally { busy = false; input.focus(); }
  }

  $("assistant-open").addEventListener("click", () => { panel.show(); $("assistant-open").setAttribute("aria-expanded", "true"); checkStatus(); input.focus(); });
  $("assistant-close").addEventListener("click", () => { panel.close(); $("assistant-open").setAttribute("aria-expanded", "false"); });
  form.addEventListener("submit", e => { e.preventDefault(); ask(input.value); });
  input.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(input.value); } });
  $("assistant-suggestions").addEventListener("click", e => { const b = e.target.closest("button"); if (b) ask(b.textContent); });
  panel.addEventListener("keydown", e => { if (e.key === "Escape") $("assistant-close").click(); });
})();
