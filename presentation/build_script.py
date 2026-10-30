"""Build the slide-by-slide speaker script (compact A4 PDF) for the 20-minute pitch.

Each slide gets its time window, a fuller spoken script than the
deck notes, the numbers to remember and the hand-over line. Layout is done by WeasyPrint (CLI).
"""
from __future__ import annotations

import html
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
BUILD.mkdir(exist_ok=True)
PDF = HERE / "output/Safewater_Lines_Pitch_Speaker_Script.pdf"
deck = json.loads((HERE / "pitch_slide_content.json").read_text())

# (minutes, script paragraphs, numbers to remember, hand-over line)
SCRIPT = [
    (.5, ["Good morning, and thank you for your time.",
          "Over the last few weeks we analysed the Your Voice survey: 327 responses, 30 rated questions and almost 1,900 written comments. In the next 20 minutes we will cover four things: what employees value, what they most want improved, how we tested those priorities so they are not just opinion, and what we recommend you approve today."],
     "327 responses · 30 questions · 1,892 comments", "Let me start with what we worked from."),
    (1.5, ["Briefly, the evidence. 327 people answered 30 rated questions and wrote 1,892 comments, from 23 locations and in five languages. Mumbai is the largest group, about 40% of answers, and 38% of people have been here less than three years.",
           "One rule for reading every number today: “positive” means Usually or Almost always, a four or five on the scale. We deliberately do not count “Sometimes” as positive, because it is not an endorsement.",
           "We did not rely on scores alone. We read the survey four ways: the scores themselves; which questions move together with people wanting to stay and recommend the company; the question where everyone had to pick the one thing HR should do better; and what people wrote in their own words.",
           "Two limits up front, so we are clear from the start. We were not given the total headcount, so we cannot give a response rate. And what we show are associations, not proof of cause and effect."],
     "Positive = 4–5 · Mumbai 40% · 38% under 3 years", "First, the good news."),
    (1, ["Start with the strengths, because they are large and they matter.",
         "96% understand how their work helps the business. 92% are proud to work here. 91% say people in their team genuinely help each other, and 90% feel they belong.",
         "When we asked what people would never want to lose, 119 people named their team or their colleagues. That is the foundation of this company. Whatever we change, the first rule is: do not damage this."],
     "96% · 92% proud · 91% team help · 90% belong · 119 named their team", "Now the other side: where scores are lowest."),
    (1, ["Now the gaps. These are the five lowest scores out of all 30 questions.",
         "My efforts are recognised: 72%. We celebrate each other’s success: 73%. People decisions are consistent: 75%. I understand how people decisions are made: 76%. Rewards are fair and based on performance: 76%.",
         "Look at what they have in common. Every one of them is about how people decisions are made, explained and recognised. They sit about ten points below the average question, which is 85%. So the gap is not about the work or the team; it is about decisions about people."],
     "Average question 85% · lowest five 72–76%", "Before we go further, one caution about all of these scores."),
    (1, ["The survey asked people for their name, and 69% gave it. When we split the answers, anonymous people were less positive on every key question.",
         "For example, 92% of named people plan to stay three to five years, compared with 78% of anonymous people. On recommending the company it is 92% against 82%. These differences are statistically significant, not noise.",
         "People may answer more carefully when their name is attached. So the real picture is probably a little less positive than the headline numbers. Our simple recommendation: run the next survey without names."],
     "Stay 3–5 yrs: 92% named vs 78% anonymous (p = 0.001)", "So low scores tell us part of the story. The next question is: which of these actually matter for keeping people?"),
    (1.5, ["Low scores alone do not tell us what matters most. So we asked a second question: which issues move together with the outcomes leaders care about, people recommending the company, being satisfied, and planning to stay.",
           "Together, the questions leaders can act on explain about 65% of the differences between people on those outcomes. We then split that fairly between questions, because many of them overlap.",
           "Each dot here is one question. Further left means fewer people answered positively. Higher up means a stronger link to staying and recommending. The shaded top-left corner is where both are true: low score and high importance. Six questions are there: leaders act on feedback, equal growth opportunities, teams working together, fair rewards, consistent decisions and understanding how decisions are made.",
           "On the right, by survey area, fairness carries the largest share, about 31%. Note what is not in that corner: own-team help is very high but barely separates people who stay from those who might leave, so it is a strength to protect, not a lever. As always, these are associations, not proof of cause."],
     "Explains 65% · fairness 31% · six “fix first” questions", "That is what the numbers say. Next, what people said in their own words."),
    (1.5, ["We also mapped the written comments. Every suggestion was tagged with its topics, and this map shows which topics people raise together. Each circle is a topic: the bigger it is, the more people raised it. A line means two topics came up in the same answer at least ten times.",
           "The topics fall naturally into three families. Orange: fairness, recognition, career growth, workload and pay. That is our first priority. Blue: communication, being heard and follow-through, support and trust. That is our second. Green: working across teams and clear roles and processes. That is the targeted fix.",
           "One honest caution. Some links follow the wording of the questions. For example, most communication-and-teamwork mentions came from the teamwork question itself. So we use this map to organise what people said, not as separate proof. The proof is in the next slide."],
     "1,230 coded answers from 305 people · 3 families → 3 recommendations", "So how did we decide which themes become priorities?"),
    (1, ["We put every theme through the same four checks, and we set the pass marks before we looked at the results, so we could not bend them to fit a story. Is the score low? Is it linked to staying and recommending? Did people pick it as HR’s main job? Did people raise it on their own when asked for one change?",
           "Only two themes are strong on all four: fair people decisions with career growth, and leaders who listen and act. Those are our two priorities.",
           "Recognition scores lowest and people write about it a lot, but on its own it is less linked to staying, so it sits inside Priority 1 rather than standing alone. Cross-team work is real but smaller, so it gets a targeted fix. Pay and facilities clearly matter to people, but no survey question measured them, so they go to the yearly review."],
     "2 of 7 themes pass all four checks", "Let me take the two priorities in turn."),
    (1.5, ["Priority 1 is fair decisions that people understand: promotions, pay rises, rewards and recognition.",
           "Only 75% say people decisions are made consistently, one of the lowest scores in the survey. Of the areas leaders can change, fairness is the one most linked to people wanting to stay and recommend the company. And 51 people said HR’s main job should be helping careers grow.",
           "In one employee’s words: “Inconsistent performance evaluations and opaque promotion criteria.” That is typical of what we read.",
           "This is not a claim that decisions are unfair. It is that people cannot see how they are made. In practice, that means clear, published rules for promotion, pay and rewards, a reason given for every decision, and managers recognising each person regularly."],
     "75% consistent · fairness No. 1 link · 51 chose careers", "The second priority is about what happens after people speak up."),
    (1.5, ["Priority 2 is leaders who listen, and then act.",
           "We asked everyone to pick the one thing HR should do better. The top answer, by a clear margin, was listening to employees and their concerns: 67 people, one in five. 80% say leaders act on feedback, and of all the questions leaders can act on, it is the single one most linked to people wanting to stay.",
           "One employee put it simply: “Employees’ problems and suggestions should be heard and appropriate action taken promptly.”",
           "People are not asking for more announcements. Notice that “keep us informed” was one of the least chosen options. They want proof that when they raise something, something happens. In practice: every concern gets an owner, a date and an answer."],
     "67 chose listening (20%) · 80% leaders act · top link to staying", "Where should we begin?"),
    (1, ["This table shows the share of positive answers by group. Darker means lower, and we only show groups of at least ten people.",
           "Customer Service stands out. It is the lowest group on all four measures: 64% on fair decisions, 69% on leaders acting, only 57% feel recognised, and 76% plan to stay, against 87% overall. People with three to five years’ service also dip, and women answer about ten points less positively than men on fairness and recognition.",
           "This is not about blaming a team. It tells us where to listen first, and where a pilot can show the clearest change."],
     "Customer Service (51): 64% · 69% · 57% · 76%", "Before the plan, one smaller issue and one we cannot fix in 90 days."),
    (1, ["People rate their own team very highly, 91%, but teams working together across the company lower, at 82%. 45 people rate their own team well but work with other teams poorly.",
           "It is real, but it is smaller than the two priorities, and people rarely raised it on their own. So rather than a big programme, we suggest a targeted fix: take one handover in Customer Service and agree who sends what, who receives it, and who covers when someone is away."],
     "Own team 91% vs across teams 82% · 45 people", "And then, what else people told us."),
    (1, ["When we asked the most open question, “if you could make one change”, the answers we did not prompt, people mostly asked for better communication, recognition, career growth and follow-through. That matches our two priorities, which is reassuring.",
           "People also care about pay, benefits and facilities: 51 people picked it as HR’s main job. A 90-day pilot cannot fix pay, and we will not pretend it can. So we suggest sending it to the yearly pay and facilities review, and telling people clearly that this is where it went. Being open about that builds trust in itself."],
     "One change: communication 69 · recognition 60 · career 47 · follow-through 41", "So here is what we propose."),
    (1.5, ["One 90-day pilot with three parts, starting in Customer Service, using the tools and processes we already have.",
           "Part one, fair decisions, owned by the HR head: publish clear rules for promotion, pay and rewards; give a reason for every decision; and have managers recognise each person every month.",
           "Part two, listen and act, owned by a leadership sponsor with HR: log every concern with an owner and a date; send a monthly “you said, we did” update; and hold listening sessions, starting in Customer Service.",
           "Part three, handovers, owned by the Operations head: map one Customer Service handover, agree who sends, receives and covers, and flag anything overdue.",
           "None of this needs a new system. The owners are our proposal and need your approval."],
     "3 parts · 3 owners · no new system", "Here is how the 90 days run."),
    (1, ["Day 0 is the day you approve the pilot.",
           "In the first two weeks we pick the pilot teams, check the current rules, and run a short anonymous survey as our starting point. By day 30 the rules are published, owners are named and the concern log is open. From day 31 to 60 we run it: monthly recognition and updates, and a weekly review of problems, checking it is not adding paperwork. In the last month we repeat the short survey and decide together: grow it, change it, or stop it.",
           "At each step, leadership decides whether to continue, so the risk stays small."],
     "Days 0–14 · 15–30 · 31–60 · 61–90", "How will we know it worked?"),
    (1, ["For each part we check two things: did we do the work, and did employees notice?",
           "For fair decisions: rules published for every pilot role, and the share who say decisions are consistent rising from 75% to about 80%. For listen and act: every concern answered within two working days, and “leaders act on feedback” rising from 80% to about 85%. For handovers: at least 95% complete by day 60.",
           "We measure with a short anonymous survey so people can be honest, and the targets are confirmed in the first 14 days once we have that baseline. We also watch our strengths, pride and own-team help, to make sure they do not drop."],
     "75% → ~80% · 80% → ~85% · 95% handovers", "Which brings us to what we need from you."),
    (1, ["We are asking for three decisions today.",
           "One: approve one 90-day pilot with the three parts: fair decisions, listen and act, and one handover, starting in Customer Service.",
           "Two: name the owners, the HR head, a leadership sponsor and the Operations head, and give them time for one review a month.",
           "Three: run the next survey without names, starting with a short anonymous survey now and again at day 90."],
     "Approve · name owners · go anonymous", "Before questions, a word on what we can and cannot say."),
    (.5, ["Thank you. Three honest limits before we open for questions. The links we showed are not proof of cause and effect; the pilot is how we test them. We do not know the total headcount, so we cannot give a response rate. And the comments were read with AI help and checked once, not by an independent team.",
          "We are happy to take questions, and we can show any result by department or tenure."],
     "", ""),
]
assert len(SCRIPT) == len(deck) == 18 and abs(sum(m for m, *_ in SCRIPT) - 20) < 1e-9


def clock(t):
    return f"{int(t)}:{round(t % 1 * 60):02d}"


pages, start, words = [], 0.0, 0
for i, ((minutes, paras, nums, nxt), sc) in enumerate(zip(SCRIPT, deck), 1):
    words += sum(len(p.split()) for p in paras)
    title = sc["title"].replace("\n", " ")
    body = "".join(f"<p>{html.escape(p)}</p>" for p in paras)
    extra = (f'<div class="nums"><b>Numbers to remember</b> {html.escape(nums)}</div>' if nums else "") + \
            (f'<div class="next"><b>Hand over</b> “{html.escape(nxt)}”</div>' if nxt else "")
    pages.append(f'''<section><div class="head"><span class="no">{i:02d}</span><span class="title">{html.escape(title)}</span>
<span class="time">{clock(start)} – {clock(start + minutes)} · {minutes:g} min</span></div>
{body}{extra}</section>''')
    start += minutes

CSS = """
@page { size: A4; margin: 15mm 16mm 15mm 16mm;
  @bottom-left { content: "Safewater Lines · 20-minute pitch · speaker script"; font: 7.5pt Arial; color: #6b7b88 }
  @bottom-right { content: counter(page) " / " counter(pages); font: 7.5pt Arial; color: #6b7b88 } }
body { font-family: Arial, Helvetica, sans-serif; font-size: 10pt; line-height: 1.42; color: #243441 }
.cover .kicker { color: #2f5d7c; font-weight: bold; font-size: 8pt; letter-spacing: .04em }
.cover h1 { font-size: 22pt; margin: 2pt 0 4pt } .cover p { color: #5b6b78 }
.cover table { border-collapse: collapse; width: 100%; font-size: 9pt; margin-top: 8pt }
.cover td, .cover th { padding: 3pt 5pt; border-bottom: 1px solid #e1e7eb; text-align: left }
.cover th { background: #eef2f5; color: #2f5d7c; font-size: 7.6pt; text-transform: uppercase }
section { break-inside: avoid; margin-bottom: 12pt }
.head { border-bottom: 1.5px solid #2f5d7c; padding-bottom: 3pt; margin-bottom: 5pt; break-after: avoid }
.no { color: #2f5d7c; font-weight: bold; font-size: 15pt; margin-right: 8pt }
.title { font-weight: bold; font-size: 13pt }
.time { float: right; color: #2f5d7c; font-weight: bold; font-size: 9.5pt; margin-top: 4pt }
p { margin: 0 0 6pt }
.nums, .next { font-size: 8.8pt; padding: 3pt 8pt; margin-top: 4pt; border-left: 3px solid #2f5d7c; background: #f3f6f8 }
.next { background: none; color: #5b6b78 }
.nums b, .next b { color: #2f5d7c; text-transform: uppercase; font-size: 7.6pt; letter-spacing: .03em; margin-right: 6pt }
"""

if __name__ == "__main__":
    cover = f'''<div class="cover"><div class="kicker">SAFEWATER LINES / YOUR VOICE SURVEY</div><h1>Speaker script</h1>
<p>Slide-by-slide script for the 20-minute pitch ({words:,} words, about {words / 20:.0f} words a minute, a calm pace with room for pauses). Read it as written or in your own words; the
time windows keep you on track. Use the methodology sheet for detailed questions.</p>
</div>'''
    src = BUILD / "speaker_script.html"
    src.write_text(f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Speaker script</title><style>{CSS}</style></head><body>{cover}{''.join(pages)}</body></html>")
    subprocess.run(["weasyprint", "--quiet", str(src), str(PDF)], check=True)
    print(f"Created {PDF} ({words} words, {len(pages)} slides)")
