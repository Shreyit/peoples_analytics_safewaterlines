# Presentation storyline and speaker guide

A 18-slide, 20-minute pitch in plain English. Each slide's notes start with its time window; read them as a script or in your own words.

Present from Safewater_Lines_Pitch_20min.pptx (no internal file references). The TEAM_with_sources copy shows the evidence file behind each slide.

## 01 · What our people are telling us

[0:00 – 0:30] Good morning. We analysed the Your Voice survey: 327 responses, 30 rated questions and almost 1,900 written comments. In the next 20 minutes we will show what employees value, what they most want improved, how we tested those priorities, and what we recommend.

**Evidence:** Your Voice survey (responses to 21 October); analysis 30 October 2026.

## 02 · What we analysed

[0:30 – 2:00] Briefly, the evidence. 327 responses, 30 rated questions and 1,892 written comments, from 23 locations in five languages. Throughout, positive means Usually or Almost always, four or five on the scale. Sometimes is not counted as positive. We read the survey in four ways: the scores, which questions move with wanting to stay and recommend, the question where everyone picked one thing HR should do better, and the open comments. Two limits up front: we were not given the headcount, so there is no response rate, and these are associations, not proof of cause.

**Evidence:** survey_clean.csv; workbook language sheets; named_vs_anonymous.csv; favourable = 4–5.

## 03 · Strengths to protect: pride and team support

[2:00 – 3:00] Start with the strengths, because they are large. Almost everyone understands how their work helps the business. 92% are proud to work here. 91% say people in their team help each other, and 90% feel they belong. When we asked what people never want to lose, 119 people named their team or colleagues. Whatever we change, we must protect this.

**Evidence:** item_evidence_profile.csv (PRI2, PRI1, CAM1, CAM3).

## 04 · The five lowest scores are all about people decisions

[3:00 – 4:00] Now the gaps. These are the five lowest scores out of 30 questions. They have one thing in common: recognition, consistent decisions, understanding how decisions are made, and fair rewards. All of them are about how people decisions are made and explained. They sit about 10 points below the average question.

**Evidence:** item_evidence_profile.csv (RES4, CAM5, FAI3, FAI5, FAI1).

## 05 · Anonymous answers are clearly less positive

[4:00 – 5:00] One caution on all the scores. The survey asked for a name, and 69% gave it. Anonymous answers were less positive on every key question. For example, 92% of named respondents plan to stay 3 to 5 years, against 78% of anonymous respondents. People may answer more carefully when their name is attached, so the headline scores are probably a little optimistic. The practical fix is simple: do not ask for names next time.

**Evidence:** named_vs_anonymous.csv; notebook Step 7.4.

## 06 · What links most to staying and recommending

[5:00 – 6:30] Low scores alone do not tell us what matters most. So we asked which questions move together with three outcomes: recommending the company, being satisfied, and planning to stay. Together the questions explain about 65% of the differences in those outcomes. Each dot is a question. Further left means fewer people answered positively; higher up is a stronger link to the outcomes. The shaded corner is where both are true: leaders acting on feedback, equal growth opportunities, fair rewards, consistent and understood decisions, and teams working together. By survey block, fairness carries the largest share, about 31%. These are associations, not proof of cause.

**Evidence:** priority_matrix.csv; driver_model_summary.csv; notebook Step 7.1 (relative weights, 500 bootstraps).

## 07 · In their own words, concerns form three groups

[6:30 – 8:00] We also mapped the written comments. Each circle is a topic; bigger means more people raised it. A line means two topics were raised in the same answer at least ten times. The topics fall into three groups. Orange: fairness, recognition, career growth, workload and pay, which is our first priority. Blue: communication, being heard and follow-through, support and trust, which is our second. Green: working across teams and clear roles and processes, which is the targeted fix. One honest caution: some links follow the question wording. For example, most communication-and-teamwork mentions came from the teamwork question. So the map organises what people said; it is not separate proof.

**Evidence:** reports/network/topic_network_data.json; topic_network_edges.csv; notebook §5.4 (VOSviewer-style map, own layout and grouping).

## 08 · Two themes pass all four evidence checks

[8:00 – 9:00] We then put every theme through the same four checks, with the pass marks set before we looked at the results. Is the score low? Is it linked to staying and recommending? Did people pick it as HR's main job? Did people raise it on their own when asked for one change? Only two themes are strong on all four: fair people decisions with career growth, and leaders who listen and act. Those are our two priorities. Recognition scores lowest and is written about a lot, so it sits inside Priority 1. Cross-team work is real but smaller, so it gets a targeted fix. Pay and facilities matter, but no survey question measured them, so they go to the yearly review.

**Evidence:** priority_triangulation.csv; notebook Step 7.3; pass marks fixed before reading the result.

## 09 · Priority 1: fair decisions that people understand

[9:00 – 10:30] Priority one is fair decisions that people understand. Only 75% say people decisions are made consistently. Of the areas leaders can change, fairness is the one most linked to people wanting to stay and recommend the company. And 51 people said HR's main job should be helping careers grow. In one employee's words: inconsistent performance evaluations and opaque promotion criteria. What it means in practice: clear rules for promotion, pay and rewards, and a reason given for every decision.

**Evidence:** item_evidence_profile.csv; driver_model_summary.csv; hr_priority_counts.csv; quote verbatim, de-identified.

## 10 · Priority 2: leaders who listen, and then act

[10:30 – 12:00] Priority two is leaders who listen and then act. We asked everyone to pick the one thing HR should do better. The top answer, by a clear margin, was listening to employees and their concerns: 67 people. Only 80% say leaders act on feedback, and among the actionable questions it is the one most linked to people wanting to stay. People are not asking for more announcements. They want proof that when they raise something, something happens.

**Evidence:** hr_priority_counts.csv; item_evidence_profile.csv (CRE5); quote verbatim, de-identified.

## 11 · Where to start: Customer Service

[12:00 – 13:00] Where should we start? This table shows the share of positive answers by group, and darker means lower. Customer Service is the lowest group on almost everything: only 57% feel recognised, and 76% plan to stay. People with 3 to 5 years' service also dip. Women answer less positively than men on fairness and recognition. This is not about blaming a team. It tells us where to listen first and where a pilot can make the biggest difference.

**Evidence:** group_hotspots.csv; notebook Step 7.5.

## 12 · A smaller fix: handovers between teams

[13:00 – 14:00] There is one smaller issue. People rate their own team very highly, 91%, but teams working together across the company lower, 82%. 45 people rate their own team well but other teams poorly. It is real, but smaller than the two priorities, and people rarely raised it on their own. So we suggest a targeted fix: take one handover in Customer Service and agree who sends what, who receives it, and who covers when someone is away.

**Evidence:** cross_team_paired_detail.csv; item_evidence_profile.csv (CAM1, CAM2).

## 13 · What else people told us

[14:00 – 15:00] When we asked an open question, if you could make one change, people mostly asked for better communication, recognition, career growth and follow-through. That matches our two priorities. People also care about pay, benefits and facilities: 51 people picked it as HR's main job. A 90-day pilot cannot fix pay, so we suggest sending it to the yearly pay and facilities review, and telling people clearly that this is where it went.

**Evidence:** one_change_topics.csv; hr_priority_counts.csv.

## 14 · Our plan: one 90-day pilot, three parts

[15:00 – 16:30] Here is the plan. One 90-day pilot with three parts, starting in Customer Service. Part one, owned by the HR head: publish clear rules for promotion, pay and rewards, give a reason for every decision, and have managers recognise each person every month. Part two, owned by a leadership sponsor: log every concern with an owner and a date, and send a monthly 'you said, we did' update. Part three, owned by the Operations head: fix one handover between teams. None of this needs a new system.

**Evidence:** implementation_roadmap_0_90_days.csv (revised IDs P1, P2, T); proposed owners, not approved commitments.

## 15 · 90 days, step by step

[16:30 – 17:30] Step by step. In the first two weeks we choose the pilot teams, check the current rules and run a short anonymous survey as our starting point. By day 30 the rules are published, owners are named and the concern log is open. From day 31 to 60 we run it, review problems every week and check it is not adding paperwork. In the last month we repeat the short survey and decide together: grow it, change it or stop it.

**Evidence:** roadmap_decision_gates.csv (adapted).

## 16 · How we will know it worked

[17:30 – 18:30] How will we know it worked? For each part we check two things: did we do the work, and did employees notice? For example, rules published for every pilot role, and the share who say decisions are consistent going up from 75% by about 5 points. We measure with a short anonymous survey so people can be honest. And we watch our strengths, pride and teamwork, to make sure they do not drop.

**Evidence:** roadmap_kpi_dictionary.csv; item_evidence_profile.csv. Targets are suggestions to confirm in the first 14 days.

## 17 · What we ask you to decide today

[18:30 – 19:30] We are asking for three decisions today. One: approve one 90-day pilot with the three parts. Two: name the owners, the HR head, a leadership sponsor and the Operations head, and give them time for one review a month. Three: run the next survey without names. Thank you. We are happy to take questions.

**Evidence:** implementation_roadmap_0_90_days.csv; roadmap_decision_gates.csv.

## 18 · Thank you. Questions?

[19:30 – 20:00] Thank you. Before questions, three honest limits. These links are not proof of cause and effect. We were not given the total headcount. And the comments were read with AI help and checked once, not by an independent team. We are happy to take questions, and we can show any result by department or tenure on the dashboard.

**Evidence:** Safewater_Lines_Full_Reference.pdf; dashboard/dist/index.html.
