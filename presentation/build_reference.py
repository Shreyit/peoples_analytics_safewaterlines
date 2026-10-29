"""Build the full reference report (A4 PDF) from the notebook's generated outputs.

Inputs are aggregate only: the generated analysis guide, exported tables and figures,
and the notebook's annex/methodology Markdown. Layout is done by WeasyPrint (CLI).
"""
from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path

import markdown
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPORTS = ROOT / "reports"
TABLES = REPORTS / "tables"
FIG = REPORTS / "figures"
OUT = HERE / "output"
BUILD = HERE / "build"
BUILD.mkdir(exist_ok=True)
PDF = OUT / "Safewater_Lines_Full_Reference.pdf"


def md(text):
    return markdown.markdown(text, extensions=["tables", "sane_lists", "attr_list"])


def figure(name, caption):
    return f'<figure><img src="{(FIG / name).as_uri()}"><figcaption>{html.escape(caption)}</figcaption></figure>'


def table(frame, columns=None, rename=None, fmt=None, cls=""):
    frame = frame[columns] if columns else frame
    frame = frame.rename(columns=rename or {})
    fmt = fmt or {}
    head = "".join(f"<th>{html.escape(str(c))}</th>" for c in frame.columns)
    rows = []
    for _, r in frame.iterrows():
        cells = []
        for c, v in r.items():
            if pd.isna(v): v = "—"
            elif c in fmt: v = fmt[c].format(v)
            elif isinstance(v, float): v = f"{v:.1f}"
            cells.append(f"<td>{html.escape(str(v))}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return f'<table class="data {cls}"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


FIGURE_CAPTIONS = {
    "strengths_and_opportunities.png": "Strengths and opportunities by question (favourable share).",
    "topic_cooccurrence_network.png": "Topic co-mention network (VOSviewer-inspired; prompt-sensitive).",
    "implementation_roadmap.png": "Proposed 0–90-day implementation timeline.",
}


def localise_links(text):
    """Embed linked figures, keep web links, and turn local file links into readable file names."""
    figures = []
    def repl(m):
        label, target = m.group(1), m.group(2)
        if target.startswith("http"):
            return f"[{label}]({target})"
        name = Path(target).name
        if name.endswith(".png") and name in FIGURE_CAPTIONS:
            figures.append(name)
        return f"{label} (*{name}*)" if "." in name else label
    out = []
    for line in text.splitlines():
        figures.clear()
        out.append(re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl, line))
        for name in dict.fromkeys(figures):
            out.append("")
            out.append(f'<div markdown="0">{figure(name, FIGURE_CAPTIONS[name])}</div>')
            out.append("")
    return "\n".join(out)


# ---------- inputs ----------
guide = (REPORTS / "ANALYSIS_FROM_DATA_TO_ACTION.md").read_text().replace("<!-- STEP7_PRIORITISATION -->", "")
guide = re.sub(r"^# .*\n", "", guide, count=1)                 # the report supplies its own part titles
guide = localise_links(guide)
guide = guide.replace("## 15. Prioritisation check (Step 7, 30 October 2026)",
                      "## 15. Prioritisation check (Step 7, 30 October 2026)\n\n" +
                      f'<div markdown="0">{figure("priority_matrix.png", "Priority matrix: link to outcomes vs favourable share, 19 actionable questions.")}</div>\n\n' +
                      f'<div markdown="0">{figure("group_hotspots.png", "Favourable % on priority questions by group (n ≥ 10).")}</div>\n')
nb = json.load(open(ROOT / "notebooks/00_data_understanding_eda.ipynb"))
cells = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown"]
annex = [c for c in cells if re.match(r"## [A-D]\. ", c)]
method = next(c for c in cells if c.startswith("# Methodology reference"))
assert len(annex) == 4, [a[:30] for a in annex]

df = pd.read_csv(ROOT / "data/processed/survey_clean.csv")
item = pd.read_csv(TABLES / "item_evidence_profile.csv")
tri = pd.read_csv(TABLES / "priority_triangulation.csv")
pm = pd.read_csv(TABLES / "priority_matrix.csv")
nva = pd.read_csv(TABLES / "named_vs_anonymous.csv").rename(columns={"Unnamed: 0": "group"})
hot = pd.read_csv(TABLES / "group_hotspots.csv")
hr = pd.read_csv(TABLES / "hr_priority_counts.csv").rename(columns={"hr_priority": "option"})
one = pd.read_csv(TABLES / "one_change_topics.csv")
voice = pd.read_csv(TABLES / "employee_voice_topic_summary.csv")
road = pd.read_csv(TABLES / "implementation_roadmap_0_90_days.csv")
kpi = pd.read_csv(TABLES / "roadmap_kpi_dictionary.csv")
gates = pd.read_csv(TABLES / "roadmap_decision_gates.csv")
verify = pd.read_csv(TABLES / "finding_verification_register.csv")
model = pd.read_csv(TABLES / "driver_model_summary.csv", index_col=0)["value"]
codebook = pd.read_csv(ROOT / "data/processed/codebook.csv")
assert len(df) == 327

fav = item.set_index("item")["fav_%"]
anon = nva.set_index("group")

# ---------- executive summary (computed figures only) ----------
summary = f"""
<p class="lead">327 people answered the Your Voice survey (30 rating questions, six open questions, one HR-priority choice) in five languages.
People are proud of Safewater Lines and help each other. The gaps are in how people decisions are made and explained, and in whether leaders visibly act on what employees raise.</p>
<div class="kpis">
  <div><b>{fav['PRI1']:.1f}%</b><span>proud to work here</span></div>
  <div><b>{fav['PRI3']:.1f}%</b><span>intend to stay 3–5 years (anonymous: {anon.loc['Anonymous', 'stay_3_5_yrs_fav']:.1f}%)</span></div>
  <div><b>{fav['FAI3']:.1f}%</b><span>say people decisions are consistent</span></div>
  <div><b>{fav['CRE5']:.1f}%</b><span>say leaders act on feedback</span></div>
</div>
<h3>Recommendation</h3>
<ol>
<li><b>Protect</b> pride, belonging and own-team support ({fav['PRI1']:.1f}%, {fav['CAM3']:.1f}%, {fav['CAM1']:.1f}% favourable).</li>
<li><b>Priority 1: fair, explainable people decisions, growth and recognition.</b> The five lowest-scoring questions sit here; Fairness accounts for {model['dim_FAI']:.0f}% of the explained link to recommend, satisfaction and intention to stay.</li>
<li><b>Priority 2: leaders listen and visibly act.</b> The top actionable link to outcomes, the most common HR request ({int(hr.iloc[0]['respondents'])} people) and the most-raised "one change".</li>
<li><b>Targeted fix: cross-team handovers</b>, starting in Customer Service (45 people rate their own team 4–5 but cross-team work 1–3).</li>
<li><b>Route pay, benefits and facilities</b> to the annual review, and <b>drop the name field</b> from the next survey.</li>
</ol>
<p>The order comes from a four-source evidence check (Section 15). Only the two priorities are strong on all four sources:</p>
{table(tri, ["theme", "score", "outcome_link", "hr_choice", "one_change", "strong_lenses"],
       {"theme": "Theme", "score": "Score", "outcome_link": "Outcome link", "hr_choice": "HR choice", "one_change": "'One change'", "strong_lenses": "Strong (of 4)"},
       {"Strong (of 4)": "{:.0f}"})}
<h3>How to read this report</h3>
<ul>
<li>Favourable = 4–5 (Usually / Almost always). 3 = Sometimes, not neutral. Percentages use all 327 responses unless stated.</li>
<li>Headcount was not supplied, so the response rate is unknown. 69% gave their name, and anonymous respondents are less favourable on every key question.</li>
<li>Links to outcomes are associations from one survey, not causes. Comment coding was AI-assisted with one documented re-review; it is not independently validated.</li>
</ul>
"""

# ---------- appendices ----------
item_tab = item.assign(**{"no straight-liners %": item["fav_without_straightliners_pct"]})
appendix_a = "\n".join([
    "<h2 id='a1'>A1. All 30 rating questions</h2>",
    table(item_tab.sort_values("fav_%"), ["item", "question", "mean", "fav_%", "sometimes_%", "unfav_%", "top_box_%", "no straight-liners %"],
          {"item": "Code", "question": "Question", "mean": "Mean", "fav_%": "Fav %", "sometimes_%": "Sometimes %", "unfav_%": "Unfav %", "top_box_%": "Top box %"},
          {"Mean": "{:.2f}"}, "small"),
    "<h2 id='a2'>A2. Priority matrix (relative weights, 500 bootstraps)</h2>",
    f"<p>Outcome = mean of OVR1, OVR4, PRI3. R² = {model['actionable_r2']:.2f} (all), {model['r2_no_straightliners']:.2f} (no straight-liners), {model['r2_anonymous_only']:.2f} (anonymous only). "
    f"Dimension shares: CRE {model['dim_CRE']:.1f}%, RES {model['dim_RES']:.1f}%, FAI {model['dim_FAI']:.1f}%, CAM {model['dim_CAM']:.1f}%.</p>",
    table(pm, ["Unnamed: 0", "fav_pct", "importance_pct", "imp_ci_low", "imp_ci_high", "p_top5", "imp_no_straightliners", "imp_anonymous_only", "quadrant"],
          {"Unnamed: 0": "Item", "fav_pct": "Fav %", "importance_pct": "Importance %", "imp_ci_low": "95% CI low", "imp_ci_high": "95% CI high",
           "p_top5": "P(top 5)", "imp_no_straightliners": "No straight-liners", "imp_anonymous_only": "Anonymous only", "quadrant": "Quadrant"},
          {"P(top 5)": "{:.2f}"}, "small"),
    "<h2 id='a3'>A3. Four-source evidence check</h2>",
    table(tri, ["theme", "items", "lowest_fav_rank_of_30", "score", "max_p_top5_driver", "outcome_link", "hr_choice_pct", "hr_choice", "one_change_records", "one_change"],
          {"theme": "Theme", "items": "Items", "lowest_fav_rank_of_30": "Lowest rank", "score": "Score", "max_p_top5_driver": "Max P(top 5)",
           "outcome_link": "Outcome link", "hr_choice_pct": "HR %", "hr_choice": "HR grade", "one_change_records": "One change (people)", "one_change": "One-change grade"},
          {"Lowest rank": "{:.0f}", "Max P(top 5)": "{:.2f}", "One change (people)": "{:.0f}"}, "small"),
    "<h2 id='a4'>A4. Named vs anonymous respondents</h2>",
    table(nva, ["group", "n", "culture_mean", "stay_3_5_yrs_fav", "recommend_fav", "fix_first_items_fav", "straightliner_pct"],
          {"group": "Group", "culture_mean": "Culture mean", "stay_3_5_yrs_fav": "Stay 3–5 yrs %", "recommend_fav": "Recommend %",
           "fix_first_items_fav": "Fix-first items %", "straightliner_pct": "Straight-liners %"}, {"n": "{:.0f}", "Culture mean": "{:.2f}"}),
    "<h2 id='a5'>A5. Group hotspots (favourable %, n ≥ 10)</h2>",
    table(hot, rename={"group_type": "Type", "group": "Group"}, fmt={"n": "{:.0f}"}, cls="small"),
    "<h2 id='a6'>A6. HR forced choice</h2>",
    table(hr, ["option", "respondents", "pct"], {"option": "If HR could do one thing better…", "respondents": "People", "pct": "%"}, {"People": "{:.0f}"}),
    "<h2 id='a7'>A7. Comment topics</h2>",
    "<p>Open “one change” question (people raising each topic):</p>",
    table(one, ["topic", "records", "pct_of_nonblank"], {"topic": "Topic", "records": "People", "pct_of_nonblank": "% of answers"}, {"People": "{:.0f}"}),
    "<p>All six open questions (requests and strengths, unique people):</p>",
    table(voice, ["topic", "request_record_n", "request_pct_all_327", "preserve_record_n"],
          {"topic": "Topic", "request_record_n": "Request (people)", "request_pct_all_327": "Request % of 327", "preserve_record_n": "Preserve (people)"},
          {"Request (people)": "{:.0f}", "Preserve (people)": "{:.0f}"}),
    "<h2 id='a8'>A8. Finding verification register</h2>",
    table(verify, rename={"finding": "Finding", "recomputed_value": "Recomputed", "check": "Check"}, cls="small"),
])
appendix_b = "\n".join([
    "<h2 id='b1'>B1. Implementation roadmap (0–90 days)</h2>",
    "<p>IDs: P1 = fair decisions and growth; P1-R = recognition; P2 = listen and act; T = targeted cross-team fix; S2 = role clarity; G = governance; V = verification.</p>",
    table(road, ["action_id", "workstream", "timing_from_approval", "proposed_accountable_owner", "action", "proposed_standard_or_decision_gate"],
          {"action_id": "ID", "workstream": "Workstream", "timing_from_approval": "Timing", "proposed_accountable_owner": "Accountable",
           "action": "Action", "proposed_standard_or_decision_gate": "Standard / gate"}, cls="small"),
    "<h2 id='b2'>B2. KPI dictionary</h2>",
    table(kpi, ["kpi_id", "workstream", "measure", "source_item_or_system", "current_reference_baseline", "proposed_target_or_target_setting_rule"],
          {"kpi_id": "ID", "workstream": "Workstream", "measure": "Measure", "source_item_or_system": "Source", "current_reference_baseline": "Current reference",
           "proposed_target_or_target_setting_rule": "Target rule"}, cls="small"),
    "<h2 id='b3'>B3. Decision gates</h2>",
    table(gates, rename={"gate": "Gate", "required_decision": "Decision", "interpretation_rule": "Interpretation rule"}, cls="small"),
])
appendix_c = "<h2 id='c1'>C1. Question codebook</h2>" + table(codebook[codebook["col"] != "full_name"], ["col", "block", "question"],
                                                                {"col": "Code", "block": "Block", "question": "Question"}, cls="small")
appendix_d = "\n".join(md(a) for a in annex)
appendix_e = md(re.sub(r"^# .*\n", "", method, count=1))

parts = [
    ("summary", "Executive summary", summary),
    ("analysis", "Part 1 — From data to action: the full analysis", md(guide)),
    ("appA", "Appendix A — Evidence tables", appendix_a),
    ("appB", "Appendix B — Roadmap, KPIs and decision gates", appendix_b),
    ("appC", "Appendix C — Questionnaire", appendix_c),
    ("appD", "Appendix D — Terms, variables, mappings and lineage", appendix_d),
    ("appE", "Appendix E — Methodology reference", appendix_e),
]

# ---------- table of contents from h1/h2 ----------
body, toc, n = [], [], 0
for pid, title, content in parts:
    body.append(f'<section class="part"><h1 id="{pid}">{html.escape(title)}</h1>')
    toc.append(f'<li class="toc1"><a href="#{pid}">{html.escape(title)}</a></li>')
    def add_id(m):
        global n
        n += 1
        text = re.sub("<[^>]+>", "", m.group(2))
        toc.append(f'<li class="toc2"><a href="#h{n}">{html.escape(html.unescape(text))}</a></li>')
        return f'<h2 id="h{n}"{m.group(1)}>{m.group(2)}</h2>'
    content = re.sub(r"<h2(?: id='[^']*')?([^>]*)>(.*?)</h2>", add_id, content)
    body.append(content + "</section>")

CSS = """
@page { size: A4; margin: 20mm 17mm 20mm 17mm;
  @top-left { content: "Safewater Lines · Your Voice survey · Full reference"; font: 8pt Arial; color: #647582; }
  @bottom-right { content: counter(page) " / " counter(pages); font: 8pt Arial; color: #647582; }
  @bottom-left { content: "Confidential · aggregate results only"; font: 8pt Arial; color: #647582; } }
@page:first { @top-left { content: none } @bottom-left { content: none } @bottom-right { content: none } }
body { font-family: Arial, Helvetica, sans-serif; font-size: 9.6pt; line-height: 1.45; color: #243441; }
h1 { font-size: 20pt; color: #243441; margin: 0 0 10pt; padding-bottom: 6pt; border-bottom: 2px solid #365F7B; }
h2 { font-size: 13pt; color: #365F7B; margin: 16pt 0 6pt; break-after: avoid; }
h3 { font-size: 11pt; color: #243441; margin: 12pt 0 4pt; break-after: avoid; }
section.part { break-before: page; }
p, li { orphans: 2; widows: 2; }
a { color: #365F7B; text-decoration: none; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 8.4pt; }
th { background: #F2F5F7; color: #365F7B; text-align: left; padding: 3pt 5pt; border-bottom: 1px solid #B9C7D1; }
td { padding: 3pt 5pt; border-bottom: 0.5pt solid #DEE4E8; vertical-align: top; }
tr { break-inside: avoid; }
table.small { font-size: 7.4pt; }
figure { margin: 8pt 0 12pt; break-inside: avoid; text-align: center; }
figure img { max-width: 100%; max-height: 120mm; }
figcaption { font-size: 8pt; color: #647582; margin-top: 3pt; }
code { font-size: 8.4pt; background: #F2F5F7; padding: 0 2pt; }
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center; }
.cover .eyebrow { color: #365F7B; font-weight: bold; letter-spacing: .5pt; font-size: 10pt; }
.cover h1.title { font-size: 34pt; border: 0; line-height: 1.12; margin: 14pt 0; }
.cover p { font-size: 12pt; color: #647582; }
.cover .rule { width: 40pt; height: 3pt; background: #365F7B; margin: 18pt 0; }
.toc { break-before: page; }
.toc ol { list-style: none; padding: 0; }
.toc li a::after { content: leader('.') target-counter(attr(href), page); }
.toc li.toc1 { font-weight: bold; margin-top: 7pt; font-size: 10pt; }
.toc li.toc2 { margin-left: 12pt; font-size: 8.8pt; }
.lead { font-size: 11pt; }
.kpis { display: flex; gap: 8pt; margin: 10pt 0; }
.kpis div { flex: 1; background: #F2F5F7; padding: 8pt; border-top: 3px solid #365F7B; }
.kpis b { display: block; font-size: 18pt; color: #365F7B; }
.kpis span { font-size: 8.4pt; color: #647582; }
"""

cover = f"""
<div class="cover">
  <div class="eyebrow">SAFEWATER LINES · PEOPLE ANALYTICS</div>
  <h1 class="title">Your Voice survey<br>Full reference report</h1>
  <div class="rule"></div>
  <p>Data, methods, findings, evidence tables, roadmap and methodology behind the executive presentation and the 20-minute pitch.</p>
  <p>327 responses · 30 rating questions · 1,892 comments<br>Responses as of 21 October · Analysis 30 October 2026 · TISS</p>
</div>
<nav class="toc"><h1>Contents</h1><ol>{''.join(toc)}</ol></nav>
"""
doc = f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Safewater Lines — Full reference report</title><style>{CSS}</style></head><body>{cover}{''.join(body)}</body></html>"
src = BUILD / "reference.html"
src.write_text(doc)
subprocess.run(["weasyprint", "--quiet", str(src), str(PDF)], check=True)

import pymupdf  # noqa: E402  verify after rendering
pdf = pymupdf.open(PDF)
text = "".join(p.get_text() for p in pdf)
for must in ["Executive summary", "15. Prioritisation check", "Appendix E", "Fix first", "Leaders listen and visibly act"]:
    assert must in text, must
# Privacy: no respondent's typed name may appear anywhere (names are read in memory only, never written).
raw = pd.read_excel(ROOT / "data/raw/Your Voice- Responses 21 OCT - FINAL.xlsx", "SWL - MASTERDATA", header=1)
names = raw.iloc[:, 5].dropna().astype(str).str.strip()
names = names[names.str.len() >= 4].str.lower()
low = " ".join(text.lower().split())
leaks = sum(n in low for n in set(names))
assert leaks == 0, f"{leaks} respondent names found in the reference PDF"
preview = HERE / "preview/reference"
preview.mkdir(parents=True, exist_ok=True)
for old in preview.glob("page-*.png"):
    old.unlink()
for i in range(min(len(pdf), 60)):
    pdf[i].get_pixmap(matrix=pymupdf.Matrix(1, 1), alpha=False).save(preview / f"page-{i+1:02d}.png")
print(f"Created {PDF} ({len(pdf)} pages, {len(figures_used := re.findall(r'<img ', doc))} figures, {doc.count('<table')} tables).")
