"""Create an editable executive PPTX and a PDF companion from one layout model.

Only aggregate evidence is included. All measurements are in points (960 × 540).
The companion PDF uses the same scene model, not a PowerPoint rendering engine.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Pt
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TABLES = ROOT / "reports/tables"
OUT = HERE / "output"
PREVIEW = HERE / "preview"
OUT.mkdir(exist_ok=True)
PREVIEW.mkdir(exist_ok=True)
W, H = 960, 540
INK, BLUE, MUTED = "243441", "365F7B", "647582"
LINE, PALE, LIGHT, MID, DARK = "DEE4E8", "F2F5F7", "E9EEF1", "B9C7D1", "577A91"
WHITE = "FFFFFF"
FONT_DIR = Path("/System/Library/Fonts/Supplemental")
pdfmetrics.registerFont(TTFont("Arial", str(FONT_DIR / "Arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONT_DIR / "Arial Bold.ttf")))

df = pd.read_csv(ROOT / "data/processed/survey_clean.csv")
item = pd.read_csv(TABLES / "item_evidence_profile.csv").set_index("item")
topics = pd.read_csv(TABLES / "employee_voice_topic_summary.csv").set_index("topic_code")
pm = pd.read_csv(TABLES / "priority_matrix.csv", index_col=0)
tri = pd.read_csv(TABLES / "priority_triangulation.csv", index_col=0)
hr = pd.read_csv(TABLES / "hr_priority_counts.csv", index_col=0)
one = pd.read_csv(TABLES / "one_change_topics.csv", index_col=0)
nva = pd.read_csv(TABLES / "named_vs_anonymous.csv", index_col=0)
hot = pd.read_csv(TABLES / "group_hotspots.csv").set_index("group")
model = pd.read_csv(TABLES / "driver_model_summary.csv", index_col=0)["value"]

rating_cols = [f"{d}{i}" for d in ["CRE", "RES", "FAI", "PRI", "CAM", "OVR"] for i in range(1, 6)]
assert len(df) == 327 and df[rating_cols].notna().sum().sum() == 9810
assert ((df.CAM1 >= 4) & (df.CAM2 <= 3)).sum() == 45
assert df[[f"FAI{i}" for i in range(1, 6)]].le(3).any(axis=1).sum() == 137
assert int(topics.loc["r", "request_record_n"]) == 179
# The revised priority order rests on these results; fail the build if the evidence changes.
FIX_FIRST = pm.index[pm["quadrant"].eq("Fix first")].tolist()
assert set(FIX_FIRST) == {"CRE5", "FAI2", "CAM2", "FAI1", "FAI3", "FAI5"}
assert tri["strong_lenses"].iloc[:2].tolist() == [4, 4] and tri["strong_lenses"].iloc[2:].max() <= 2
assert model[[f"dim_{d}" for d in ["CRE", "RES", "FAI", "CAM"]]].idxmax() == "dim_FAI"
assert int(hr["respondents"].iloc[0]) == 67 and hr.index[0].startswith("Listening")

R2 = model["actionable_r2"]
FAI_SHARE = model["dim_FAI"]
ANON_N = int(nva.loc["Anonymous", "n"])
anon = ~df["gave_name"]
CV_RECORDS = int(tri.loc["Leaders listen and visibly act", "one_change_records"])
ONE_CHANGE_BASE = int(round(one.loc["c", "records"] / one.loc["c", "pct_of_nonblank"] * 100))
assert ONE_CHANGE_BASE == int(df["oe_one_change"].notna().sum())


def fav(code):
    return float(item.loc[code, "fav_%"])


def fav_anon(code):
    return float((df.loc[anon, code] >= 4).mean() * 100)


def request(code):
    return int(topics.loc[code, "request_record_n"])


def wrap(text, width, size, bold=False):
    font = "Arial-Bold" if bold else "Arial"
    lines = []
    for paragraph in str(text).split("\n"):
        current = ""
        for word in paragraph.split():
            trial = (current + " " + word).strip()
            if current and pdfmetrics.stringWidth(trial, font, size) > width:
                lines.append(current)
                current = word
            else:
                current = trial
        lines.append(current)
    return lines


slides = []


class Slide:
    title_size, subtitle_y = 28, 128

    def __init__(self, section, title, subtitle, source, notes, appendix=False, cover=False):
        self.section, self.title, self.subtitle = section, title, subtitle
        self.source, self.notes, self.appendix = source, notes, appendix
        self.objects = []
        slides.append(self)
        self.number = len(slides)
        if not cover:
            self.text("SAFEWATER LINES  /  " + section.upper(), 48, 26, 864, 16, 9.5, BLUE, True)
            self.text(title, 48, 54, 864, 72, self.title_size, INK, True, leading=1.12)
            self.text(subtitle, 48, self.subtitle_y, 864, 24, 11.5, MUTED)
        self.line(48, 500, 912, 500, LINE, .6)
        self.text("Source: " + source, 48, 510, 806, 21, 7.7, MUTED, leading=1.13)
        self.objects[-1]["role"] = "source"     # lets a presenting version drop internal file references
        self.text(f"{'APPENDIX  /  ' if appendix else ''}{self.number:02d}", 816, 510, 96, 12, 8, MUTED, align="right")

    def text(self, value, x, y, w, h, size=14, color=INK, bold=False, align="left", leading=1.2):
        lines = wrap(value, w, size, bold)
        if len(lines) * size * leading > h + .1:
            raise ValueError(f"Slide {self.number}: text exceeds height: {value!r} ({len(lines)} lines in {h})")
        for line in lines:
            if pdfmetrics.stringWidth(line, "Arial-Bold" if bold else "Arial", size) > w + .1:
                raise ValueError(f"Slide {self.number}: unbreakable line exceeds width: {line}")
        self.objects.append(dict(kind="text", text=str(value), lines=lines, x=x, y=y, w=w, h=h,
                                 size=size, color=color, bold=bold, align=align, leading=leading))

    def rect(self, x, y, w, h, fill=PALE, stroke=None, radius=False):
        self.objects.append(dict(kind="rect", x=x, y=y, w=w, h=h, fill=fill, stroke=stroke, radius=radius))

    def line(self, x1, y1, x2, y2, color=LINE, width=1):
        self.objects.append(dict(kind="line", x=x1, y=y1, x2=x2, y2=y2, color=color, width=width))

    def circle(self, x, y, diameter, fill=DARK, stroke=None):
        self.objects.append(dict(kind="circle", x=x, y=y, w=diameter, h=diameter, fill=fill, stroke=stroke))

    def label(self, text, x, y, width=380):
        self.text(text.upper(), x, y, width, 18, 10, BLUE, True)

    def rule_note(self, text, y=465):
        self.line(48, y - 8, 912, y - 8)
        self.text(text, 48, y, 864, 26, 10.5, MUTED)


def body(s, text, x, y, w, size=14, h=70, color=INK, bold=False):
    s.text(text, x, y, w, h, size, color, bold)


def stack(s, code, label, x, y, label_w=250, bar_w=290, row_h=45):
    body(s, label, x, y + 1, label_w, 12.5, 33)
    bx = x + label_w + 12
    counts = [item.loc[code, "unfavourable_n"], item.loc[code, "sometimes_n"], item.loc[code, "favourable_n"]]
    pos = bx
    for n, color in zip(counts, [MUTED, MID, BLUE]):
        width = float(n) / 327 * bar_w
        s.rect(pos, y + 5, width, 15, color)
        pos += width
    s.text(f"{fav(code):.1f}%", bx + bar_w + 12, y, 58, 25, 14, BLUE, True, "right")


def legend(s, x=48, y=445):
    for dx, color, text in [(0, MUTED, "1–2 · Unfavourable"), (166, MID, "3 · Sometimes"), (310, BLUE, "4–5 · Favourable")]:
        s.rect(x + dx, y + 3, 9, 8, color)
        s.text(text, x + dx + 15, y, 156, 15, 10, MUTED)


def table(s, columns, rows, x=48, y=171, widths=None, row_h=47, header_h=32, size=12):
    widths = widths or [864 / len(columns)] * len(columns)
    s.rect(x, y, sum(widths), header_h, PALE)
    pos = x
    for heading, width in zip(columns, widths):
        s.text(heading, pos + 9, y + 8, width - 18, header_h - 9, 10, BLUE, True)
        pos += width
    y += header_h
    for row in rows:
        pos = x
        for col, (value, width) in enumerate(zip(row, widths)):
            s.text(value, pos + 9, y + 10, width - 18, row_h - 12, size, INK if col == 0 else MUTED, col == 0)
            pos += width
        s.line(x, y + row_h, x + sum(widths), y + row_h, LINE, .6)
        y += row_h


def hbar(s, label, value, vmax, x, y, label_w, bar_w, highlight=False, fmt="{:.0f}", size=11.5):
    h = max(16, size * 1.25)
    body(s, label, x, y, label_w, size, h)
    s.rect(x + label_w + 8, y + 3 + (h - 16) / 2, bar_w, 10, LIGHT)
    s.rect(x + label_w + 8, y + 3 + (h - 16) / 2, value / vmax * bar_w, 10, BLUE if highlight else MID)
    s.text(fmt.format(value), x + label_w + bar_w + 14, y, 46, h, size, BLUE if highlight else MUTED, highlight)


def mix(a, b, t):
    pa, pb = [int(a[i:i + 2], 16) for i in (0, 2, 4)], [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(pa, pb))


def grade_mark(s, grade, x, y):
    if grade == "Strong":
        s.circle(x, y, 10, BLUE)
    elif grade == "Medium":
        s.circle(x, y, 10, MID)
    elif grade == "Weak":
        s.circle(x, y, 10, WHITE, MID)


def quote(s, text, x, y, w, h=60, size=12):
    s.rect(x, y, 3, h - 6, MID)
    s.text(text, x + 14, y, w - 14, h, size, INK)


# 01 — Cover
s = Slide("Executive presentation", "Proud people. Fairer decisions. A listening loop that closes.", "",
          "Your Voice master survey; analysis snapshot 30 October 2026.",
          "Open with the organisational question: what should Safewater Lines protect, and what should it fix first? People are proud and feel they belong. The gaps are in how people decisions are made and explained, and in whether leaders visibly act on what employees raise. We propose one 90-day pilot with three workstreams, measured with an anonymous pulse. Use the dashboard for questions rather than walking through every metric.", cover=True)
s.text("SAFEWATER LINES", 48, 40, 700, 20, 12, BLUE, True)
s.text("PEOPLE EXPERIENCE  /  EXECUTIVE REVIEW", 48, 82, 800, 20, 10, MUTED)
s.rect(48, 135, 52, 4, BLUE)
s.text("Proud people. Fairer decisions.\nA listening loop that closes.", 48, 163, 850, 116, 38, INK, True, leading=1.12)
s.text("An evidence-based pathway for fair, explainable people decisions,\nvisible follow-through and smoother handovers.", 48, 302, 850, 58, 18, MUTED, leading=1.3)
s.text("327 responses  ·  30 rating items  ·  1,892 comments", 48, 403, 850, 25, 14, INK)
s.text("30 OCTOBER 2026  /  TISS", 48, 454, 850, 18, 10, BLUE, True)

# 02 — Executive summary
s = Slide("Executive summary", "Protect pride. Make people decisions fair\nand visible. Close the listening loop.",
          "Two priorities backed by all four sources of evidence, plus one targeted operational fix.",
          "item_evidence_profile.csv; priority_matrix.csv; priority_triangulation.csv; driver_model_summary.csv; group_hotspots.csv.",
          f"Lead with the recommendation. Protect what works: pride, belonging and own-team support are all above 90% favourable. Priority 1 is fair, explainable people decisions, growth and recognition: the five lowest-scoring questions sit here, and Fairness is the block most strongly linked to recommending, satisfaction and intention to stay ({FAI_SHARE:.0f}% of the explained variation). Priority 2 is leaders listening and visibly acting: it is the top actionable link to outcomes, the most common HR request and the most raised 'one change'. Cross-team handovers show a real but narrower gap; fix them in a targeted pilot starting in Customer Service. All links are associations from one survey, not proven causes.")
for y, label, heading, detail in [
    (168, "PROTECT", "Pride, belonging and own-team support", f"{fav('PRI1'):.1f}% proud to work here · {fav('CAM3'):.1f}% feel they belong · {fav('CAM1'):.1f}% helped by own team."),
    (240, "PRIORITY 1", "Fair, explainable people decisions, growth and recognition", f"The 5 lowest-scoring questions. Fairness is the block most linked to staying and recommending ({FAI_SHARE:.0f}%)."),
    (312, "PRIORITY 2", "Leaders listen and visibly act", f"Top actionable link to outcomes · top HR request ({hr['pct'].iloc[0] + hr.loc['Keeping employees informed', 'pct']:.0f}%) · most-raised 'one change'."),
    (384, "TARGETED FIX", "Cross-team handovers, starting in Customer Service", "45 rate their own team well but cross-team work 1–3; lowest in Customer Service."),
]:
    s.line(48, y - 9, 912, y - 9)
    s.label(label, 48, y + 4, 140)
    body(s, heading, 199, y, 713, 17, 24, bold=True)
    body(s, detail, 199, y + 28, 713, 12.5, 30, MUTED)
s.rule_note("One 90-day pilot · three workstreams · named owners · an anonymous pulse at Day 0 and Day 90.")

# 03 — Headline and how to read
s = Slide("The headline", "Positive overall, and noticeably\nless so when people stay anonymous", "Read every headline figure next to its anonymous counterpart.",
          "named_vs_anonymous.csv; item_evidence_profile.csv; survey_clean.csv; notebook Step 7.4.",
          f"Most respondents intend to stay and would recommend Safewater Lines. But 69% typed their name in the optional field, and the {ANON_N} anonymous respondents are clearly less positive: {nva.loc['Anonymous', 'stay_3_5_yrs_fav']:.0f}% intend to stay for 3–5 years versus {nva.loc['Named', 'stay_3_5_yrs_fav']:.0f}% of named respondents. This is consistent with people being more guarded when named, although who chose to give a name may also differ. Either way, report both figures and run the next survey without a name field. The right-hand column gathers the reading rules in one place so the rest of the deck can stay direct.")
s.label("Intend to stay 3–5 years", 48, 171)
s.text(f"{fav('PRI3'):.1f}%", 48, 194, 190, 54, 42, BLUE, True)
body(s, "All 327 respondents", 48, 248, 190, 12, 18, MUTED)
s.text(f"{nva.loc['Anonymous', 'stay_3_5_yrs_fav']:.1f}%", 250, 194, 190, 54, 42, DARK, True)
body(s, f"{ANON_N} anonymous respondents", 250, 248, 190, 12, 18, MUTED)
s.label("Would recommend as a great place to work", 48, 290)
s.text(f"{fav('OVR1'):.1f}%", 48, 312, 190, 40, 30, BLUE, True)
s.text(f"{nva.loc['Anonymous', 'recommend_fav']:.1f}%", 250, 312, 190, 40, 30, DARK, True)
body(s, f"On the six fix-first questions, named respondents are {nva.loc['Named', 'fix_first_items_fav']:.0f}% favourable and anonymous respondents {nva.loc['Anonymous', 'fix_first_items_fav']:.0f}%.", 48, 372, 400, 12.5, 48, INK)
s.line(480, 171, 480, 445)
s.label("How to read this deck", 512, 171, 400)
for i, line in enumerate([
    "327 responses. Headcount was not supplied, so the response rate is unknown.",
    "Favourable = 4–5 (Usually / Almost always). 3 = Sometimes, not neutral.",
    "54 people (16.5%) gave the same answer to all 30 questions; the priority order is unchanged without them.",
    "Comments were coded with AI assistance and re-reviewed once; not independently validated.",
    "Links to outcomes are associations from one survey, not proven causes.",
]):
    s.rect(512, 208 + i * 47, 5, 5, BLUE)
    body(s, line, 528, 201 + i * 47, 384, 12, 36, MUTED)
s.rule_note("The gap fits people being more guarded when named, but those who chose to name themselves may also differ.")

# 04 — Strengths
s = Slide("Strengths to protect", "Pride and helpful colleagues\nare assets to protect", "Improvement should build on what employees already value.",
          "item_evidence_profile.csv (PRI2, PRI1, CAM1); employee_voice_topic_summary.csv (preserve topic t); notebook §8.",
          "Three items show a strong foundation: 95.7% understand their contribution to business success, 92.4% are proud to work for Safewater Lines and 91.1% report help within their own team. In the 'what should we never lose' question, 119 respondents name their team or colleagues. Pride items are among the strongest associations with recommending and intending to stay (Spearman about 0.5–0.6), so protecting them matters for retention, not only for morale. Own-team support is high but only weakly related to the outcomes. Use all three as guardrails: the pilot should not erode them.")
for y, code, label in [(185, "PRI2", "Understand contribution to business success"), (268, "PRI1", "Proud to work for Safewater Lines"), (351, "CAM1", "Help and support within own team")]:
    body(s, label, 48, y, 550, 15, 30, bold=True)
    s.rect(48, y + 35, 640, 13, LIGHT)
    s.rect(48, y + 35, fav(code) / 100 * 640, 13, DARK)
    s.text(f"{fav(code):.1f}%", 731, y + 6, 175, 49, 32, BLUE, True, "right")
s.rule_note("119 people name their team or colleagues as what to never lose. Pride also moves closely with intending to stay.")

# 05 — Dimensions
s = Slide("Survey landscape", "Fairness is the weakest survey block", "Favourable share of answers per block; mean on the 1–5 scale.",
          "survey_clean.csv; five items per block; 1,635 valid answers per block; equal-weight working means.",
          "Pride has the highest favourable share and Fairness the lowest. Respect and Camaraderie sit below Credibility and Overall experience. Each block has five complete items and 1,635 valid answers. The block labels come from the questionnaire and are not proven to be statistically distinct, so the next slides work at the level of individual questions. Do not compare these figures with an external benchmark or an official Trust Index; there is no valid matching basis.")
s.text("SURVEY BLOCK", 48, 169, 220, 18, 10, MUTED, True)
s.text("FAVOURABLE SHARE  /  0–100%", 280, 169, 400, 18, 10, MUTED, True)
s.text("MEAN / 5", 790, 169, 122, 18, 10, MUTED, True, "right")
for i, (d, label) in enumerate([("PRI", "Pride"), ("OVR", "Overall experience"), ("CRE", "Credibility"), ("CAM", "Camaraderie"), ("RES", "Respect"), ("FAI", "Fairness")]):
    y = 201 + 39 * i
    cols = [f"{d}{j}" for j in range(1, 6)]
    share = float(df[cols].ge(4).to_numpy().mean() * 100)
    avg = float(df[cols].to_numpy().mean())
    if d == "FAI": s.rect(40, y - 6, 880, 35, PALE)
    s.text(label, 48, y, 217, 24, 14, INK, d == "FAI")
    s.rect(280, y + 5, 380, 12, LIGHT)
    s.rect(280, y + 5, share / 100 * 380, 12, BLUE if d == "FAI" else DARK)
    s.text(f"{share:.1f}%", 681, y - 1, 90, 26, 16, BLUE, d == "FAI", "right")
    s.text(f"{avg:.2f}", 800, y, 112, 25, 14, MUTED, align="right")
s.rule_note(f"Fairness is also the block most linked to recommending, satisfaction and staying: {FAI_SHARE:.0f}% of the explained variation.")

# 06 — Priority matrix
s = Slide("What to fix first", "Six questions matter most and\nscore below the median: fix these first",
          f"Link to recommend / satisfied / stay 3–5 years (relative weights, R² = {R2:.2f}) against today's favourable share; 19 actionable questions.",
          "priority_matrix.csv; driver_model_summary.csv; notebook Step 7.1. Pride and belonging excluded as near-outcomes.",
          f"The vertical axis shows how much of the variation in recommending, satisfaction and intention to stay each question accounts for, using relative-weights analysis, which handles correlated questions fairly. Together the 19 questions explain {R2:.0%} of that variation. The horizontal axis is today's favourable share. The shaded corner holds questions that matter more than average and score below the median: leaders acting on feedback, equal growth opportunities, teams working together, fair rewards, consistent decisions and understanding decisions. Confidence intervals overlap, so read this as tiers, not exact ranks. The order is unchanged without straight-liners. Among anonymous respondents recognition rises into the top tier and cross-team work drops out. These are associations, not causes.")
px0, px1, py0, py1, fx0, fx1, iy1 = 100, 600, 178, 440, 70, 93, 10
X = lambda f: px0 + (f - fx0) / (fx1 - fx0) * (px1 - px0)
Y = lambda i: py1 - i / iy1 * (py1 - py0)
mf, mi = pm["fav_pct"].median(), pm["importance_pct"].median()
s.rect(px0, py0, X(mf) - px0, Y(mi) - py0, PALE)
s.line(px0, py1, px1, py1, MID, .8)
s.line(px0, py0, px0, py1, MID, .8)
s.line(X(mf), py0, X(mf), py1, LINE, .8)
s.line(px0, Y(mi), px1, Y(mi), LINE, .8)
for f in range(70, 95, 5):
    s.text(str(f), X(f) - 15, py1 + 4, 30, 12, 9, MUTED, align="center")
for i in range(0, 11, 2):
    s.text(str(i), px0 - 32, Y(i) - 6, 26, 12, 9, MUTED, align="right")
s.text("Link to outcomes (% of explained variation)", px0, 162, 300, 13, 9, MUTED, True)
s.text("Favourable % →", X(90) + 22, py1 + 4, 80, 12, 9, MUTED, True)
s.text("FIX FIRST", px0 + 6, py0 + 5, 120, 12, 9.5, BLUE, True)
s.text("PROTECT", px1 - 106, py0 + 5, 100, 12, 9.5, MUTED, True, "right")
s.text("MONITOR", px0 + 6, py1 - 16, 100, 12, 9.5, MUTED, True)
s.text("MAINTAIN", px1 - 106, py1 - 16, 100, 12, 9.5, MUTED, True, "right")
NAMES = {"CRE5": "Leaders act on feedback", "FAI2": "Equal growth opportunities", "CAM2": "Teams work together",
         "FAI1": "Fair rewards & recognition", "FAI3": "Consistent decisions", "FAI5": "Understand decisions",
         "CRE3": "Confidence in direction", "RES3": "Safe to share views", "RES2": "Resources & support",
         "FAI4": "Fair workload", "CRE2": "Leaders keep promises", "RES5": "Dignity & respect",
         "RES4": "Efforts recognised", "CAM5": "Successes celebrated", "RES1": "Manager support",
         "CRE4": "Timely change updates", "CAM4": "Rely on other teams", "CRE1": "Open communication",
         "CAM1": "Own-team support"}
# Label offsets (dx, dy, align) are set by hand to avoid collisions; checked visually after each build.
LABEL_AT = {"CRE5": (0, -20, "center"), "FAI2": (-8, 2, "right"), "CAM2": (-8, 4, "right"), "RES3": (8, -12, "left"),
            "RES2": (8, -5, "left"), "FAI4": (8, -5, "left"), "CRE3": (8, 4, "left"), "FAI1": (8, -5, "left"),
            "FAI3": (-8, -12, "right"), "FAI5": (8, -5, "left"), "CRE2": (8, 2, "left"), "RES5": (8, -5, "left"),
            "RES4": (8, -12, "left"), "CAM5": (8, -3, "left"), "RES1": (8, -5, "left"), "CRE4": (8, 2, "left"),
            "CAM4": (8, -5, "left"), "CRE1": (8, -5, "left"), "CAM1": (-8, -6, "right")}
for code, r in pm.iterrows():
    x, y = X(r["fav_pct"]), Y(r["importance_pct"])
    first = r["quadrant"] == "Fix first"
    s.circle(x - 4.5, y - 4.5, 9, BLUE if first else MID)
    dx, dy, align = LABEL_AT[code]
    w = pdfmetrics.stringWidth(NAMES[code], "Arial-Bold" if first else "Arial", 8.5) + 2
    lx = x + dx if align == "left" else x + dx - w if align == "right" else x - w / 2
    s.text(NAMES[code], lx, y + dy, w, 11, 8.5, INK if first else MUTED, first, align)
s.line(640, 171, 640, 445)
s.label("Fix first  /  favourable today", 664, 171, 248)
for i, code in enumerate(pm.loc[FIX_FIRST].sort_values("fav_pct").index):
    body(s, NAMES[code], 664, 200 + i * 30, 180, 12, 16, bold=True)
    s.text(f"{pm.loc[code, 'fav_pct']:.1f}%", 852, 200 + i * 30, 60, 16, 12, BLUE, True, "right")
body(s, "Read as tiers: intervals overlap. Order unchanged without straight-liners.", 664, 392, 248, 10.5, 40, MUTED)
s.rule_note("Recognition scores lowest but links weakly overall; among anonymous respondents it rises into the top tier, so it joins Priority 1.", y=471)

# 07 — Evidence check
s = Slide("Evidence check", "Two themes are backed by\nall four sources of evidence", "Each source has a different weakness; a priority needs several of them to agree.",
          "priority_triangulation.csv; priority_matrix.csv; hr_priority_counts.csv; one_change_topics.csv; grading rules fixed in notebook Step 7.3.",
          "We checked every candidate theme against four independent sources: how low its questions score, how strongly they link to recommending, satisfaction and intention to stay, how many people chose it as the one thing HR should improve, and how many raise it when asked 'if you could make one change' (the only question that names no topic). Grading rules were fixed before looking at the result. Fair decisions with growth, and leaders listening and acting, are strong on all four. Recognition scores lowest and is raised often. Cross-team work links to outcomes but is mid-table on score and rarely raised unprompted. Pay and facilities have no rating question but are a clear HR request, so they are routed to the annual review rather than ignored.")
cols = [("THEME", 236), ("LOWEST SCORE", 118), ("OUTCOME LINK", 118), ("HR CHOICE", 118), ("'ONE CHANGE'", 118), ("DECISION", 156)]
x0, y0, hh, rh = 48, 171, 28, 33
s.rect(x0, y0, 864, hh, PALE)
pos = x0
for heading, w in cols:
    s.text(heading, pos + 9, y0 + 9, w - 18, 14, 9.5, BLUE, True)
    pos += w
DECISION = {"Fair, explainable people decisions & growth": "Priority 1", "Leaders listen and visibly act": "Priority 2",
            "Recognition of contributions": "Inside Priority 1", "Cross-team collaboration": "Targeted pilot",
            "Support when problems arise": "Via listening loop", "Workload & role clarity": "Inside handover pilot",
            "Pay, benefits & facilities": "Annual review"}
THEME_LABEL = {"Fair, explainable people decisions & growth": "Fair people decisions & growth",
               "Leaders listen and visibly act": "Leaders listen and act", "Recognition of contributions": "Recognition",
               "Cross-team collaboration": "Cross-team collaboration", "Support when problems arise": "Support with problems",
               "Workload & role clarity": "Workload & role clarity", "Pay, benefits & facilities": "Pay, benefits & facilities"}
for k, (theme, r) in enumerate(tri.iterrows()):
    y = y0 + hh + k * rh
    top = k < 2
    if top: s.rect(x0, y, 864, rh, "F7F9FA")
    s.text(THEME_LABEL[theme], x0 + 9, y + 9, 218, 16, 11.5, INK, top)
    cells = [(r["score"], "—" if pd.isna(r["lowest_fav_rank_of_30"]) else f"#{int(r['lowest_fav_rank_of_30'])} of 30"),
             (r["outcome_link"], "—" if pd.isna(r["max_p_top5_driver"]) else f"{r['max_p_top5_driver']:.0%} top-5"),
             (r["hr_choice"], "—" if pd.isna(r["hr_choice_pct"]) else f"{r['hr_choice_pct']:.0f}%"),
             (r["one_change"], f"{int(r['one_change_records'])} people")]
    pos = x0 + 236
    for g, txt in cells:
        grade_mark(s, g, pos + 9, y + 11)
        s.text(txt, pos + 25 if g != "—" else pos + 9, y + 9, 88, 15, 10.5, MUTED)
        pos += 118
    s.text(DECISION[theme], pos + 9, y + 9, 140, 15, 11, BLUE if top else MUTED, True)
    s.line(x0, y + rh, x0 + 864, y + rh, LINE, .6)
lx = 48
for g, txt in [("Strong", "Strong"), ("Medium", "Medium"), ("Weak", "Weak")]:
    grade_mark(s, g, lx, 440)
    s.text(txt, lx + 15, 438, 60, 14, 10, MUTED)
    lx += 80
s.text("— = no matching question or option", lx, 438, 260, 14, 10, MUTED)
s.rule_note("Score: rank of the lowest question · Outcome link: share of 500 resamples where a question is a top-5 driver · HR: % choosing it · One change: people raising it.", y=465)

# 08 — Priority 1
s = Slide("Priority 1  /  Fair people decisions", "Make people decisions fair,\nexplainable and visible", "The five lowest-scoring questions in the survey, plus growth opportunities, a top link to outcomes.",
          "item_evidence_profile.csv; driver_model_summary.csv; hr_priority_counts.csv; fairness_response_breadth.csv; quote verbatim, de-identified.",
          f"The five lowest questions in the survey all sit here: having efforts recognised, celebrating successes, decision consistency, understanding how decisions are made, and fair rewards and recognition. Equal growth opportunities scores higher but is one of the two strongest actionable links to outcomes. Fairness is the block most strongly linked to recommending, satisfaction and intention to stay ({FAI_SHARE:.0f}% of the explained variation), and 51 people chose career progression as the one thing HR should improve. Recognition belongs here: the fairness question itself asks whether recognition and rewards are fair, and recognition weighs more heavily among anonymous respondents. The 137 people with at least one fairness answer of 1–3 include 'Sometimes', so this is breadth, not the rate of unfair treatment. The quote is one verbatim, de-identified comment chosen because it is typical of the fairness answers.")
for i, (code, label) in enumerate([("RES4", "Efforts recognised"), ("CAM5", "Successes celebrated"), ("FAI3", "Consistent decisions"),
                                   ("FAI5", "Understand decisions"), ("FAI1", "Fair rewards & recognition"), ("FAI2", "Equal growth opportunities")]):
    stack(s, code, label, 48, 176 + i * 40, 174, 288)
s.line(641, 171, 641, 434)
s.text(f"{FAI_SHARE:.0f}%", 668, 171, 244, 44, 32, BLUE, True)
body(s, "of the explained link to staying and recommending comes from Fairness, the largest block", 668, 215, 244, 11.5, 42, INK)
s.text(f"{int(hr.loc['Help employees progress in their careers', 'respondents'])}", 668, 266, 244, 40, 28, BLUE, True)
body(s, "chose 'help employees progress in their careers' as HR's one fix", 668, 306, 244, 11.5, 30, INK)
quote(s, "“Inconsistent performance evaluations and opaque promotion criteria.”", 668, 356, 244, 60, 12)
legend(s, y=416)
s.rule_note("137 of 327 rated at least one fairness question 1–3. That includes Sometimes, so it is breadth, not the rate of unfair treatment.", y=471)

# 09 — Priority 2
s = Slide("Priority 2  /  Listen and act", "Leaders listen, and visibly act\non what they hear", "The most common HR request, the top actionable link to outcomes, and the most-raised change.",
          "hr_priority_counts.csv; priority_matrix.csv (CRE5); priority_triangulation.csv; quote verbatim, de-identified.",
          f"Asked to pick the one thing HR should do better, 67 people chose listening to employees and their concerns, the most common answer. Another 13 chose keeping employees informed. 'Leaders are willing to listen to employee feedback and act on it' is {fav('CRE5'):.1f}% favourable and is the question most strongly linked to recommending, satisfaction and staying among the actionable ones. In the open 'one change' question, {CV_RECORDS} people ask for better communication or follow-through, more than for any other theme. The ask is not more announcements; it is evidence that raising something leads to a response. Benefits and facilities come joint second in the HR question and are addressed on slide 12.")
s.label(f"If HR could do one thing better  /  n = {len(df)}", 48, 171, 560)
SHORT = {"Listening to employees and their concerns": "Listening to concerns", "Help employees progress in their careers": "Career progression",
         "Improve employee benefits and facilities": "Benefits & facilities", "Help resolve employee problems": "Resolving problems",
         "Recognising and appreciating good work": "Recognising good work", "Supporting employees when they need help": "Support when needed",
         "Making rules and processes simple": "Simpler rules & processes", "Being available and easy to approach": "Being approachable",
         "Employee activities and engagement": "Activities & engagement", "Keeping employees informed": "Keeping people informed"}
for i, (opt, r) in enumerate(hr.iterrows()):
    hbar(s, SHORT[opt], r["respondents"], hr["respondents"].max(), 48, 198 + i * 24, 168, 250,
         opt in ("Listening to employees and their concerns", "Keeping employees informed"))
s.line(560, 171, 560, 434)
s.text(f"{fav('CRE5'):.1f}%", 588, 171, 324, 44, 32, BLUE, True)
body(s, "say leaders act on feedback: the top actionable link to staying and recommending", 588, 215, 324, 11.5, 30, INK)
s.text(str(CV_RECORDS), 588, 254, 324, 40, 28, BLUE, True)
body(s, "people ask for better communication or follow-through as their 'one change', more than any other theme", 588, 294, 324, 11.5, 30, INK)
quote(s, "“Employees’ problems and suggestions should be heard and appropriate action taken promptly.”", 588, 348, 324, 60, 12)
s.rule_note("The ask is not more announcements. It is visible proof that raising something leads to a response.", y=465)

# 10 — Group hotspots
ROWS = [("All respondents", "All respondents"), ("Customer Service", "Customer Service"), ("Sales", "Sales"), ("Documentation", "Documentation"),
        ("Finance & Accounts", "Finance & Accounts"), ("Operations", "Operations"), ("0 - 3", "0–3 years"), ("3 - 5", "3–5 years"),
        ("5 - 10", "5–10 years"), ("10 - 15", "10–15 years"), ("15 & Above", "15+ years")]
METRICS = ["Fair decisions", "Growth", "Listen & act", "Recognition", "Cross-team", "Stay 3–5 yrs"]
gap = {m: hot.loc["Male", m] - hot.loc["Female", m] for m in ["Fair decisions", "Growth", "Listen & act", "Recognition"]}
assert 9 <= min(gap.values()) and max(gap.values()) <= 13
s = Slide("Where to start", "Start where the gaps are largest:\nCustomer Service and 3–5-year staff", "% favourable on the priority questions by group; darker = lower. Groups with n ≥ 10.",
          "group_hotspots.csv; notebook Step 7.5. Smaller departments and the mixed 'Other' group not shown.",
          f"Customer Service is lowest or close to lowest on every priority column: recognition {hot.loc['Customer Service', 'Recognition']:.0f}%, fair decisions {hot.loc['Customer Service', 'Fair decisions']:.0f}% and intention to stay {hot.loc['Customer Service', 'Stay 3–5 yrs']:.0f}%. The 3–5-year group dips on fair decisions, recognition and intention to stay. Women are {min(gap.values()):.0f}–{max(gap.values()):.0f} points below men on fair decisions, growth, listening and recognition. Use this to choose where to pilot and listen first, not to rank or blame teams. Groups overlap, and composition or role mix could explain part of each pattern.")
gx, gy, lw, cw, rh = 48, 171, 214, 108, 22
s.rect(gx, gy, lw + cw * 6, 26, PALE)
s.text("GROUP (n)", gx + 9, gy + 8, lw - 18, 13, 9.5, BLUE, True)
for j, m in enumerate(METRICS):
    s.text(m.upper(), gx + lw + j * cw, gy + 8, cw, 13, 9.5, BLUE, True, "center")
for i, (key, label) in enumerate(ROWS):
    y = gy + 30 + i * rh + (6 if i >= 1 else 0) + (6 if i >= 6 else 0)
    n = int(hot.loc[key, "n"])
    s.text(f"{label} ({n})", gx + 9, y + 4, lw - 18, 14, 11, INK, i == 0)
    for j, m in enumerate(METRICS):
        v = float(hot.loc[key, m])
        t = min(max((95 - v) / 35, 0), 1)
        s.rect(gx + lw + j * cw + 1, y, cw - 2, rh - 2, mix("EEF2F5", BLUE, t))
        s.text(f"{v:.0f}", gx + lw + j * cw, y + 4, cw, 14, 11, WHITE if t > .55 else INK, key == "Customer Service", "center")
s.rule_note(f"Women are {min(gap.values()):.0f}–{max(gap.values()):.0f} points below men on fair decisions, growth, listening and recognition (n = 67 vs 259).", y=471)

# 11 — Cross-team targeted pilot
s = Slide("Targeted fix  /  Cross-team", "Cross-team handovers: a real but\nnarrower gap to fix where it bites", "Own team versus other teams in the same responses. Ranks 9th of 30, and rarely raised unprompted.",
          "cross_team_deep_dive.csv; cross_team_paired_detail.csv; group_hotspots.csv; CAM1 × CAM2; n = 327.",
          f"Own-team support is 91.1% favourable versus 82.3% for cross-team collaboration. The paired table is the stronger evidence: 45 people rate their own team 4–5 but cross-team work 1–3, while only 16 show the reverse, which is unlikely to be chance. But cross-team collaboration ranks 9th of 30 questions, only 16 people raise teamwork in the open 'one change' question, and among anonymous respondents it drops out of the top tier of outcome links. So it is a targeted operational fix rather than the headline. Customer Service is lowest at {hot.loc['Customer Service', 'Cross-team']:.0f}%, so start there, and verify one real handover with both sides before designing anything.")
s.label("FAVOURABLE SHARE", 48, 171)
for y, code, label in [(208, "CAM1", "Own-team support"), (272, "CAM2", "Cross-team collaboration"), (336, "CAM4", "Support from other teams")]:
    s.text(label, 48, y, 390, 22, 13)
    s.rect(48, y + 26, 354, 12, LIGHT)
    s.rect(48, y + 26, fav(code) / 100 * 354, 12, DARK)
    s.text(f"{fav(code):.1f}%", 415, y + 15, 78, 33, 19, BLUE, True, "right")
s.line(523, 171, 523, 435)
s.text("45", 560, 169, 340, 65, 47, BLUE, True)
body(s, "Own team favourable; cross-team 1–3", 560, 234, 340, 14, 42, bold=True)
body(s, "13.8% of 327 respondents; only 16 show the reverse.", 560, 279, 340, 11.5, 35, MUTED)
table(s, ["Own team / cross-team", "1–3", "4–5"], [["1–3", "13", "16"], ["4–5", "45", "253"]], x=560, y=330, widths=[204, 68, 68], row_h=34, header_h=29, size=12)
s.rule_note(f"Customer Service is lowest on cross-team work ({hot.loc['Customer Service', 'Cross-team']:.0f}%). Start the handover pilot there; verify the actual workflow first.")

# 12 — What else we heard
s = Slide("Employee voice", "In their own words, people ask for\ncommunication, recognition and growth", f"'If you could make one change…', the only question that names no topic. {ONE_CHANGE_BASE} answers; one answer can raise several topics.",
          "one_change_topics.csv; hr_priority_counts.csv; priority_triangulation.csv; named_vs_anonymous.csv.",
          f"The open 'one change' question is the cleanest comment evidence, because it does not steer people towards a topic. Communication and decision explanations, recognition, career growth and follow-through lead; teamwork is raised by only 16 people. Pay, benefits and facilities matter too: 51 people chose 'improve employee benefits and facilities' as HR's one fix, and {int(tri.loc['Pay, benefits & facilities', 'one_change_records'])} raise pay or facilities here. These are outside a 90-day pilot, so say publicly that they go to the annual compensation and facilities review. Finally, fix the survey itself: drop the name field and collect headcount so a response rate can be reported.")
s.label("Topics raised  /  people", 48, 171, 500)
SHORT_T = {"c": "Communication & explanations", "r": "Recognition & feedback", "d": "Career growth & learning", "v": "Voice & follow-through",
           "w": "Workload & flexibility", "m": "Support & respect", "p": "Role clarity & processes", "s": "Facilities, tools & staffing",
           "t": "Teamwork & cross-team", "b": "Pay, incentives & benefits"}
for i, (code, r) in enumerate(one.loc[list(SHORT_T)].sort_values("records", ascending=False).iterrows()):
    hbar(s, SHORT_T[code], r["records"], one["records"].max(), 48, 198 + i * 24, 186, 232, code in ("c", "r", "d", "v"))
s.line(560, 171, 560, 434)
s.label("Heard, but outside a 90-day pilot", 588, 171, 324)
body(s, "Pay, benefits and facilities", 588, 198, 324, 13, 18, bold=True)
body(s, f"51 people (15.6%) chose this as HR's one fix. Route it to the annual compensation and facilities review, and say so publicly.", 588, 220, 324, 11.5, 56, MUTED)
s.label("Fix the survey itself", 588, 300, 324)
body(s, "Drop the name field", 588, 327, 324, 13, 18, bold=True)
body(s, f"69% gave their name, and anonymous respondents are about {nva.loc['Named', 'fix_first_items_fav'] - nva.loc['Anonymous', 'fix_first_items_fav']:.0f} points less favourable. Also collect headcount so a response rate can be reported.", 588, 349, 324, 11.5, 56, MUTED)
s.rule_note("Comments were coded with AI assistance and re-reviewed once; counts may shift slightly after independent validation.", y=465)

# 13 — Pilot design
s = Slide("Recommended response", "One 90-day pilot, three workstreams,\nclear accountability", "Built on existing processes and tools; starting in Customer Service plus one comparison area.",
          "implementation_roadmap_0_90_days.csv (adapted to the revised priorities); proposed actions, not approved commitments.",
          "Priority 1 is owned by the HR head with business heads: publish the criteria for appraisal, promotion and reward in the pilot roles, record and share the reason for each decision with a route to ask for review, and have managers give each person specific recognition every month. Priority 2 is owned by a leadership sponsor with HR: log every raised concern with an owner and a next-update date, publish a monthly 'you said, we did' update, and hold skip-level listening sessions starting in Customer Service. The handover pilot is owned by the Operations head with both team leads. All owners are proposals. No new platform is assumed. Specific accounts about facilities, respectful treatment or working-time boundaries need confidential verification through existing routes.")
for x, tag, owner, steps, effort, day30 in [
    (48, "P1  /  Fair decisions & recognition", "HR head + business heads",
     ["Publish appraisal, promotion and reward criteria for pilot roles.", "Record and share the reason for each decision; offer a review route.", "Managers give each person specific recognition every month."],
     "Effort: medium · existing HR processes", "Day 30: criteria published for all pilot roles."),
    (344, "P2  /  Listen and act", "Leadership sponsor + HR",
     ["Log each raised concern with an owner and next-update date.", "Publish a monthly 'you said, we did' update.", "Hold skip-level listening sessions, Customer Service first."],
     "Effort: low · leadership time, no new system", "Day 30: log live; first monthly update sent."),
    (640, "Pilot  /  Cross-team handover", "Operations head + both team leads",
     ["Map one Customer Service handover with both sides.", "Define required information, receiver and backup.", "Acknowledge receipt; escalate when overdue."],
     "Effort: low–medium · reuse existing tools", "Day 30: checklist and owners agreed."),
]:
    s.rect(x, 171, 272, 30, PALE)
    s.text(tag, x + 10, 179, 256, 16, 12, BLUE, True)
    s.text("OWNER", x, 214, 272, 13, 9, BLUE, True)
    body(s, owner, x, 229, 272, 12.5, 16, bold=True)
    for i, step in enumerate(steps):
        s.text(f"{i+1:02d}", x, 262 + i * 42, 24, 14, 10.5, BLUE, True)
        body(s, step, x + 26, 260 + i * 42, 244, 11.5, 30)
    body(s, effort, x, 394, 272, 10.5, 14, MUTED, True)
    body(s, day30, x, 414, 272, 10.5, 28, MUTED)
s.rule_note("Specific accounts about working conditions or treatment need confidential verification through existing routes.", y=465)

# 14 — Roadmap
s = Slide("Implementation", "A 90-day pilot turns\nthe findings into a decision", "Day 0 begins at organisational approval, not at the assignment deadline.",
          "implementation_roadmap_0_90_days.csv; roadmap_decision_gates.csv (adapted to the revised priorities); all standards and owners are proposals.",
          "Day 0 is organisational approval of scope, sponsor, owners and capacity. In the first 14 days, choose the pilot area (Customer Service first), review existing criteria and run an anonymous baseline pulse on the priority questions. Days 15–30 publish criteria, assign owners, open the concern-to-action log and agree the handover checklist. Days 31–60 run monthly recognition and updates, review handover exceptions weekly, and check burden and usefulness. Days 61–90 repeat the anonymous pulse, compare process measures, confirm pride and belonging held, and decide whether to scale, adapt or stop.")
phases = [
    ("DAYS 0–14", "Verify and baseline", "Pick pilot area (Customer Service first).\nReview current criteria.\nRun anonymous baseline pulse.", "HR + functional owners", "Gate: approve scope and targets"),
    ("DAYS 15–30", "Make the pilot ready", "Publish criteria; assign owners.\nOpen the concern-to-action log.\nAgree the handover checklist.", "Pilot managers + HR", "Gate: continue or adapt"),
    ("DAYS 31–60", "Run and improve", "Monthly recognition and updates.\nWeekly handover exception review.\nCheck burden and usefulness.", "Workstream owners", "Gate: review progress"),
    ("DAYS 61–90", "Evaluate and decide", "Repeat the anonymous pulse.\nCompare process measures.\nCheck pride and belonging held.", "Sponsor + HR + owners", "Gate: scale, adapt or stop"),
]
for i, (time, title, detail, owner, gate) in enumerate(phases):
    x = 48 + i * 222
    s.rect(x, 173, 198, 3, BLUE)
    s.label(time, x, 193, 198)
    body(s, title, x, 231, 197, 17, 51, bold=True)
    body(s, detail, x, 299, 197, 12, 88, MUTED)
    body(s, owner, x, 403, 197, 11, 37, BLUE, True)
    body(s, gate, x, 455, 197, 10, 29, MUTED)

# 15 — Measures
s = Slide("Measures of success", "Measure the process and\nwhether employees notice", "Process checks show the pilot ran; repeated anonymous questions show whether it helped.",
          "roadmap_kpi_dictionary.csv; item_evidence_profile.csv; group_hotspots.csv; named_vs_anonymous.csv. Targets are indicative.",
          "Each workstream has a process check and an experience check. The process checks are design standards, not survey predictions. The experience checks repeat the exact survey questions in an anonymous pulse, so results are comparable and less affected by the name field. The +5-point figures are indicative and should be confirmed at Day 14 once the pilot baseline is known; a before-and-after change alone does not prove the pilot caused it. Guardrails make sure the pilot does not erode pride, own-team support or intention to stay.")
table(s, ["WORKSTREAM", "PROCESS CHECK", "EXPERIENCE CHECK  /  TODAY"], [
    ["Fair decisions & recognition", "Criteria published for 100% of pilot roles by Day 30; a reason recorded for every decision; monthly recognition.", f"FAI1 / FAI3 / FAI5 / RES4: {fav('FAI1'):.0f} / {fav('FAI3'):.0f} / {fav('FAI5'):.0f} / {fav('RES4'):.0f}%. Indicative: +5 points by Day 90."],
    ["Listen and act", "Concerns acknowledged within 2 business days; owner and update date within 5; monthly 'you said, we did'.", f"CRE5: {fav('CRE5'):.1f}%. Indicative: +5 points; ask 'did you see a useful change?'"],
    ["Cross-team handover", "≥95% of in-scope handovers complete by Day 60; timeliness target set after the baseline.", f"CAM2 / CAM4: {fav('CAM2'):.1f} / {fav('CAM4'):.1f}% (Customer Service CAM2 {hot.loc['Customer Service', 'Cross-team']:.0f}%)."],
    ["Guardrails", "No extra reporting burden beyond the agreed logs.", f"Should not fall: pride {fav('PRI1'):.0f}%, own-team support {fav('CAM1'):.0f}%, stay {fav('PRI3'):.0f}% (anonymous {nva.loc['Anonymous', 'stay_3_5_yrs_fav']:.0f}%)."],
], widths=[150, 330, 384], row_h=58, header_h=31, size=10.5)
s.rule_note("Measure with an anonymous pulse; report n and the anonymous share. Confirm numerical targets at Day 14.", y=475)

# 16 — Leadership decision
s = Slide("Leadership decision", "Three decisions to start on Monday", "A bounded, measurable pilot rather than a broad programme.",
          "FINAL_ANALYSIS_SYNTHESIS.md; implementation_roadmap_0_90_days.csv; roadmap_decision_gates.csv; notebook Step 7.6.",
          "Close with three specific decisions. First, approve one 90-day pilot covering fair decisions and recognition, the listen-and-act loop, and one Customer Service handover. Second, name the owners (a leadership sponsor, the HR head and the Operations head) and protect their time with a monthly review. Third, run the next survey anonymously: remove the name field, run a baseline pulse in the first 14 days and repeat it at Day 90. Invite discussion on which pilot roles and which handover matter most to verify first.")
for y, n, title, detail in [
    (174, "01", "Approve one 90-day pilot", "Fair decisions and recognition, the listen-and-act loop, and one Customer Service handover."),
    (265, "02", "Name owners and protect their time", "Leadership sponsor, HR head and Operations head; one review per month."),
    (356, "03", "Run the next survey anonymously", "Remove the name field; baseline pulse in the first 14 days, repeated at Day 90."),
]:
    s.text(n, 48, y, 60, 45, 28, BLUE, True)
    body(s, title, 138, y, 760, 19, 32, bold=True)
    body(s, detail, 138, y + 39, 760, 13.5, 39, MUTED)
s.rule_note("Protect pride and belonging while making people decisions fairer and showing employees they were heard.", y=473)

# 17 — Methodology appendix
s = Slide("Reference  /  Methodology", "Methods were selected for the decision", "The notebook contains the full research trail and methodology reference.",
          "ANALYSIS_FROM_DATA_TO_ACTION.md §12; notebooks/00_data_understanding_eda.ipynb, Step 7 and final methodology cell.",
          "Primary evidence is counts, distributions, favourable shares and paired comparisons. Working means assume equal category spacing and weights. Step 7 adds relative-weights analysis on 19 actionable questions (pride and belonging excluded as near-outcomes) with 500 bootstrap resamples, and a four-source evidence check with grading rules fixed before reading the result. Comment analysis uses 15 explicit overlapping topics with stance, assisted by AI and re-reviewed once; it is not independently validated. Exact bigrams and trigrams help navigate phrases. The topic network describes same-answer co-mentions and is prompt-sensitive. Sensitivity checks exclude straight-liners and use anonymous respondents only. None of these establishes causation.", appendix=True)
table(s, ["METHOD", "PURPOSE / USE", "BOUNDARY"], [
    ["Audit + distributions", "Check source, wording, valid n and category shares.", "Supplied records; population coverage unknown."],
    ["Means + diagnostics", "Summarise blocks; alpha and rank associations explored.", "Descriptive scores; coherence ≠ validity or cause."],
    ["Relative-weights drivers", "Share outcome R² across 19 actionable items; 500 bootstraps.", "Associations; halo and ceiling effects; read as tiers."],
    ["Four-source evidence check", "Score, outcome link, HR choice and 'one change' comments.", "Grading thresholds are project rules set in advance."],
    ["Paired comparisons", "Compare own-team and cross-team in each record.", "Shows a pattern, not which workflow causes it."],
    ["Contextual topic coding", "15 overlapping topics; bigrams/trigrams for navigation.", "AI-assisted interpretation; human validation pending."],
    ["Topic network", "Explore same-answer topic co-mentions.", "Prompt-sensitive; not a causal or employee network."],
    ["Sensitivity checks", "Without straight-liners; anonymous only; comment re-review.", "Exclusion is not bias correction; no attrition model."],
], widths=[180, 331, 353], row_h=36, header_h=30, size=10.2)

# 18 — Confidence / robustness
cmp_items = [("Recognition / RES4", "RES4"), ("Consistency / FAI3", "FAI3"), ("Listen and act / CRE5", "CRE5"), ("Cross-team / CAM2", "CAM2"), ("Pride / PRI1", "PRI1")]
rho = pm[["importance_pct", "imp_no_straightliners", "imp_anonymous_only"]].corr(method="spearman")
s = Slide("Reference  /  Confidence", "The priorities hold up under\nthe main robustness checks", "Sensitivity checks inform interpretation; they do not turn a descriptive survey into a causal study.",
          "item_evidence_profile.csv; priority_matrix.csv; named_vs_anonymous.csv; coding_review_before_after.csv; assistant_review_status.csv.",
          f"Favourable shares fall when straight-liners are excluded and fall further among anonymous respondents, but the ordering of strengths and gaps is the same: pride stays high, and fairness, recognition and listening stay lowest. The driver ranking is identical without straight-liners (Spearman {rho.iloc[0, 1]:.2f}). Among the {ANON_N} anonymous respondents it shifts (Spearman {rho.iloc[0, 2]:.2f}): growth, fair rewards and leaders acting on feedback stay in the top tier, recognition rises into it and cross-team work drops out. That small group points the same way as the evidence check. The comment re-review covered 568 comments and changed 53 decisions; 75 cases still need context, and no independent coder was available.", appendix=True)
s.label("Favourable share under each check", 48, 171, 470)
table(s, ["QUESTION", "ALL", "NO STRAIGHT-LINERS", "ANONYMOUS"],
      [[lab, f"{fav(c):.1f}%", f"{item.loc[c, 'fav_without_straightliners_pct']:.1f}%", f"{fav_anon(c):.1f}%"] for lab, c in cmp_items],
      x=48, y=198, widths=[176, 74, 136, 100], row_h=40, header_h=30, size=11)
s.label("Driver ranking stability", 568, 171, 344)
s.text(f"ρ = {rho.iloc[0, 1]:.2f}", 568, 198, 130, 32, 22, BLUE, True)
body(s, f"without straight-liners (n = {int(len(df) - df['straightliner'].sum())})", 700, 205, 212, 11.5, 30, MUTED)
s.text(f"ρ = {rho.iloc[0, 2]:.2f}", 568, 246, 130, 32, 22, BLUE, True)
body(s, f"anonymous only (n = {ANON_N}): recognition rises, cross-team drops", 700, 249, 212, 11.5, 44, MUTED)
s.label("Comment review", 568, 318, 344)
for y, value, label in [(344, "568", "comments reread"), (376, "53", "decisions revised"), (408, "75", "cases still need context")]:
    s.text(value, 568, y, 70, 26, 20, BLUE, True)
    body(s, label, 650, y + 5, 262, 12, 18, MUTED)
s.rule_note("Independent human validation of the comment coding remains outstanding.", y=475)

# 19 — Segment follow-up
s = Slide("Reference  /  Follow-up", "Use group patterns to guide listening,\nnot to assign blame", "Selected descriptive examples; group composition and response selection may influence differences.",
          "focused_group_profile.csv; cross_team_fairness_overlap.csv; whole-study n = 327; selected groups n ≥ 10.",
          "The 3–5-year tenure group and Customer Service are examples for further listening, not a ranking of problem groups. Eleven of 53 responses in the 3–5-year group show favourable own-team support and a 1–3 cross-team rating; 27 have at least one fairness item at 1–3. Corresponding Customer Service counts are 10 of 51 and 29 of 51. Departments and tenure groups overlap, so they are not independent comparisons. Composition, selection, role mix and working context could explain patterns. The heterogeneous Other grouping is unsuitable for a simple team-level diagnosis. Cross-team and fairness patterns overlap for 47 records but 90 records have a fairness item at 1–3 despite favourable cross-team collaboration, which is why the two themes should not be collapsed into one explanation.", appendix=True)
table(s, ["SCOPE", "VALID n", "OWN-TEAM 4–5 / CROSS-TEAM 1–3", "≥1 FAIRNESS ITEM AT 1–3"], [
    ["Full study", "327", "45 / 327  ·  13.8%", "137 / 327  ·  41.9%"],
    ["Tenure: 3–5 years", "53", "11 / 53  ·  20.8%", "27 / 53  ·  50.9%"],
    ["Customer Service", "51", "10 / 51  ·  19.6%", "29 / 51  ·  56.9%"],
], widths=[192, 76, 306, 290], row_h=59, header_h=43, size=12)
body(s, "Follow up with contrasting experiences and verified work examples before choosing the pilot workflow.", 48, 421, 864, 16, 50, bold=True)
s.rule_note("1–3 includes Sometimes. These examples do not establish department effects, causes or fairness-incident prevalence.", y=475)

# 20 — Network, interpreted conservatively
s = Slide("Reference  /  Topic connections", "The topic map helps organise discussion", "VOSviewer-inspired exploration of same-answer co-mentions; not a causal map or a native VOSviewer run.",
          "topic_network_edges.csv; topic_network_parameter_sensitivity.csv; reports/network/topic_network_data.json.",
          "The full primary network includes 1,230 topic-coded suggestion/mixed answers from 305 response records, 13 displayed topics and 34 links supported by at least ten answers. This slide shows a selected five-topic excerpt using original node support and same-answer counts; positions are schematic, not analytical distances. Communication and teamwork co-occur in 98 answers from 93 records; 85 of those answers arise from the teamwork prompt. Fairness and career co-occur in 46 answers from 43 records; 41 come from the fairness prompt. Prompt dependence and parameter sensitivity limit any claim that the graph independently validates a mechanism. Node sizes represent unique-record support within the primary network context, line widths represent answer co-mentions. The offline interactive map provides question exclusion and further context.", appendix=True)

network = json.loads((ROOT / "reports/network/topic_network_data.json").read_text())
edges = pd.read_csv(TABLES / "topic_network_edges.csv")
positions = {"c": (170, 241), "t": (170, 400), "r": (450, 241), "d": (450, 400), "f": (590, 320)}
labels = {"c": "Communication", "t": "Teamwork", "r": "Recognition", "d": "Career / learning", "f": "Fairness"}
for a, b in [("c", "t"), ("c", "r"), ("d", "r"), ("f", "r"), ("d", "f")]:
    row = edges.loc[((edges.a == a) & (edges.b == b)) | ((edges.a == b) & (edges.b == a))].iloc[0]
    ax, ay = positions[a]; bx, by = positions[b]
    s.line(ax, ay, bx, by, MID, 1 + float(row.comments) / 35)
    if (a, b) == ("c", "t"):
        s.rect(187, 310, 40, 22, WHITE)
        s.text(str(int(row.comments)), 187, 313, 40, 19, 12, BLUE, True, "center")

# Support is read from the same primary context as the exported map.
primary = network["contexts"]["all"]
assert primary["comment_n"] == 1230 and primary["contributor_n"] == 305
support = {node["id"]: node["people"] for node in primary["nodes"]}
assert len(support) == 13
for code, (x, y) in positions.items():
    diameter = math.sqrt(support[code]) * 3.5
    s.circle(x - diameter / 2, y - diameter / 2, diameter, BLUE)
    s.text(labels[code], x - 83, y - diameter / 2 - 29, 166, 22, 12, INK, True, "center")
s.line(658, 171, 658, 450)
s.label("READ WITH THE PROMPTS", 692, 172, 220)
body(s, "Communication × teamwork", 692, 210, 220, 13, 43, bold=True)
body(s, "98 co-mentions; 85 arise from the teamwork prompt.", 692, 258, 220, 12.5, 57, MUTED)
body(s, "Fairness × career", 692, 340, 220, 13, 35, bold=True)
body(s, "46 co-mentions; 41 arise from the fairness prompt.", 692, 383, 220, 12.5, 57, MUTED)
s.rule_note("Selected excerpt: node area reflects record support; line width indicates co-mentions. Positions are schematic.", y=475)

MAIN = sum(not sc.appendix for sc in slides)
APPX = len(slides) - MAIN


def hex_rgb(value):
    return RGBColor.from_string(value)


DECK = "Safewater_Lines_People_Experience"
TITLE = "Safewater Lines | People Experience"


def render_pptx(name=DECK, title=TITLE, sources=True):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Pt(W), Pt(H)
    props = prs.core_properties
    props.title = title
    props.subject = "Survey findings and proposed 90-day organisational pathway"
    props.author = "Safewater Lines People Analytics Project"
    props.keywords = "employee survey, fairness, listening, recognition, people analytics"
    for scene in slides:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = hex_rgb(WHITE)
        for obj in scene.objects:
            if not sources and obj.get("role") == "source":
                continue
            kind = obj["kind"]
            if kind == "line":
                shape = slide.shapes.add_connector(1, Pt(obj["x"]), Pt(obj["y"]), Pt(obj["x2"]), Pt(obj["y2"]))
                shape.line.color.rgb = hex_rgb(obj["color"])
                shape.line.width = Pt(obj["width"])
            elif kind in {"rect", "circle"}:
                shape = slide.shapes.add_shape(MSO_SHAPE.OVAL if kind == "circle" else MSO_SHAPE.RECTANGLE,
                    Pt(obj["x"]), Pt(obj["y"]), Pt(obj["w"]), Pt(obj["h"]))
                shape.fill.solid()
                shape.fill.fore_color.rgb = hex_rgb(obj["fill"])
                if obj["stroke"]:
                    shape.line.color.rgb = hex_rgb(obj["stroke"])
                else:
                    shape.line.fill.background()
            elif kind == "text":
                shape = slide.shapes.add_textbox(Pt(obj["x"]), Pt(obj["y"]), Pt(obj["w"]), Pt(obj["h"]))
                tf = shape.text_frame
                tf.clear()
                tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
                tf.word_wrap = False
                tf.auto_size = MSO_AUTO_SIZE.NONE
                tf.vertical_anchor = MSO_ANCHOR.TOP
                p = tf.paragraphs[0]
                p.text = "\v".join(obj["lines"])
                p.font.name, p.font.size = "Arial", Pt(obj["size"])
                p.font.bold = obj["bold"]
                p.font.color.rgb = hex_rgb(obj["color"])
                p.line_spacing = Pt(obj["size"] * obj["leading"])
                p.space_before = p.space_after = Pt(0)
                from pptx.enum.text import PP_ALIGN
                p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[obj["align"]]
            # Explicit empty effects override PowerPoint's inherited theme shadows.
            shape._element.spPr.append(OxmlElement("a:effectLst"))
        slide.notes_slide.notes_text_frame.text = scene.notes + ("\n\nEVIDENCE\n" + scene.source + "\nFull methodology: reports/ANALYSIS_FROM_DATA_TO_ACTION.md and notebook Step 7." if sources else "")
    pptx_path = OUT / f"{name}.pptx"
    prs.save(pptx_path)
    return pptx_path


def render_pdf(name=DECK, title=TITLE, sources=True):
    path = OUT / f"{name}.pdf"
    pdf = canvas.Canvas(str(path), pagesize=(W, H))
    pdf.setTitle(title)
    pdf.setAuthor("Safewater Lines People Analytics Project")
    def color(hex_value):
        return tuple(int(hex_value[i:i+2], 16) / 255 for i in (0, 2, 4))
    for scene in slides:
        for obj in scene.objects:
            if not sources and obj.get("role") == "source":
                continue
            kind = obj["kind"]
            if kind == "line":
                pdf.setStrokeColorRGB(*color(obj["color"]))
                pdf.setLineWidth(obj["width"])
                pdf.line(obj["x"], H - obj["y"], obj["x2"], H - obj["y2"])
            elif kind in {"rect", "circle"}:
                pdf.setFillColorRGB(*color(obj["fill"]))
                if obj["stroke"]: pdf.setStrokeColorRGB(*color(obj["stroke"]))
                if kind == "circle":
                    pdf.ellipse(obj["x"], H - obj["y"] - obj["h"], obj["x"] + obj["w"], H - obj["y"], fill=1, stroke=int(bool(obj["stroke"])))
                else:
                    pdf.rect(obj["x"], H - obj["y"] - obj["h"], obj["w"], obj["h"], fill=1, stroke=int(bool(obj["stroke"])))
            elif kind == "text":
                font = "Arial-Bold" if obj["bold"] else "Arial"
                pdf.setFont(font, obj["size"])
                pdf.setFillColorRGB(*color(obj["color"]))
                for i, line in enumerate(obj["lines"]):
                    x = obj["x"]
                    tw = pdfmetrics.stringWidth(line, font, obj["size"])
                    if obj["align"] == "right": x += obj["w"] - tw
                    elif obj["align"] == "center": x += (obj["w"] - tw) / 2
                    pdf.drawString(x, H - obj["y"] - obj["size"] * .91 - i * obj["size"] * obj["leading"], line)
        pdf.showPage()
    pdf.save()
    return path


def validate(pptx_path, pdf_path, preview=PREVIEW, qa_path=HERE / "qa_results.json"):
    from pptx import Presentation as ReadPresentation
    import pymupdf
    preview.mkdir(parents=True, exist_ok=True)
    main = sum(not sc.appendix for sc in slides)
    reopened = ReadPresentation(pptx_path)
    assert len(reopened.slides) == len(slides)
    assert all(s.has_notes_slide for s in reopened.slides)
    bounds = []
    for scene in slides:
        for o in scene.objects:
            if o["kind"] == "line":
                valid = min(o["x"], o["x2"]) >= 0 and max(o["x"], o["x2"]) <= W and min(o["y"], o["y2"]) >= 0 and max(o["y"], o["y2"]) <= H
            else:
                valid = o["x"] >= 0 and o["y"] >= 0 and o["x"] + o["w"] <= W + .1 and o["y"] + o["h"] <= H + .1
            if not valid: bounds.append({"slide": scene.number, "object": o})
    assert not bounds, bounds
    pdf = pymupdf.open(pdf_path)
    assert len(pdf) == len(slides)
    for old in preview.glob("slide-*.png"):
        old.unlink()
    thumbs = []
    for i, page in enumerate(pdf):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False)
        target = preview / f"slide-{i+1:02d}.png"
        pix.save(target)
        image = Image.open(target).convert("RGB")
        image.thumbnail((480, 270))
        thumbs.append(image)
    sheet = Image.new("RGB", (480 * 3, 300 * math.ceil(len(thumbs) / 3)), "#E8ECEF")
    draw = ImageDraw.Draw(sheet)
    for i, thumb in enumerate(thumbs):
        x, y = (i % 3) * 480, (i // 3) * 300
        sheet.paste(thumb, (x, y))
        draw.text((x + 12, y + 277), f"{i+1:02d}  {slides[i].section}", fill="#365F7B")
    sheet.save(preview / "contact-sheet.png")
    checks = {"slides": len(slides), "main_slides": main, "appendix_slides": len(slides) - main,
              "pptx_reopened": True, "all_slides_have_speaker_notes": True,
              "all_shapes_within_slide": True, "text_boxes_fit_using_Arial_metrics": True,
              "pdf_pages": len(pdf), "preview_engine": "PDF companion rendered by PyMuPDF; not a native PowerPoint render",
              "source_assertions": "327 records; 9810 answers; 45 paired discordant; 137 fairness breadth; 179 recognition requests; "
                                   "fix-first set; two themes strong on 4/4 lenses; Fairness largest driver block; top HR choice = listening"}
    qa_path.write_text(json.dumps(checks, indent=2) + "\n")


def write_notes(guide_path=HERE / "SPEAKER_GUIDE.md", json_path=HERE / "slide_content.json", intro=None, sources=True):
    intro = intro or [f"{MAIN} main slides, followed by {APPX} reference slides. Allow roughly 15 minutes for the main story (about a minute per slide); use the appendix for questions. Timing is a suggested rehearsal plan, not an assignment requirement.", "", "All suggested owners, standards and pilot actions require organisational decisions. Quotes are verbatim, de-identified and chosen as typical examples, not as evidence of frequency."]
    content = ["# Presentation storyline and speaker guide", "", *intro, ""]
    for s in slides:
        content.extend([f"## {s.number:02d} · {s.title.replace(chr(10), ' ')}", "", s.notes, "", "**Evidence:** " + s.source, ""])
    guide_path.write_text("\n".join(content))
    json_path.write_text(json.dumps([{"slide": s.number, "section": s.section, "title": s.title, "source": s.source, "notes": s.notes, "objects": [o for o in s.objects if sources or o.get("role") != "source"]} for s in slides], ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    pptx_path = render_pptx()
    pdf_path = render_pdf()
    validate(pptx_path, pdf_path)
    write_notes()
    print(f"Created {pptx_path}\nCreated {pdf_path}\n{len(slides)} slides ({MAIN} main + {APPX} appendix), notes, companion previews and layout checks complete.")
