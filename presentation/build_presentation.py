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
item = pd.read_csv(ROOT / "reports/tables/item_evidence_profile.csv").set_index("item")
topics = pd.read_csv(ROOT / "reports/tables/employee_voice_topic_summary.csv").set_index("topic_code")
rating_cols = [f"{d}{i}" for d in ["CRE", "RES", "FAI", "PRI", "CAM", "OVR"] for i in range(1, 6)]
assert len(df) == 327 and df[rating_cols].notna().sum().sum() == 9810
assert ((df.CAM1 >= 4) & (df.CAM2 <= 3)).sum() == 45
assert df[[f"FAI{i}" for i in range(1, 6)]].le(3).any(axis=1).sum() == 137
assert int(topics.loc["r", "request_record_n"]) == 179


def fav(code):
    return float(item.loc[code, "fav_%"])


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
    def __init__(self, section, title, subtitle, source, notes, appendix=False, cover=False):
        self.section, self.title, self.subtitle = section, title, subtitle
        self.source, self.notes, self.appendix = source, notes, appendix
        self.objects = []
        slides.append(self)
        self.number = len(slides)
        if not cover:
            self.text("SAFEWATER LINES  /  " + section.upper(), 48, 26, 864, 16, 9.5, BLUE, True)
            self.text(title, 48, 54, 864, 72, 28, INK, True, leading=1.12)
            self.text(subtitle, 48, 128, 864, 24, 11.5, MUTED)
        self.line(48, 500, 912, 500, LINE, .6)
        self.text("Source: " + source, 48, 510, 806, 21, 7.7, MUTED, leading=1.13)
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


# 01 — Cover
s = Slide("Executive presentation", "Strong foundations. More dependable execution.", "", 
          "Your Voice master survey; analysis snapshot 29 October 2026.",
          "Open with the organisational question: how can Safewater Lines preserve what employees value while making everyday work and people decisions more dependable? This presentation describes the supplied response pool, then proposes a bounded pilot. The title is a working interpretation of the evidence, not a measured causal model. Use the dashboard for questions, rather than walking through every metric. Presentation date is 30 October 2026 at TISS. Team names were not supplied, so no names or commitments have been invented.", cover=True)
s.text("SAFEWATER LINES", 48, 40, 700, 20, 12, BLUE, True)
s.text("PEOPLE EXPERIENCE  /  EXECUTIVE REVIEW", 48, 82, 800, 20, 10, MUTED)
s.rect(48, 135, 52, 4, BLUE)
s.text("Strong foundations.\nMore dependable execution.", 48, 163, 850, 116, 38, INK, True, leading=1.12)
s.text("An evidence-based pathway for cross-team work, fair people decisions\nand a better employee experience.", 48, 302, 850, 58, 18, MUTED, leading=1.3)
s.text("327 response records  ·  30 rating items  ·  1,892 comments", 48, 403, 850, 25, 14, INK)
s.text("30 OCTOBER 2026  /  TISS", 48, 454, 850, 18, 10, BLUE, True)

# 02 — Executive conclusion
s = Slide("Executive judgement", "Preserve pride. Improve coordination.\nMake people decisions clearer.",
          "Two improvement priorities, supported by three everyday management practices.",
          "item_evidence_profile.csv; paired_team_support_comparison.csv; final_focus_evidence_and_actions.csv.",
          "Lead with the recommendation. First protect the positive foundation: pride and own-team support. The first selected improvement priority is cross-team execution; 45 paired records show favourable own-team support and a 1–3 cross-team rating. The second is fairness of people decisions, where consistency, explanations and rewards have lower favourable shares. Recognition, role clarity/backup and visible follow-through support these priorities. These are evidence-informed organising choices, selected with the user, rather than a statistical ranking of causal drivers. The proposed response is a limited 90-day pilot, not an organisation-wide transformation promise.")
for y, label, heading, detail in [
    (171, "PRESERVE", "Pride and mutual support", f"{fav('PRI1'):.1f}% company pride; {fav('CAM1'):.1f}% help within own team."),
    (263, "PRIORITY 1", "Make cross-team execution dependable", "45 records: own-team support favourable, cross-team work rated 1–3."),
    (355, "PRIORITY 2", "Make people decisions consistent and explainable", f"{fav('FAI3'):.1f}% favourable on decision consistency; {fav('FAI5'):.1f}% on understanding decisions."),
]:
    s.line(48, y - 9, 912, y - 9)
    s.label(label, 48, y + 6, 128)
    body(s, heading, 199, y, 700, 19, 28, bold=True)
    body(s, detail, 199, y + 35, 700, 13, 37, MUTED)
s.rule_note("Proposed response: one cross-functional workflow and a defined set of pilot roles, reviewed over 90 days.")

# 03 — Base
s = Slide("Evidence base", "Start with the response base", "Describe the supplied records before drawing organisational conclusions.",
          "survey_clean.csv; codebook.csv; qualitative_coding_coverage.csv; assistant_review_status.csv.",
          "The master contains 327 response records and 30 complete rating items, giving 9,810 valid rating answers. There are six open-ended questions, 1,892 nonblank comments and 321 records with at least one comment. We have not independently confirmed that each record corresponds to a unique employee. Favourable is 4–5, unfavourable 1–2 and the middle category is Sometimes, not neutral. The culture mean is a custom equal-weight summary of 25 items, excluding overall experience; it is not a validated engagement index. Eligible workforce size is missing, so neither participation rate nor workforce representativeness is established. Qualitative coding remains interpretive and not independently human validated.")
for x, value, label in [(48, "327", "Response records"), (270, "30", "Complete rating items"), (492, "1,892", "Nonblank comments"), (714, "321", "Comment contributors")]:
    s.text(value, x, 173, 195, 58, 36, BLUE, True)
    body(s, label, x, 235, 195, 13, 35, MUTED)
s.line(48, 286, 912, 286)
s.label("SCORING", 48, 310)
body(s, "1–2  Unfavourable\n3      Sometimes\n4–5  Favourable", 48, 340, 350, 16, 84)
s.label("READING THE EVIDENCE", 468, 310)
body(s, "9,810 valid item answers; 84.9% are favourable.\nNo eligible-workforce denominator is available.\nComment coding is interpretive; human validation remains.", 468, 340, 435, 13, 94, MUTED)
s.rule_note("All findings describe the supplied response pool. No response-rate or workforce-wide prevalence claim is made.")

# 04 — Strengths
s = Slide("Strengths to preserve", "Pride and helpful colleagues\nare assets to protect", "Improvement should build on what employees already value.",
          "item_evidence_profile.csv (PRI2, PRI1, CAM1); employee_voice_topic_summary.csv (preserve topic t).",
          "Three items show a strong foundation: 95.7% understand their contribution to business success, 92.4% are proud to work for Safewater Lines and 91.1% report help within their own team. These are favourable shares of 327 valid answers per item. In the preserve prompt, 119 records mention team or colleague-related strengths. Some identify valued people or relationships rather than describing a specific helpful behaviour, so do not overstate this as 119 accounts of assistance. Keep these strengths as guardrails during the pilot. A higher overall score should not come at the expense of pride or mutual support.")
for y, code, label in [(185, "PRI2", "Understand contribution to business success"), (268, "PRI1", "Proud to work for Safewater Lines"), (351, "CAM1", "Help and support within own team")]:
    body(s, label, 48, y, 550, 15, 30, bold=True)
    s.rect(48, y + 35, 640, 13, LIGHT)
    s.rect(48, y + 35, fav(code) / 100 * 640, 13, DARK)
    s.text(f"{fav(code):.1f}%", 731, y + 6, 175, 49, 32, BLUE, True, "right")
s.rule_note("119 records mention team/colleague strengths in the preserve prompt. Use pride and own-team support as guardrails.")

# 05 — Dimensions
s = Slide("Survey landscape", "Fairness is the weakest survey block", "Favourable item-answer shares show where further diagnosis is useful.",
          "survey_clean.csv; five items per block; 1,635 valid answers per block; equal-weight working means.",
          "Pride has the highest favourable item-answer share and Fairness the lowest. Respect and Camaraderie sit below Credibility and Overall experience. Each block has five complete items and therefore 1,635 valid rating answers. These block labels come from the questionnaire; naming them does not establish that they are statistically distinct constructs. Means assume equal category spacing and equal weights. We use the distributions and individual questions to guide action rather than assuming that a small difference between means is substantively important. These results should not be compared to an external benchmark or official Trust Index without a valid matching basis.")
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
s.rule_note("Overall experience is a separate block. The 25-item culture mean is descriptive, not a validated engagement index.")

# 06 — Paired comparison
s = Slide("Priority 1  /  Cross-team work", "Helpful colleagues do not guarantee\nsmooth cross-team execution", "Compare own-team support and cross-team collaboration in the same response records.",
          "cross_team_deep_dive.csv; cross_team_paired_detail.csv; CAM1 × CAM2; n = 327.",
          "The own-team support item is 91.1% favourable versus 82.3% for cross-team collaboration, a difference of 8.9 percentage points. Reliance on colleagues in other teams is 80.1% favourable. The stronger evidence is the paired table: 45 records rate own-team support at 4–5 and cross-team work at 1–3, while 16 show the reverse. Both are favourable in 253 records, and both are 1–3 in 13. The difference points to a coordination question, not proof that any specific team is failing. The survey cannot identify which department pair, workflow step or process causes delays. Verify one real handover path before selecting the pilot.")
s.label("FAVOURABLE SHARE", 48, 171)
for y, code, label in [(208, "CAM1", "Own-team support"), (272, "CAM2", "Cross-team collaboration"), (336, "CAM4", "Support from other teams")]:
    s.text(label, 48, y, 390, 22, 13)
    s.rect(48, y + 26, 354, 12, LIGHT)
    s.rect(48, y + 26, fav(code) / 100 * 354, 12, DARK)
    s.text(f"{fav(code):.1f}%", 415, y + 15, 78, 33, 19, BLUE, True, "right")
s.line(523, 171, 523, 435)
s.text("45", 560, 169, 340, 65, 47, BLUE, True)
body(s, "Own-team favourable; cross-team 1–3", 560, 234, 340, 14, 42, bold=True)
body(s, "13.8% of all 327 records; 16 show the reverse.", 560, 279, 340, 11.5, 35, MUTED)
table(s, ["Own-team / cross-team", "1–3", "4–5"], [["1–3", "13", "16"], ["4–5", "45", "253"]], x=560, y=330, widths=[204, 68, 68], row_h=34, header_h=29, size=12)
s.rule_note("The 8.9-point difference is descriptive. The next step is to verify handovers, receiving ownership and backup.")

# 07 — Fairness
s = Slide("Priority 2  /  Fairness", "Consistency and explanations\ndeserve a closer look", "Keep Sometimes separate from an unfavourable response.",
          "fairness_item_deep_dive.csv; fairness_response_breadth.csv; item_evidence_profile.csv; n = 327 per item.",
          "Decision consistency, understanding employee decisions and performance-related rewards are the three lowest favourable fairness items. Equal career opportunities and fair workload distribution score higher. Across the five fairness items, 137 records have at least one response at 1–3 and 97 have two or more. This is a breadth measure across items, not the proportion of employees who have been treated unfairly. Sometimes is included, and the items overlap. The appropriate response is to review how criteria are specified, explained and applied, while retaining positive and no-concern experiences. These findings do not establish discrimination or verified misconduct.")
for y, code, label in [(185, "FAI3", "Decision consistency"), (235, "FAI5", "Understanding decisions"), (285, "FAI1", "Rewards / performance"), (335, "FAI2", "Career opportunities"), (385, "FAI4", "Workload distribution")]:
    stack(s, code, label, 48, y, 174, 288)
s.line(641, 171, 641, 434)
s.text("137 / 327", 676, 178, 236, 52, 30, BLUE, True)
body(s, "At least one fairness item rated 1–3", 676, 240, 236, 14, 58)
s.text("97 / 327", 676, 320, 236, 43, 26, BLUE, True)
body(s, "Two or more fairness items rated 1–3", 676, 373, 236, 13, 52)
legend(s, y=445)
s.rule_note("1–3 includes Sometimes. These counts are not a prevalence estimate of unfair treatment.", y=471)

# 08 — Voice
s = Slide("Employee voice", "Employee requests point\nto practical changes", "Prompted, overlapping topics; counts describe requests, not incidents or dissatisfaction rates.",
          "employee_voice_topic_summary.csv; fairness_prompt_topic_detail.csv; assistant_review_status.csv.",
          "Across the six prompts, a record can contribute to multiple request topics but is counted once within each topic. The largest request topics include communication, recognition/feedback and teamwork. These counts help specify what to test; they do not independently validate the rating results or establish severity. Within 308 nonblank fairness-prompt answers, 67 mention career/learning requests, 66 recognition and 64 communication. There are also 73 no-current-concern replies. These figures deliberately retain contrasting experiences. The contextual coding had a documented same-assistant re-review, not independent human validation. All figures could be refined during that validation.")
for i, (code, label) in enumerate([("c", "Communication / explanations"), ("r", "Recognition / feedback"), ("t", "Teamwork / coordination"), ("d", "Career / learning"), ("v", "Voice / follow-through"), ("f", "Fair treatment / consistency")]):
    y = 178 + i * 43
    body(s, label, 48, y, 251, 12.5, 30)
    s.rect(312, y + 5, 224, 12, LIGHT)
    s.rect(312, y + 5, request(code) / 327 * 224, 12, DARK)
    s.text(str(request(code)), 549, y - 1, 52, 27, 15, BLUE, True, "right")
s.line(630, 171, 630, 440)
s.label("WITHIN THE FAIRNESS PROMPT", 663, 174, 249)
body(s, "67  Career / learning requests\n66  Recognition requests\n64  Communication requests", 663, 214, 249, 14, 86, MUTED)
s.text("73", 663, 326, 249, 49, 32, BLUE, True)
body(s, "Replies report no current concern.\nRetain this contrasting evidence.", 663, 382, 249, 13, 57)
s.rule_note("Request counts use all 327 records as the reference pool. Fairness-prompt examples refer to 308 nonblank answers.")

# 09 — Support practices
s = Slide("Supporting practices", "Three practices can make\nthe two priorities workable", "Practical enablers to incorporate in the pilot, rather than three separate change programmes.",
          "item_evidence_profile.csv (RES4, CRE5); employee_voice_topic_summary.csv; final_focus_evidence_and_actions.csv.",
          "Recognition and feedback, role clarity/backup, and visible follow-through are useful supporting practices. Recognition has 72.5% favourable answers and 179 unique records requesting recognition or feedback. The topic is broader than awards: it includes useful performance feedback. Roles/processes and workload/boundaries appear in 91 and 78 records respectively; these topics overlap and do not diagnose burnout. Listening and action has 79.8% favourable answers, with 134 records requesting voice or follow-through. These patterns suggest specific management practices to test alongside the two priorities. They are not proven causal mechanisms or an independent statistical ranking of priorities.")
for x, title, value, detail, action in [
    (48, "Recognition and feedback", f"{fav('RES4'):.1f}%", "Favourable on recognition.\n179 records request recognition / feedback.", "Offer specific feedback; explain how contributions are recognised."),
    (345, "Role clarity and backup", "91 / 78", "Records request roles/process changes / workload-boundary changes.", "Define critical task owners, backup and escalation expectations."),
    (642, "Visible follow-through", f"{fav('CRE5'):.1f}%", "Favourable on listening and action.\n134 records request voice / follow-through.", "Acknowledge concerns, assign an owner and give the next update."),
]:
    s.rect(x, 172, 270, 4, BLUE)
    body(s, title, x, 194, 265, 17, 50, bold=True)
    s.text(value, x, 259, 263, 50, 32, BLUE, True)
    body(s, detail, x, 322, 263, 12.5, 70, MUTED)
    body(s, action, x, 406, 263, 13, 66)

# 10 — Pilot design
s = Slide("Recommended response", "Pilot two changes\nwith clear accountability", "Start with a bounded workflow and agreed pilot roles; verify the operational problem first.",
          "implementation_roadmap_0_90_days.csv (G0, P1-A/B/C, P2-A/B/C); proposed actions, not approved commitments.",
          "For cross-team execution, the proposed accountable owner is the Operations or functional head. First map one real handover path with both sides, then define required information, receiving owner, acknowledgement, escalation and backup. For fairness, the proposed owner is the HR head with business decision owners. Review existing appraisal, progression and reward criteria, make them accessible, give reasons and establish a clarification or review route. All named roles are proposed, not confirmed appointments. Existing tools should be reused where practical; this is not a request to purchase a new platform. Specific facilities, equipment, respectful-treatment or boundary accounts need confidential verification and appropriate routing.")
for x, tag, title, owner, steps, deliverable in [
    (48, "P1", "Cross-team execution", "Operations / functional head", ["Map one handover with both sides.", "Define information, recipient and backup.", "Use acknowledgement and escalation."], "By Day 30: documented handover types and assigned owners."),
    (492, "P2", "Fair people decisions", "HR head + business decision owners", ["Review appraisal, progression and rewards.", "Publish understandable pilot-role criteria.", "Explain decisions and the review route."], "By Day 30: accessible criteria and review route for all pilot roles."),
]:
    s.rect(x, 171, 420, 33, PALE)
    s.text(tag + "  /  " + title, x + 12, 179, 396, 24, 15, BLUE, True)
    s.label("PROPOSED ACCOUNTABLE OWNER", x, 224, 420)
    body(s, owner, x, 252, 412, 14, 38, bold=True)
    for i, step in enumerate(steps):
        s.text(f"{i+1:02d}", x, 306 + i * 36, 30, 23, 11, BLUE, True)
        body(s, step, x + 40, 302 + i * 36, 370, 12.5, 33)
    body(s, deliverable, x, 424, 414, 12, 43, MUTED)
s.rule_note("Specific work-condition or treatment accounts require confidential verification through the relevant existing routes.", y=475)

# 11 — Roadmap
s = Slide("Implementation", "A 90-day pilot turns\nthe findings into a decision", "Day 0 begins at organisational approval, not at the assignment deadline.",
          "implementation_roadmap_0_90_days.csv; roadmap_decision_gates.csv; all standards and owners are proposals.",
          "At Day 0 the organisation decides whether to approve the pilot scope, sponsor, owners and capacity. During the first 14 days, collect the operational baseline, select exact pulse items, confirm eligible populations and agree numerical outcome targets. Days 15–30 make the pilot ready: checklist, owners, criteria and feedback/concern processes. Days 31–60 operate and adapt the pilot through weekly exception reviews, checking for administrative burden and actual employee usefulness. Days 61–90 repeat comparable experience questions, compare operational measures and decide whether to scale, adapt or stop. Earlier verification of specific accounts should proceed according to urgency and existing routes.")
phases = [
    ("DAYS 0–14", "Verify and baseline", "Choose one workflow.\nReview existing criteria.\nAgree outcome targets.", "HR + functional owners", "Gate: approve baseline"),
    ("DAYS 15–30", "Make the pilot ready", "Assign owners / backup.\nPublish pilot-role criteria.\nStart feedback / action log.", "Pilot managers + HR", "Gate: continue or adapt"),
    ("DAYS 31–60", "Run and improve", "Review delays and rework.\nAudit decision explanations.\nCheck usefulness and burden.", "Workstream owners", "Gate: review progress"),
    ("DAYS 61–90", "Evaluate and decide", "Repeat selected pulse items.\nReview process and resources.\nPreserve pride and support.", "Sponsor + HR + owners", "Gate: scale, adapt or stop"),
]
for i, (time, title, detail, owner, gate) in enumerate(phases):
    x = 48 + i * 222
    s.rect(x, 173, 198, 3, BLUE)
    s.label(time, x, 193, 198)
    body(s, title, x, 231, 197, 17, 51, bold=True)
    body(s, detail, x, 299, 197, 12, 84, MUTED)
    body(s, owner, x, 403, 197, 11, 37, BLUE, True)
    body(s, gate, x, 455, 197, 10, 29, MUTED)

# 12 — Measures
s = Slide("Measures of success", "Measure process quality\nand employee experience", "Separate proposed operating standards from outcome targets that still need a pilot baseline.",
          "roadmap_kpi_dictionary.csv; roadmap_decision_gates.csv; whole-study survey references are not pilot baselines.",
          "Use both operational process measures and repeated experience items. Required-field completeness is proposed at at least 95% by Day 60; workflow-specific timeliness targets need the first 14-day log. For fairness, criteria and review-route access is proposed for 100% of pilot roles by Day 30, alongside documented reasons for reviewed decisions. These standards are design choices, not effects predicted from the survey. Recognition should track offers, completions and voluntary declines in feedback conversations. Normal concerns should have acknowledgement within two business days, and an owner/next-update date within five; this is not a five-day resolution promise. Repeated item outcomes need comparable wording, composition, valid denominators and nonresponse reporting. Preserve PRI1 and CAM1 as guardrails. Before-and-after change alone is not proof of causality.")
table(s, ["WORKSTREAM", "PROPOSED PROCESS CHECK", "EXPERIENCE CHECK / CURRENT REFERENCE"], [
    ["Cross-team work", "≥95% handover completeness by Day 60; timeliness target after baseline.", "Repeat CAM2 / CAM4.\nCurrent: 82.3% / 80.1% favourable."],
    ["People decisions", "100% pilot-role criteria access by Day 30; review reasons and exceptions.", "Repeat FAI1 / FAI3 / FAI5.\nCurrent: 76.1% / 74.6% / 75.5%."],
    ["Recognition", "Offer each eligible pilot employee feedback each 30-day cycle.", "Repeat RES4 / CAM5.\nCurrent: 72.5% / 72.8%."],
    ["Listening / action", "Normal concerns: acknowledge ≤2 business days; owner / update date ≤5.", "Repeat CRE5; ask if useful change was seen. Current: 79.8%."],
], widths=[146, 355, 363], row_h=62, header_h=33, size=11.5)
s.rule_note("Set numerical outcome targets by Day 14. Review at Days 60/90; retain PRI1 pride and CAM1 support as guardrails.", y=475)

# 13 — Close / decision
s = Slide("Leadership decision", "Approve a focused pilot,\nthen scale on evidence", "A practical next step grounded in the current response pool.",
          "FINAL_ANALYSIS_SYNTHESIS.md; implementation_roadmap_0_90_days.csv; roadmap_decision_gates.csv.",
          "Close with three specific decisions. Approve the scope of one cross-functional workflow and a defined set of pilot roles; name the sponsor and accountable functional/HR owners; and authorise the 14-day baseline effort with a Day-90 review. Numerical outcome targets, capacity and owners still need organisational approval. Protect pride and helpful relationships while improving how work crosses teams and how people decisions are explained and applied. The dashboard supports discussion and the appendix contains the measurement and method detail. Invite discussion on which workflow is most valuable to verify first, rather than asking leadership to endorse a broad unbounded programme.")
for y, n, title, detail in [
    (174, "01", "Confirm a bounded scope", "One cross-functional workflow and clearly defined pilot roles."),
    (265, "02", "Name owners and provide capacity", "Executive sponsor, HR lead and accountable functional owner."),
    (356, "03", "Approve the baseline and review gates", "14 days to agree measures and targets; Day 90 to scale, adapt or stop."),
]:
    s.text(n, 48, y, 60, 45, 28, BLUE, True)
    body(s, title, 138, y, 760, 19, 32, bold=True)
    body(s, detail, 138, y + 39, 760, 13.5, 39, MUTED)
s.rule_note("Protect pride and mutual support while making cross-team work and people decisions more dependable.", y=473)

# 14 — Methodology appendix
s = Slide("Reference  /  Methodology", "Methods were selected for the decision", "The notebook contains the full research trail and methodology reference.",
          "ANALYSIS_FROM_DATA_TO_ACTION.md §12; notebooks/00_data_understanding_eda.ipynb, final methodology cell.",
          "Primary evidence is counts, distributions, favourable shares and paired comparisons. Working means assume equal category spacing and weights. The notebook also uses alpha as an internal-coherence diagnostic, exploratory Spearman correlations and selected Kruskal–Wallis comparisons with Benjamini–Yekutieli adjustment. None establishes validity or causation. HR-choice asymptotic p-values were withheld because of sparse cells. Comment analysis uses 15 explicit overlapping topics plus stance/status; it is codebook-based thematic content analysis, not independently validated reflexive thematic analysis. Exact bigrams/trigrams help navigate recurring phrases but do not replace contextual interpretation. The VOSviewer-inspired map describes same-answer co-mentions, with prompt and parameter sensitivity. The specific equal-weight fuzzy construction adds no information over the ordinary mean, so it is not a decision model in the final story.", appendix=True)
table(s, ["METHOD", "PURPOSE / USE", "BOUNDARY"], [
    ["Audit + distributions", "Check source, wording, valid n and category shares.", "Supplied records; population coverage unknown."],
    ["Means + diagnostics", "Summarise blocks; alpha / rank associations explored.", "Descriptive scores; coherence ≠ validity or cause."],
    ["Paired comparisons", "Compare own-team and cross-team in each record.", "Shows a pattern, not which workflow causes it."],
    ["Contextual topic coding", "15 overlapping topics with separate stance/status.", "Assistant interpretation; human validation pending."],
    ["Bigrams / trigrams", "Find recurring phrases and navigate comments.", "No automated sentiment or theme-validity claim."],
    ["Topic network", "Explore same-answer topic co-mentions.", "Prompt-sensitive; not a causal or employee network."],
    ["Sensitivity + restraint", "Check exclusions; avoid redundant fuzzy scoring.", "Exclusion is not bias correction; no attrition model."],
], widths=[180, 331, 353], row_h=39, header_h=30, size=10.4)

# 15 — Confidence / review
s = Slide("Reference  /  Confidence", "Keep the results and\ntheir limits together", "Sensitivity checks inform interpretation; they do not turn a descriptive survey into a causal study.",
          "item_evidence_profile.csv; coding_review_before_after.csv; assistant_review_status.csv; analysis guide §4–8.",
          "Primary results retain all supplied records. Excluding identical-category respondents changes the sample; it is not a correction to a known unbiased truth. The selected item shares fall after exclusion, while Pride remains the highest block and Fairness the lowest. The count of 45 paired discordant records cannot include straight-liners by definition, so its unchanged count is not independent robustness evidence. The qualitative re-review covered 568 unique comments, including all 104 original flags, and changed 53 assignment/status decisions. There are 75 remaining cases needing context confirmation, not simply unread comments. No independent human coder or inter-rater reliability is claimed. Selected revised request counts are career/learning 136, fairness 114 and support/respect 139.", appendix=True)
s.label("RATING SENSITIVITY", 48, 171)
table(s, ["ITEM", "ALL RECORDS", "EXCLUDING IDENTICAL RATINGS"], [
    ["Recognition / RES4", f"{fav('RES4'):.1f}%", f"{item.loc['RES4', 'fav_without_straightliners_pct']:.1f}%"],
    ["Consistency / FAI3", f"{fav('FAI3'):.1f}%", f"{item.loc['FAI3', 'fav_without_straightliners_pct']:.1f}%"],
    ["Cross-team / CAM2", f"{fav('CAM2'):.1f}%", f"{item.loc['CAM2', 'fav_without_straightliners_pct']:.1f}%"],
    ["Pride / PRI1", f"{fav('PRI1'):.1f}%", f"{item.loc['PRI1', 'fav_without_straightliners_pct']:.1f}%"],
], x=48, y=204, widths=[182, 99, 189], row_h=43, header_h=40, size=11)
s.label("COMMENT REVIEW STATUS", 558, 171, 354)
for y, value, label in [(209, "568", "Unique comments reread"), (271, "53", "Coding / status decisions revised"), (333, "75", "Cases still need context confirmation")]:
    s.text(value, 558, y, 83, 42, 28, BLUE, True)
    body(s, label, 657, y + 4, 255, 12.5, 41, MUTED)
body(s, "Independent human validation remains outstanding.", 558, 407, 354, 13, 49, bold=True)
s.rule_note("Selected favourable shares: n = 327 primary; n = " + str(int(df[rating_cols].nunique(axis=1).gt(1).sum())) + " after exclusion. Primary reporting retains all records.", y=475)

# 16 — Segment follow-up
s = Slide("Reference  /  Follow-up", "Use group patterns to guide listening,\nnot to assign blame", "Selected descriptive examples; group composition and response selection may influence differences.",
          "focused_group_profile.csv; cross_team_fairness_overlap.csv; whole-study n = 327; selected groups n ≥ 10.",
          "The 3–5-year tenure group and Customer Service are examples for further listening, not a ranking of problem groups. Eleven of 53 responses in the 3–5-year group show favourable own-team support and a 1–3 cross-team rating; 27 have at least one fairness item at 1–3. Corresponding Customer Service counts are 10 of 51 and 29 of 51. Departments and tenure groups overlap, so they are not independent comparisons. Composition, selection, role mix and working context could explain patterns. The heterogeneous Other grouping is unsuitable for a simple team-level diagnosis. Cross-team and fairness patterns overlap for 47 records but 90 records have a fairness item at 1–3 despite favourable cross-team collaboration, which is why the two priorities should not be collapsed into one explanation.", appendix=True)
table(s, ["SCOPE", "VALID n", "OWN-TEAM 4–5 / CROSS-TEAM 1–3", "≥1 FAIRNESS ITEM AT 1–3"], [
    ["Full study", "327", "45 / 327  ·  13.8%", "137 / 327  ·  41.9%"],
    ["Tenure: 3–5 years", "53", "11 / 53  ·  20.8%", "27 / 53  ·  50.9%"],
    ["Customer Service", "51", "10 / 51  ·  19.6%", "29 / 51  ·  56.9%"],
], widths=[192, 76, 306, 290], row_h=59, header_h=43, size=12)
body(s, "Follow up with contrasting experiences and verified work examples before choosing the pilot workflow.", 48, 421, 864, 16, 50, bold=True)
s.rule_note("1–3 includes Sometimes. These examples do not establish department effects, causes or fairness-incident prevalence.", y=475)

# 17 — Network, interpreted conservatively
s = Slide("Reference  /  Topic connections", "The topic map helps organise discussion", "VOSviewer-inspired exploration of same-answer co-mentions; not a causal map or a native VOSviewer run.",
          "topic_network_edges.csv; topic_network_parameter_sensitivity.csv; reports/network/topic_network_data.json.",
          "The full primary network includes 1,230 topic-coded suggestion/mixed answers from 305 response records, 13 displayed topics and 34 links supported by at least ten answers. This slide shows a selected five-topic excerpt using original node support and same-answer counts; positions are schematic, not analytical distances. Communication and teamwork co-occur in 98 answers from 93 records; 85 of those answers arise from the teamwork prompt. Fairness and career co-occur in 46 answers from 43 records; 41 come from the fairness prompt. Prompt dependence and parameter sensitivity limit any claim that the graph independently validates a mechanism. Node sizes represent unique-record support within the primary network context, line widths represent answer co-mentions. The offline interactive map provides question exclusion and further context.", appendix=True)

network = json.loads((ROOT / "reports/network/topic_network_data.json").read_text())
edges = pd.read_csv(ROOT / "reports/tables/topic_network_edges.csv")
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


def hex_rgb(value):
    return RGBColor.from_string(value)


def render_pptx():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Pt(W), Pt(H)
    props = prs.core_properties
    props.title = "Safewater Lines | People Experience"
    props.subject = "Survey findings and proposed 90-day organisational pathway"
    props.author = "Safewater Lines People Analytics Project"
    props.keywords = "employee survey, cross-team work, fairness, people analytics"
    for scene in slides:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = hex_rgb(WHITE)
        for obj in scene.objects:
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
        slide.notes_slide.notes_text_frame.text = scene.notes + "\n\nEVIDENCE\n" + scene.source + "\nFull methodology: reports/ANALYSIS_FROM_DATA_TO_ACTION.md."
    pptx_path = OUT / "Safewater_Lines_People_Experience.pptx"
    prs.save(pptx_path)
    return pptx_path


def render_pdf():
    path = OUT / "Safewater_Lines_People_Experience.pdf"
    pdf = canvas.Canvas(str(path), pagesize=(W, H))
    pdf.setTitle("Safewater Lines | People Experience")
    pdf.setAuthor("Safewater Lines People Analytics Project")
    def color(hex_value):
        return tuple(int(hex_value[i:i+2], 16) / 255 for i in (0, 2, 4))
    for scene in slides:
        for obj in scene.objects:
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


def validate(pptx_path, pdf_path):
    from pptx import Presentation as ReadPresentation
    import pymupdf
    reopened = ReadPresentation(pptx_path)
    assert len(reopened.slides) == len(slides) == 17
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
    assert len(pdf) == 17
    thumbs = []
    for i, page in enumerate(pdf):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False)
        target = PREVIEW / f"slide-{i+1:02d}.png"
        pix.save(target)
        image = Image.open(target).convert("RGB")
        image.thumbnail((480, 270))
        thumbs.append(image)
    sheet = Image.new("RGB", (480 * 3, 300 * 6), "#E8ECEF")
    draw = ImageDraw.Draw(sheet)
    for i, thumb in enumerate(thumbs):
        x, y = (i % 3) * 480, (i // 3) * 300
        sheet.paste(thumb, (x, y))
        draw.text((x + 12, y + 277), f"{i+1:02d}  {slides[i].section}", fill="#365F7B")
    sheet.save(PREVIEW / "contact-sheet.png")
    checks = {"slides": 17, "main_slides": 13, "appendix_slides": 4,
              "pptx_reopened": True, "all_slides_have_speaker_notes": True,
              "all_shapes_within_slide": True, "text_boxes_fit_using_Arial_metrics": True,
              "pdf_pages": len(pdf), "preview_engine": "PDF companion rendered by PyMuPDF; not a native PowerPoint render",
              "source_assertions": "327 records; 9810 answers; 45 paired discordant; 137 fairness breadth; 179 recognition requests"}
    (HERE / "qa_results.json").write_text(json.dumps(checks, indent=2) + "\n")


def write_notes():
    content = ["# Presentation storyline and speaker guide", "", "13 main slides, followed by four reference slides. Allow roughly 12–15 minutes for the main story; use the appendix for questions. Timing is a suggested rehearsal plan, not an assignment requirement.", "", "All suggested owners, standards and pilot actions require organisational decisions. No team member names were supplied.", ""]
    for s in slides:
        content.extend([f"## {s.number:02d} · {s.title.replace(chr(10), ' ')}", "", s.notes, "", "**Evidence:** " + s.source, ""])
    (HERE / "SPEAKER_GUIDE.md").write_text("\n".join(content))
    (HERE / "slide_content.json").write_text(json.dumps([{"slide": s.number, "section": s.section, "title": s.title, "source": s.source, "notes": s.notes, "objects": s.objects} for s in slides], ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    pptx_path = render_pptx()
    pdf_path = render_pdf()
    validate(pptx_path, pdf_path)
    write_notes()
    print(f"Created {pptx_path}\nCreated {pdf_path}\n17 slides, notes, companion previews and layout checks complete.")
