<p>SAFEWATER LINES / YOUR VOICE SURVEY</p>

# Methodology sheet

<p class="lede">Team copy for questions on the 20-minute pitch. Each section gives the plain answer first, then the detail. All figures come from the analysis notebook (<code>00_data_understanding_eda.ipynb</code>) and its exported tables.</p>

## At a glance

| Pitch slide | What it claims | Method | Key number |
|---|---|---|---|
| 2 | What we analysed | Cleaned survey export | 327 responses, 30 rated questions, 1,892 comments |
| 3–4 | Strengths and gaps | Favourable share (answers 4–5) | Average question 85% positive |
| 5 | Anonymous answers are less positive | Named vs anonymous comparison, Fisher exact test | Stay 3–5 yrs: 92% vs 78% (p = 0.001) |
| 6 | What links most to staying and recommending | Relative-weights regression, 500 bootstraps | R² = 0.65; fairness 31% of the link |
| 7 | Comments form three groups | Topic co-occurrence map (VOSviewer-style) | 98 communication–teamwork co-mentions |
| 8 | Two themes pass four checks | Triangulation with pre-set pass marks | 2 of 7 themes strong on all four |
| 10, 13 | What people asked HR for | Forced single choice, counts | Listening: 67 people (20%) |
| 11 | Start in Customer Service | Favourable share by group (n ≥ 10) | Lowest group on fair decisions, recognition and plan to stay |

## 1. Data and preparation

- **Source:** the survey workbook with responses to 21 October. **327 response records**, 30 rated questions on a 1–5 scale (Credibility, Respect, Fairness, Pride, Camaraderie, Overall), 6 open questions, 1 forced-choice HR question and 5 profile fields.
- **Comments:** 1,892 non-blank answers across the 6 open questions, in English, Hindi, Marathi, Tamil and Malayalam.
- **Cleaning:** answer labels mapped to 1–5; profile fields standardised; departments under 10 people grouped as “Other”. **Names were removed** from the analysis file; only a yes/no flag for “gave a name” was kept.
- **Straight-liners:** 54 people (16.5%) gave the identical answer to all 30 questions. They are kept in the headline results and every key result is re-checked without them.
- **Not available:** total headcount (so no response rate) and any employee ID linking to HR records.

## 2. How scores are read

- **Positive (favourable) = 4 or 5**, “Usually” or “Almost always”. 3 (“Sometimes”) is *not* counted as positive, and 1–3 is not called “unfavourable”.
- This is the standard way large employee surveys report results (for example, the UK Civil Service People Survey). It is easier to explain than averages and does not assume equal gaps between answer options.
- The average question is 85% positive. The five lowest (recognition, celebrating success, consistent decisions, understanding decisions, fair rewards) sit around 72–76%.

## 3. “Link to staying”: relative-weights analysis (slide 6)

**Plain answer:** we measured how strongly each question moves together with whether people want to stay, would recommend the company and are satisfied, then split the credit fairly between questions that overlap.

1. **Outcome per person** = average of three answers: *I would recommend this organization as a great place to work* (OVR1), *I am satisfied with the overall employee experience* (OVR4), *I see myself continuing to work here over the next 3–5 years* (PRI3).
2. **Explanatory questions:** the 19 questions leaders can act on, from Credibility, Respect, Fairness and Camaraderie. Pride and belonging are excluded because they are almost the outcome itself.
3. **Fit:** a linear regression of the outcome on the 19 questions explains **R² = 0.65** of the variation (0.61 without straight-liners).
4. **Fair split (Johnson’s relative weights, 2000):** the questions are converted into uncorrelated versions of themselves, the regression is run on those, and the explained variation is mapped back to the original questions. Each question’s share is rescaled to sum to 100%. This avoids ordinary regression arbitrarily giving the credit to one of several overlapping questions.
5. **Uncertainty:** 500 bootstrap resamples of the 327 people give a 95% range for each share and the probability that a question ranks in the top five (P(top 5)).
6. **By survey block** (each block averaged into one score, same method): Fairness 31%, Respect 27%, Credibility 24%, Camaraderie 18%.

**Robustness:** the ranking is essentially unchanged without straight-liners (Spearman ρ = 1.00). Among the 100 anonymous respondents it shifts (ρ = 0.59): recognition rises into the top tier and cross-team work drops, which is why recognition sits inside Priority 1.

## 4. The priority chart (slide 6)

- **Horizontal:** survey score (% positive). **Vertical:** link share from section 3.
- **Lines are the medians** of the 19 questions: 82.6% positive and 5.0% link. If all questions mattered equally each would carry 100 / 19 = 5.3%.
- **Fix first** = below-median score *and* at-or-above-median link. **Protect** = high link, high score. **Monitor** = low score, lower link. **Maintain** = high score, lower link.

| Code | Question (short) | Positive | Link share (95% range) | P(top 5) |
|---|---|---|---|---|
| CRE5 | Leaders act on feedback | 79.8% | 8.5% (5.0–13.5) | 0.71 |
| FAI2 | Equal growth opportunities | 81.7% | 8.1% (4.9–11.9) | 0.75 |
| CAM2 | Teams work well together | 82.3% | 7.5% (4.0–11.5) | 0.64 |
| FAI1 | Fair rewards and recognition | 76.1% | 5.9% (3.4–9.6) | 0.27 |
| FAI3 | Consistent decisions | 74.6% | 5.1% (2.8–8.5) | 0.14 |
| FAI5 | Understand how decisions are made | 75.5% | 5.0% (2.4–8.8) | 0.17 |

Ranges overlap, so the chart is read as tiers, not an exact order. Two questions sit on a median line: *Understand decisions* (link 5.04%, counted as fix first) and *Safe to share views* (score 82.6%, counted as protect).

## 5. Comment analysis (slides 7, 10, 13)

- **Codebook:** 15 topics with written include/exclude rules (e.g. communication, recognition, career growth, fairness, voice and follow-through, cross-team work, pay and benefits).
- **Coding:** each answer read in context and given **one or more topics** (multi-label). Answers were also classed as suggestion, current strength, no concern, no change proposed or unclear.
- **Who coded:** an AI assistant, followed by a documented second reading by the same assistant (568 re-reads, 53 labels revised). This is **not** an independent human double-coding, so there is no inter-rater agreement statistic. A small number of translations (13) still await confirmation.
- **Counting:** topics are counted **once per person**, not per mention, so one long answer cannot inflate a topic. (The topic map in section 6 counts answers instead.)

## 6. Topic map (slide 7)

- **Plain answer:** a circle is a topic; a line means two topics were raised in the same answer at least 10 times. Colours are groups of topics that tend to appear together.
- **Data:** 1,230 topic-coded suggestion answers from 305 people. Topics shown if raised in at least 20 answers (13 topics; tools and facilities had no strong links and is omitted from the slide).
- **Method:** circle size = number of people; line width = shared mentions. Layout uses association strength (pair count ÷ product of topic counts) with our own force-directed placement; groups come from weighted modularity clustering. It is **inspired by VOSviewer**, not a native VOSviewer run.
- **Key caution, prompt dependence:** 85 of the 98 communication–teamwork co-mentions came from the teamwork question, and 41 of the 46 fairness–career co-mentions came from the fairness question. The map organises what people said; it is not independent proof of the priorities.

## 7. HR choice question (slides 10, 13)

Everyone picked **one** answer to “If HR could do one thing better…”. Counts are of people (n = 327). Top three: listening to employees (67), career progression (51), benefits and facilities (51). Because the options were fixed, it shows relative preference, not everything people want.

## 8. Four-check test (slide 8)

Each theme was graded on four independent sources. **Pass marks were set before looking at the results.**

| Check | Measure | Strong | Medium |
|---|---|---|---|
| Low score | Lowest rank of the theme’s questions among all 30 | rank ≤ 6 | rank ≤ 10 |
| Linked to staying | Highest P(top 5) of the theme’s questions in the bootstrap | ≥ 0.60 | ≥ 0.20 |
| HR wish list | % of people choosing the matching HR option(s) | ≥ 15% | ≥ 8% |
| Own words | People raising the topic in the open “one change” question | ≥ 40 | ≥ 25 |

| Theme | Low score | Linked to staying | HR wish list | Own words | Strong (of 4) |
|---|---|---|---|---|---|
| Fair, explainable people decisions & growth | Strong | Strong | Strong | Strong | 4 |
| Leaders listen and visibly act | Strong | Strong | Strong | Strong | 4 |
| Recognition of contributions | Strong | Weak | Medium | Strong | 2 |
| Cross-team collaboration | Medium | Strong | — | Weak | 1 |
| Support when problems arise | Weak | Weak | Strong | Medium | 1 |
| Workload & role clarity | Weak | Medium | Weak | Strong | 1 |
| Pay, benefits & facilities | — | — | Strong | Medium | 1 |

A dash means the source has no matching question (e.g. there is no rated pay question, and no HR option for cross-team work).

## 9. Named vs anonymous (slide 5)

| | n | Plan to stay 3–5 yrs | Would recommend | Fix-first questions |
|---|---|---|---|---|
| Gave a name | 227 | 91.6% | 92.5% | 81.6% |
| Anonymous | 100 | 78.0% | 82.0% | 70.8% |

Differences are statistically significant: Fisher exact test p = 0.001 (stay) and p = 0.006 (recommend); Mann–Whitney on the overall culture score p = 0.005. This is **consistent with** more careful answers when named, but the two groups may also simply be different people. Either way, the headline scores are probably a little optimistic.

## 10. Group comparison (slide 11)

% positive by department, tenure and gender, **only for groups of 10 or more**. Columns: fair decisions (average of FAI1, FAI3, FAI5), leaders act (CRE5), recognition (RES4), plan to stay (PRI3). Groups overlap and differ in role mix, so this shows where to listen first, not which team is to blame.

## 11. Plan measures (slide 16)

Each pilot part has a process check (did we do it) and an experience check (did employees notice), measured by a short **anonymous** pulse survey at the start and at Day 90. Targets of about +5 points are suggestions, to be confirmed against the Day-0–14 baseline. Pride and own-team help are watched so they do not fall.

## 12. Limits to state openly

- Associations, not causes; the same people answered both the questions and the outcome, which can inflate links (common-method effect).
- No headcount, so no response rate and no claim about non-responders.
- 69% gave a name; anonymous answers are less positive.
- Comment coding is AI-assisted with a self re-review, not independent human coding.
- Groups under 10 people are not reported.

## Likely questions, short answers

**Why not just fix the lowest scores?** Recognition scores lowest but on its own is weakly linked to staying. Fairness and leaders acting are both low *and* strongly linked, and they pass all four checks.

**Is R² = 0.65 high?** Yes for survey data. Part of it reflects people answering consistently across one survey, so we use it to rank questions, not to forecast.

**Why relative weights and not regression coefficients?** The questions overlap heavily. Ordinary coefficients split credit unstably between overlapping questions; relative weights split it fairly and always add up to the total explained.

**How sure is the order?** The 500-resample bootstrap ranges overlap, so we read tiers. Leaders act on feedback and equal growth are in the top five in 71% and 75% of resamples.

**Does this prove fairness causes people to leave?** No. It shows which questions move together with wanting to stay. The pilot is the test.

**Were the comments read by people?** They were coded by an AI assistant with a documented second reading against a written codebook. We recommend a short human spot-check before decisions rely on topic counts.

**Is the topic map VOSviewer?** It follows VOSviewer’s idea (topic co-occurrence, association strength, clustering) with our own implementation, and links depend on question wording.

**Why Customer Service?** With 51 people it is the lowest group on fair decisions, leaders acting, recognition and plan to stay. That makes it the place a pilot can show the clearest change.

**Why is pay not a priority?** There is no rated pay question and a 90-day pilot cannot change pay. 51 people chose it as HR’s main job, so we route it to the yearly pay and facilities review and say so openly.

**Why say “positive” only for 4–5?** “Sometimes” is not an endorsement. Counting it would hide the gap. This matches common practice in large employee surveys.

<p class="foot">Tools: Python (pandas, NumPy, SciPy, Matplotlib), run in one reproducible notebook with pinned dependencies (uv). No data was uploaded to any external service for the analysis; no names appear in any output.</p>
