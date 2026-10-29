"""Create the 20-minute pitch deck in plain English.

Reuses the layout engine, data checks and renderers of build_presentation.py,
so both decks read the same aggregate evidence and pass the same fit checks.
"""
from __future__ import annotations

import build_presentation as bp
from build_presentation import BLUE, DARK, INK, LIGHT, MID, MUTED, PALE, WHITE, body, fav, hbar, mix, quote

bp.slides.clear()          # drop the executive deck built on import; keep its data and helpers
nva, hot, hr, one = bp.nva, bp.hot, bp.hr, bp.one
TIMES = []
SCALE = 1.18               # body text is larger than in the executive deck, for reading on a projector


class Slide(bp.Slide):
    """Executive-deck slide with a larger title and body text; text boxes grow to fit the larger type."""
    title_size, subtitle_y = 32, 135

    def text(self, value, x, y, w, h, size=14, color=INK, bold=False, align="left", leading=1.2):
        if size <= 17.5:
            size = round(size * SCALE, 1)
        h = max(h, len(bp.wrap(value, w, size, bold)) * size * leading)
        super().text(value, x, y, w, h, size, color, bold, align, leading)


def overlaps(slides):
    """Pairs of text boxes on the same slide whose rendered lines intersect."""
    found = []
    for sc in slides:
        boxes = []
        for o in sc.objects:
            if o["kind"] != "text" or not o["text"].strip():
                continue
            font = "Arial-Bold" if o["bold"] else "Arial"
            tw = max(bp.pdfmetrics.stringWidth(l, font, o["size"]) for l in o["lines"])
            x0 = o["x"] + (o["w"] - tw if o["align"] == "right" else (o["w"] - tw) / 2 if o["align"] == "center" else 0)
            boxes.append((x0, o["y"], x0 + tw, o["y"] + len(o["lines"]) * o["size"] * o["leading"], o["text"][:40]))
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                if a[0] < b[2] - 1 and b[0] < a[2] - 1 and a[1] < b[3] - 1 and b[1] < a[3] - 1:
                    found.append((sc.number, a[4], b[4]))
    return found


def timed(slide, minutes):
    TIMES.append(minutes)
    start = sum(TIMES[:-1])
    slide.notes = f"[{int(start)}:{round(start % 1 * 60):02d} – {int(start + minutes)}:{round((start + minutes) % 1 * 60):02d}] " + slide.notes


def pct(x):
    return f"{x:.0f}%"


def takeaway(s, text, y=410):
    s.rect(48, y, 864, 40, PALE)
    s.rect(48, y, 4, 40, BLUE)
    s.text(text, 66, y + 12, 836, 18, 14, INK, True)


# 01 — Title
s = Slide("Pitch", "What our people are telling us", "", "Your Voice survey (responses to 21 October); analysis 30 October 2026.",
          "Good morning. We analysed the Your Voice survey: 327 people, 30 questions and almost 1,900 written comments. In the next 20 minutes we will tell you what employees value, what they want fixed first, and a simple 90-day plan to start.", cover=True)
s.text("SAFEWATER LINES", 48, 40, 700, 20, 12, BLUE, True)
s.text("YOUR VOICE SURVEY  /  RESULTS AND A 90-DAY PLAN", 48, 82, 800, 20, 10, MUTED)
s.rect(48, 135, 52, 4, BLUE)
s.text("What our people\nare telling us", 48, 163, 850, 116, 44, INK, True, leading=1.1)
s.text("What employees value, what they want fixed first,\nand how we can start in 90 days.", 48, 290, 850, 58, 19, MUTED, leading=1.3)
s.text("327 people  ·  30 questions  ·  1,892 written comments", 48, 395, 850, 25, 15, INK)
s.text("30 OCTOBER 2026  /  TISS", 48, 454, 850, 18, 10, BLUE, True)
timed(s, .5)

# 02 — Short version
s = Slide("The short version", "Three things to remember", "If you remember nothing else from today, remember these.",
          "item_evidence_profile.csv; hr_priority_counts.csv; priority_triangulation.csv.",
          "Here is the whole story in one slide. One: people are proud of this company and they help each other. That is a real strength. Two: they want people decisions, like promotions, pay rises and recognition, to be fair and clear. These are the lowest scores in the survey. Three: they want leaders to listen and then act. It was the number one thing people asked HR to do better. Our plan is one 90-day pilot, starting in Customer Service.")
for i, (head, detail) in enumerate([
    ("People are proud of Safewater Lines.", f"{pct(fav('PRI1'))} are proud to work here. {pct(fav('CAM1'))} say their team helps each other."),
    ("They want people decisions to be fair and clear.", "Promotions, rewards and recognition get the lowest scores of all 30 questions."),
    ("They want leaders to listen, and then act.", "It was the No. 1 thing people asked HR to do better."),
]):
    y = 172 + i * 88
    s.text(str(i + 1), 48, y - 2, 40, 40, 32, BLUE, True)
    body(s, head, 100, y, 812, 21, 28, bold=True)
    body(s, detail, 100, y + 34, 812, 15, 22, MUTED)
takeaway(s, "Our plan: one 90-day pilot with three parts, starting in Customer Service.", y=420)
timed(s, 1)

# 03 — Who answered
s = Slide("Who answered", "Who took part", "Answers came from across India and abroad, in five languages.",
          "survey_clean.csv; workbook language sheets.",
          f"327 people answered. They could reply in English, Hindi, Marathi, Tamil or Malayalam, from 23 locations, and they wrote almost 1,900 comments. Mumbai is the biggest group, about 40% of answers, and 38% have been here less than 3 years. One limit: we were not given the total number of employees, so we cannot say what share of staff took part.")
for x, value, label in [(48, "327", "people answered"), (270, "5", "languages"), (492, "23", "locations"), (714, "1,892", "written comments")]:
    s.text(value, x, 175, 200, 52, 42, BLUE, True)
    body(s, label, x, 232, 200, 15, 22, MUTED)
s.line(48, 290, 912, 290)
s.label("Biggest groups", 48, 310)
loc = df_loc = bp.df["location"].value_counts(normalize=True) * 100
ten = bp.df["tenure"].value_counts(normalize=True) * 100
gen = bp.df["gender"].value_counts(normalize=True) * 100
body(s, f"Mumbai {pct(loc['Mumbai'])} of answers   ·   Less than 3 years' service {pct(ten['0 - 3'])}   ·   Men {pct(gen['Male'])}, women {pct(gen['Female'])}", 48, 340, 864, 16, 24)
s.rule_note("We were not given the total headcount, so we cannot say what share of employees took part.")
timed(s, 1)

# 04 — How to read the numbers
s = Slide("How to read the numbers", "How to read the numbers", "Every question had the same five answers.",
          "Survey answer scale; favourable = 4–5.",
          "Every question had five possible answers, from Almost never to Almost always. When we say a number like 80% positive, it means 8 out of 10 people answered Usually or Almost always. Sometimes is the middle answer, so we do not count it as positive. That is all you need to read the rest of the slides.")
labels = ["Almost never", "Rarely", "Sometimes", "Usually", "Almost always"]
for i, lab in enumerate(labels):
    x = 48 + i * 176
    positive = i >= 3
    s.rect(x, 186, 160, 72, BLUE if positive else (PALE if i == 2 else LIGHT))
    s.text(str(i + 1), x, 196, 160, 28, 22, WHITE if positive else INK, True, "center")
    s.text(lab, x, 228, 160, 18, 13, WHITE if positive else MUTED, False, "center")
s.line(48 + 3 * 176, 272, 48 + 4 * 176 + 160, 272, BLUE, 2)
s.text("= positive", 48 + 3 * 176, 280, 336, 20, 14, BLUE, True, "center")
body(s, "“80% positive” means 8 in 10 people answered Usually or Almost always.", 48, 330, 864, 18, 26, bold=True)
body(s, "“Sometimes” is the middle answer. We do not count it as positive.", 48, 368, 864, 15, 22, MUTED)
timed(s, .5)

# 05 — Good news
s = Slide("The good news", "The good news: people are proud\nand they help each other", "Share of people answering Usually or Almost always.",
          "item_evidence_profile.csv (PRI2, PRI1, CAM1, CAM3).",
          "Let's start with the good news, because it is big. Almost everyone understands how their work helps the business. 92% are proud to work here. 91% say people in their team help each other, and 90% feel they belong. When we asked what people never want to lose, 119 people named their team or colleagues. Whatever we change, we must protect this.")
for i, (code, label) in enumerate([("PRI2", "I know how my work helps the business"), ("PRI1", "I am proud to work here"),
                                   ("CAM1", "People in my team help each other"), ("CAM3", "I feel I belong here")]):
    y = 176 + i * 68
    body(s, label, 48, y, 600, 16, 22, bold=True)
    s.rect(48, y + 30, 640, 13, LIGHT)
    s.rect(48, y + 30, fav(code) / 100 * 640, 13, DARK)
    s.text(pct(fav(code)), 731, y + 4, 175, 40, 28, BLUE, True, "right")
s.rule_note("These are the strengths to protect while we fix the gaps.")
timed(s, 1)

# 06 — Warning
named, anonymous = nva.loc["Named", "stay_3_5_yrs_fav"], nva.loc["Anonymous", "stay_3_5_yrs_fav"]
s = Slide("One warning", "One warning: answers with a name\nlook more positive", "The survey asked for an optional name. Most people gave it.",
          "named_vs_anonymous.csv; notebook Step 7.4.",
          f"One important warning. The survey asked people for their name, and 69% gave it. People who stayed anonymous were clearly less positive. For example, {pct(named)} of named people plan to stay 3 to 5 years, but only {pct(anonymous)} of anonymous people. People may be more careful when their name is attached. So the real picture is probably a little less rosy than the headline numbers. Our simple advice: do not ask for names next time.")
s.label("Plan to stay for the next 3–5 years", 48, 171, 440)
s.text(pct(named), 48, 196, 200, 60, 50, BLUE, True)
body(s, "People who gave their name (227)", 48, 258, 200, 13, 34, MUTED)
s.text(pct(anonymous), 270, 196, 200, 60, 50, DARK, True)
body(s, f"People who stayed anonymous ({int(nva.loc['Anonymous', 'n'])})", 270, 258, 200, 13, 34, MUTED)
s.line(520, 171, 520, 400)
for i, line in enumerate(["69% of people typed their name on the survey.",
                          "Anonymous people were less positive on every key question.",
                          "So the true picture is probably a little less rosy."]):
    body(s, line, 552, 180 + i * 64, 360, 16, 44, INK if i < 2 else BLUE, i == 2)
takeaway(s, "Simple fix: don’t ask for names in the next survey.", y=410)
timed(s, 1.5)

# 07 — Lowest five
s = Slide("Where it hurts", "Where it hurts: the five lowest scores", "Share of people answering Usually or Almost always. All five are about fairness and recognition.",
          "item_evidence_profile.csv (RES4, CAM5, FAI3, FAI5, FAI1).",
          "Now the gaps. These are the five lowest scores out of 30 questions. Look at what they have in common: recognition, consistent decisions, understanding how decisions are made, and fair rewards. All of them are about how people decisions are made and explained. They are about 10 points below the average of all questions.")
avg = float(bp.df[bp.rating_cols].ge(4).to_numpy().mean() * 100)
bx, bw = 440, 380
for i, (code, label) in enumerate([("RES4", "My efforts are recognised"), ("CAM5", "We celebrate each other’s success"),
                                   ("FAI3", "People decisions are consistent"), ("FAI5", "I understand how people decisions are made"),
                                   ("FAI1", "Rewards are fair and based on performance")]):
    y = 190 + i * 48
    body(s, label, 48, y, 380, 15, 22)
    s.rect(bx, y + 4, bw, 14, LIGHT)
    s.rect(bx, y + 4, fav(code) / 100 * bw, 14, BLUE)
    s.text(pct(fav(code)), bx + bw + 14, y, 60, 22, 16, BLUE, True, "right")
s.line(bx + avg / 100 * bw, 182, bx + avg / 100 * bw, 428, INK, 1.2)
s.text(f"Average of all 30 questions: {pct(avg)}", bx + avg / 100 * bw - 300, 165, 300, 14, 11, INK, True, "right")
s.rule_note("All five lowest scores are about how people decisions are made, explained and recognised.")
timed(s, 1)

# 08 — Four tests
s = Slide("How we chose", "How we decided what to fix first", "We listened in four different ways. A real priority should show up in all of them.",
          "Notebook Step 7.3; pass marks fixed before reading the result.",
          "Low scores alone are not enough to choose priorities, so we checked every theme in four ways. One: is the score low? Two: does it move together with people wanting to stay and recommend the company? Three: did people pick it when asked what HR should do better? Four: did people raise it on their own when we asked for one change? We set the pass marks before looking at the results.")
for i, (title, q) in enumerate([("Low score", "Which questions get the lowest scores?"),
                                ("Linked to staying", "Which questions move together with wanting to stay and recommend?"),
                                ("HR wish list", "What one thing did people ask HR to do better?"),
                                ("In their own words", "What did people raise when asked for “one change”?")]):
    x = 48 + i * 222
    s.rect(x, 174, 198, 3, BLUE)
    s.text(str(i + 1), x, 190, 60, 36, 30, BLUE, True)
    body(s, title, x, 236, 198, 17, 24, bold=True)
    body(s, q, x, 268, 194, 13.5, 70, MUTED)
takeaway(s, "A real priority should pass all four. We set the pass marks before looking at the results.", y=410)
timed(s, 1.5)

# 09 — Results
s = Slide("The result", "Two themes pass all four tests", "Filled circle = strong; light = medium; empty = weak; dash = not asked.",
          "priority_triangulation.csv; notebook Step 7.3.",
          "Here is the result. Only two themes are strong on all four tests: fair people decisions with career growth, and leaders who listen and act. Those are our two priorities. Recognition scores lowest and people write about it a lot, so we put it inside priority one. Teamwork across teams is real but smaller, so it gets a targeted fix. Pay and facilities matter to people but there was no survey question on them, so we send them to the yearly review.")
rows = [("Fair, explainable people decisions & growth", "Fair decisions & career growth", "Priority 1"),
        ("Leaders listen and visibly act", "Leaders listen and act", "Priority 2"),
        ("Recognition of contributions", "Recognition", "Part of Priority 1"),
        ("Cross-team collaboration", "Teamwork across teams", "Targeted fix"),
        ("Pay, benefits & facilities", "Pay, benefits & facilities", "Yearly review")]
widths = [250, 120, 120, 120, 120, 134]
heads = ["THEME", "LOW SCORE", "LINKED TO STAY", "HR WISH LIST", "OWN WORDS", "OUR DECISION"]
s.rect(48, 171, 864, 30, PALE)
pos = 48
for h, w in zip(heads, widths):
    s.text(h, pos + 9, 180, w - 14, 14, 9.5, BLUE, True)
    pos += w
for k, (key, label, verdict) in enumerate(rows):
    y = 201 + k * 44
    top = k < 2
    if top: s.rect(48, y, 864, 44, "F7F9FA")
    s.text(label, 57, y + 14, 236, 18, 13.5, INK, top)
    r = bp.tri.loc[key]
    pos = 48 + 250
    for g in [r["score"], r["outcome_link"], r["hr_choice"], r["one_change"]]:
        if g == "Strong": s.circle(pos + 50, y + 15, 15, BLUE)
        elif g == "Medium": s.circle(pos + 50, y + 15, 15, MID)
        elif g == "Weak": s.circle(pos + 50, y + 15, 15, WHITE, MID)
        else: s.text("—", pos + 48, y + 13, 30, 18, 14, MUTED)
        pos += 120
    s.text(verdict, pos + 9, y + 14, 126, 18, 13, BLUE if top else MUTED, True)
    s.line(48, y + 44, 912, y + 44, bp.LINE, .6)
s.rule_note("Only the first two themes are strong on all four tests.")
timed(s, 1)

# 10 — Priority 1
s = Slide("Priority 1", "Priority 1: fair decisions\nthat people understand", "Promotions, pay rises, rewards and recognition.",
          "item_evidence_profile.csv; driver_model_summary.csv; hr_priority_counts.csv; quote verbatim, de-identified.",
          f"Priority one is fair decisions that people understand. Only {pct(fav('FAI3'))} say people decisions are made consistently. Of the areas leaders can change, fairness is the one most linked to people wanting to stay and recommend the company. And 51 people said HR's main job should be helping careers grow. In one employee's words: inconsistent performance evaluations and opaque promotion criteria. What it means in practice: clear rules for promotion, pay and rewards, and a reason given for every decision.")
for i, (big, text) in enumerate([(pct(fav("FAI3")), "say people decisions are made consistently, one of the lowest scores"),
                                  ("No. 1", "Of the areas leaders can change, fairness is most linked to wanting to stay"),
                                  ("51", "people said HR’s main job should be helping careers grow")]):
    y = 172 + i * 76
    s.text(big, 48, y, 150, 44, 34, BLUE, True)
    body(s, text, 210, y + 6, 340, 15, 40)
s.line(586, 172, 586, 390)
quote(s, "“Inconsistent performance evaluations and opaque promotion criteria.”", 614, 180, 298, 90, 17)
body(s, "An employee, answering the fairness question", 628, 276, 284, 11.5, 16, MUTED)
takeaway(s, "In practice: clear rules for promotion, pay and rewards, and a reason for every decision.", y=410)
timed(s, 1.5)

# 11 — Priority 2
s = Slide("Priority 2", "Priority 2: leaders who listen,\nand then act", "“If HR could do one thing better…”: everyone picked one answer.",
          "hr_priority_counts.csv; item_evidence_profile.csv (CRE5); quote verbatim, de-identified.",
          f"Priority two is leaders who listen and then act. We asked everyone to pick the one thing HR should do better. The top answer, by a clear margin, was listening to employees and their concerns: 67 people. Today only {pct(fav('CRE5'))} say leaders act on feedback, and among the actionable questions it is the one most linked to people wanting to stay. People are not asking for more announcements. They want proof that when they raise something, something happens.")
short = {"Listening to employees and their concerns": "Listen to our concerns", "Help employees progress in their careers": "Help careers grow",
         "Improve employee benefits and facilities": "Better benefits & facilities", "Help resolve employee problems": "Solve our problems",
         "Recognising and appreciating good work": "Recognise good work", "Supporting employees when they need help": "Support us when needed",
         "Making rules and processes simple": "Simpler rules", "Being available and easy to approach": "Be easy to approach",
         "Employee activities and engagement": "More activities", "Keeping employees informed": "Keep us informed"}
for i, (opt, r) in enumerate(hr.iterrows()):
    hbar(s, short[opt], r["respondents"], hr["respondents"].max(), 48, 176 + i * 23, 190, 230,
         opt in ("Listening to employees and their concerns", "Keeping employees informed"), size=12.5)
s.line(560, 172, 560, 400)
s.text(pct(fav("CRE5")), 588, 172, 324, 44, 34, BLUE, True)
body(s, "say leaders act on feedback today", 588, 218, 324, 15, 22)
quote(s, "“Employees’ problems and suggestions should be heard and appropriate action taken promptly.”", 588, 262, 324, 90, 15)
takeaway(s, "In practice: every concern gets an owner, a date and an answer.", y=420)
timed(s, 1.5)

# 12 — Where to start
s = Slide("Where to start", "Where to start: Customer Service", "% positive by group. Darker = lower. Groups with at least 10 people.",
          "group_hotspots.csv; notebook Step 7.5.",
          f"Where should we start? This table shows the share of positive answers by group, and darker means lower. Customer Service is the lowest group on almost everything: only {pct(hot.loc['Customer Service', 'Recognition'])} feel recognised, and {pct(hot.loc['Customer Service', 'Stay 3–5 yrs'])} plan to stay. People with 3 to 5 years' service also dip. Women answer less positively than men on fairness and recognition. This is not about blaming a team. It tells us where to listen first and where a pilot can make the biggest difference.")
cols = ["Fair decisions", "Listen & act", "Recognition", "Stay 3–5 yrs"]
names = ["Fair decisions", "Leaders act", "Recognition", "Plan to stay"]
groups = [("All respondents", "Everyone"), ("Customer Service", "Customer Service"), ("Sales", "Sales"), ("Documentation", "Documentation"),
          ("Finance & Accounts", "Finance & Accounts"), ("Operations", "Operations"), ("3 - 5", "3–5 years’ service")]
gx, lw, cw, rh = 48, 260, 150, 28
s.rect(gx, 171, lw + cw * 4, 28, PALE)
for j, n in enumerate(names):
    s.text(n.upper(), gx + lw + j * cw, 180, cw, 13, 10, BLUE, True, "center")
for i, (key, lab) in enumerate(groups):
    y = 203 + i * rh + (5 if i else 0)
    s.text(f"{lab} ({int(hot.loc[key, 'n'])})", gx + 9, y + 6, lw - 18, 18, 13.5, INK, key in ("All respondents", "Customer Service"))
    for j, c in enumerate(cols):
        v = float(hot.loc[key, c]); t = min(max((95 - v) / 35, 0), 1)
        s.rect(gx + lw + j * cw + 1, y, cw - 2, rh - 2, mix("EEF2F5", BLUE, t))
        s.text(pct(v), gx + lw + j * cw, y + 6, cw, 18, 13.5, WHITE if t > .55 else INK, key == "Customer Service", "center")
gap = [hot.loc["Male", m] - hot.loc["Female", m] for m in ["Fair decisions", "Recognition"]]
s.rule_note(f"Women answer less positively than men on fair decisions and recognition ({min(gap):.0f}–{max(gap):.0f} points lower).")
timed(s, 1)

# 13 — Handovers
s = Slide("A smaller fix", "A smaller fix: handovers between teams", "People help their own team. Work between teams is harder.",
          "cross_team_paired_detail.csv; item_evidence_profile.csv (CAM1, CAM2).",
          f"There is one smaller issue. People rate their own team very highly, 91%, but teams working together across the company lower, 82%. 45 people rate their own team well but other teams poorly. It is real, but smaller than the two priorities, and people rarely raised it on their own. So we suggest a targeted fix: take one handover in Customer Service and agree who sends what, who receives it, and who covers when someone is away.")
for i, (code, label) in enumerate([("CAM1", "My own team helps each other"), ("CAM2", "Teams across the company work well together")]):
    y = 182 + i * 80
    body(s, label, 48, y, 450, 16, 22, bold=True)
    s.rect(48, y + 32, 400, 14, LIGHT)
    s.rect(48, y + 32, fav(code) / 100 * 400, 14, DARK)
    s.text(pct(fav(code)), 458, y + 22, 80, 32, 24, BLUE, True, "right")
s.line(580, 172, 580, 380)
s.text("45", 612, 172, 300, 56, 46, BLUE, True)
body(s, "people rate their own team well but work with other teams poorly", 612, 232, 300, 15, 44)
takeaway(s, "The fix: one Customer Service handover. Who sends what, who receives it, who covers.", y=410)
timed(s, 1)

# 14 — What else
s = Slide("What else we heard", "What else people told us", "“If you could make one change…”: the question that did not suggest any topic.",
          "one_change_topics.csv; hr_priority_counts.csv.",
          "When we asked an open question, if you could make one change, people mostly asked for better communication, recognition, career growth and follow-through. That matches our two priorities. People also care about pay, benefits and facilities: 51 people picked it as HR's main job. A 90-day pilot cannot fix pay, so we suggest sending it to the yearly pay and facilities review, and telling people clearly that this is where it went.")
plain = {"c": "Better communication", "r": "Recognition & feedback", "d": "Career growth & learning", "v": "Act on what we say",
         "w": "Workload & flexibility", "m": "Support & respect"}
top = one.loc[list(plain)].sort_values("records", ascending=False)
for i, (code, r) in enumerate(top.iterrows()):
    hbar(s, plain[code], r["records"], top["records"].max(), 48, 182 + i * 34, 200, 230, code in ("c", "r", "d", "v"), size=14)
s.text("people", 48 + 200 + 238 + 6, 165, 60, 13, 10, MUTED)
s.line(580, 172, 580, 420)
s.label("Also heard", 612, 172, 300)
body(s, "Pay, benefits & facilities", 612, 200, 300, 17, 24, bold=True)
body(s, "51 people picked this as HR’s main job.", 612, 232, 300, 15, 22)
body(s, "Send it to the yearly pay and facilities review, and tell people that is where it went.", 612, 292, 300, 15, 64, BLUE, True)
s.rule_note("A 90-day pilot cannot fix pay. Being open about where it goes still builds trust.")
timed(s, 1)

# 15 — Plan
s = Slide("Our plan", "Our plan: one 90-day pilot,\nthree parts", "Starting in Customer Service. Using the tools and processes we already have.",
          "implementation_roadmap_0_90_days.csv (revised IDs P1, P2, T); proposed owners, not approved commitments.",
          "Here is the plan. One 90-day pilot with three parts, starting in Customer Service. Part one, owned by the HR head: publish clear rules for promotion, pay and rewards, give a reason for every decision, and have managers recognise each person every month. Part two, owned by a leadership sponsor: log every concern with an owner and a date, and send a monthly 'you said, we did' update. Part three, owned by the Operations head: fix one handover between teams. None of this needs a new system.")
for x, tag, owner, steps in [
    (48, "1  /  Fair decisions", "HR head", ["Publish clear rules for promotion, pay and rewards.", "Give a reason for every decision.", "Managers recognise each person monthly."]),
    (344, "2  /  Listen and act", "Leadership sponsor + HR", ["Log every concern with an owner and a date.", "Monthly “you said, we did” update.", "Listening sessions, Customer Service first."]),
    (640, "3  /  Handovers", "Operations head", ["Map one Customer Service handover.", "Agree who sends, receives and covers.", "Flag anything overdue."]),
]:
    s.rect(x, 172, 272, 34, PALE)
    s.text(tag, x + 12, 181, 256, 18, 15, BLUE, True)
    s.text("OWNER", x, 218, 272, 13, 9.5, BLUE, True)
    body(s, owner, x, 234, 272, 15, 20, bold=True)
    for i, step in enumerate(steps):
        s.rect(x, 280 + i * 50, 6, 6, BLUE)
        body(s, step, x + 16, 273 + i * 50, 254, 14, 40)
s.rule_note("No new system is needed. Owners are our proposal and need leadership approval.")
timed(s, 1.5)

# 16 — 90 days
s = Slide("Step by step", "90 days, step by step", "Day 0 is the day leadership approves the pilot.",
          "roadmap_decision_gates.csv (adapted).",
          "Step by step. In the first two weeks we choose the pilot teams, check today's rules and run a short anonymous survey as our starting point. By day 30 the rules are published, owners are named and the concern log is open. From day 31 to 60 we run it, review problems every week and check it is not adding paperwork. In the last month we repeat the short survey and decide together: grow it, change it or stop it.")
for i, (time, title, detail) in enumerate([("Days 0–14", "Get ready", "Pick pilot teams. Check today’s rules. Short anonymous survey."),
                                           ("Days 15–30", "Set up", "Publish rules. Name owners. Open the concern log."),
                                           ("Days 31–60", "Run it", "Monthly recognition and updates. Weekly problem review."),
                                           ("Days 61–90", "Decide", "Repeat the short survey. Grow it, change it or stop it.")]):
    x = 48 + i * 222
    s.rect(x, 174, 198, 3, BLUE)
    s.label(time, x, 192, 198)
    body(s, title, x, 224, 198, 20, 28, bold=True)
    body(s, detail, x, 270, 194, 14.5, 110, MUTED)
s.rule_note("At each step, leadership decides whether to continue.")
timed(s, 1)

# 17 — Measures
s = Slide("How we'll know", "How we will know it worked", "Check that we did the work, and that employees noticed.",
          "roadmap_kpi_dictionary.csv; item_evidence_profile.csv. Targets are suggestions to confirm in the first 14 days.",
          f"How will we know it worked? For each part we check two things: did we do the work, and did employees notice? For example, rules published for every pilot role, and the share who say decisions are consistent going up from {pct(fav('FAI3'))} by about 5 points. We measure with a short anonymous survey so people can be honest. And we watch our strengths, pride and teamwork, to make sure they do not drop.")
bp.table(s, ["PART", "WE CHECK THAT…", "EMPLOYEES SHOULD SAY… (TODAY → GOAL)"], [
    ["Fair decisions", "Rules are published for every pilot role, with a reason for each decision.", f"“Decisions are consistent”: {pct(fav('FAI3'))} → about {pct(fav('FAI3') + 5)}"],
    ["Listen and act", "Every concern is answered within 2 working days and has an owner.", f"“Leaders act on feedback”: {pct(fav('CRE5'))} → about {pct(fav('CRE5') + 5)}"],
    ["Handovers", "At least 95% of handovers are complete by Day 60.", f"“Teams work well together”: {pct(fav('CAM2'))} → higher"],
    ["Protect strengths", "No extra paperwork beyond the agreed logs.", f"Pride {pct(fav('PRI1'))} and own-team help {pct(fav('CAM1'))} do not drop"],
], widths=[150, 360, 354], row_h=56, header_h=30, size=12.5)
s.rule_note("Measured with a short anonymous survey. Goals are suggestions to confirm in the first 14 days.", y=473)
timed(s, 1)

# 18 — Decisions
s = Slide("Your decision", "What we ask you to decide today", "Three decisions to get started.",
          "implementation_roadmap_0_90_days.csv; roadmap_decision_gates.csv.",
          "We are asking for three decisions today. One: approve one 90-day pilot with the three parts. Two: name the owners, the HR head, a leadership sponsor and the Operations head, and give them time for one review a month. Three: run the next survey without names. Thank you. We are happy to take questions.")
for i, (title, detail) in enumerate([("Approve one 90-day pilot", "Fair decisions, listen and act, and one handover, starting in Customer Service."),
                                     ("Name the owners", "HR head, a leadership sponsor and the Operations head, with one review a month."),
                                     ("Run the next survey without names", "A short anonymous survey now, and again at Day 90.")]):
    y = 176 + i * 88
    s.text(f"0{i + 1}", 48, y, 70, 44, 32, BLUE, True)
    body(s, title, 138, y, 760, 21, 30, bold=True)
    body(s, detail, 138, y + 38, 760, 15, 24, MUTED)
timed(s, 1)

# 19 — Thank you
s = Slide("Thank you", "Thank you. Questions?", "Before questions, three honest limits.",
          "Safewater_Lines_Full_Reference.pdf; dashboard/dist/index.html.",
          "Thank you. Before questions, three honest limits. These links are not proof of cause and effect. We were not given the total headcount. And the comments were read with AI help and checked once, not by an independent team. We are happy to take questions, and we can show any result by department or tenure on the dashboard.")
s.label("What we can and cannot say", 48, 180, 600)
for i, line in enumerate(["The links we show are not proof of cause and effect.",
                          "We do not know the total headcount, so we cannot give a response rate.",
                          "Comments were read with AI help and checked once, not by an independent team."]):
    s.rect(48, 220 + i * 46, 6, 6, BLUE)
    body(s, line, 66, 213 + i * 46, 846, 16, 24)
takeaway(s, "Happy to take questions. We can show any result by department or tenure.", y=380)
timed(s, .5)

assert abs(sum(TIMES) - 20) < 1e-9, sum(TIMES)

clashes = overlaps(bp.slides)
assert not clashes, "\n".join(map(str, clashes))

if __name__ == "__main__":
    title = "Safewater Lines | What our people are telling us"
    # Team copy: source footers on each slide and evidence lines in the notes.
    team = "Safewater_Lines_Pitch_20min_TEAM_with_sources"
    bp.render_pptx(team, title)
    bp.render_pdf(team, title)
    # Presenting copy: no internal file references on the slides or in the notes.
    name = "Safewater_Lines_Pitch_20min"
    pptx_path = bp.render_pptx(name, title, sources=False)
    pdf_path = bp.render_pdf(name, title, sources=False)
    bp.validate(pptx_path, pdf_path, preview=bp.PREVIEW / "pitch", qa_path=bp.HERE / "pitch_qa_results.json")
    bp.write_notes(bp.HERE / "PITCH_SPEAKER_GUIDE.md", bp.HERE / "pitch_slide_content.json", sources=False,
                   intro=[f"A {len(bp.slides)}-slide, 20-minute pitch in plain English. Each slide's notes start with its time window; read them as a script or in your own words.",
                          "", "Present from Safewater_Lines_Pitch_20min.pptx (no internal file references). The TEAM_with_sources copy shows the evidence file behind each slide."])
    print(f"Created {pptx_path} (presenting)\nCreated {bp.OUT / (team + '.pptx')} (team, with sources)\n{len(bp.slides)} slides, {sum(TIMES):.0f} minutes, no text overlaps.")
