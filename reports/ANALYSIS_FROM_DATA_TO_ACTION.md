# Safewater Lines — from source data to findings and action

Updated 29 October 2026. This is the complete reading guide for the analysis so far: start at the base, follow how each method adds evidence, then see how the findings become proposed actions. All calculations, coding decisions and outputs remain in [one notebook](../notebooks/00_data_understanding_eda.ipynb). The assignment is documented in [the brief](../docs/PROJECT_BRIEF.md).

## Read this first: what is complete?

The analytical draft, a documented same-assistant review and the proposed implementation roadmap are complete. The review reread 568 comment records, including all 104 original flags, and changed 53 coding/status decisions. 75 cases still need context clarification/confirmation. No independent team-member or native-speaker validation is claimed. A roadmap with proposed owners, timing and measures is ready for organisational review; the PowerPoint is not yet built.

Cross-team execution and fairness were first selected as the focus. The Step 7 prioritisation check (section 15) revised the order: Priority 1 is fair, explainable people decisions and growth, with recognition; Priority 2 is leaders listening and visibly acting; cross-team handovers are a targeted fix; role clarity/workload/backup supports the pilot. The order rests on four sources of evidence with grading rules fixed in advance, not on a single synthetic score.

## The progression at a glance

| Level | Question | What it adds |
| --- | --- | --- |
| 0. Purpose | What organisational decision must this serve? | Preserve strengths and define practical improvements, not just scores/dashboards |
| 1. Source and structure | What exactly did we receive? | 327 master response records, six rating blocks, comments and one HR choice |
| 2. Quality and types | Can the variables be interpreted consistently? | Harmonised labels, documented grouping, identified missing/repetitive answers |
| 3. Base distributions | How did people answer each question? | Counts, Sometimes/unfavourable shares, favourable shares and working means |
| 4. Measurement and relationships | Do items cohere, move together or vary by group? | Reliability diagnostics, exploratory associations, adjusted group comparisons and sensitivity |
| 5. Employee voice | What do employees value and ask to improve? | Contextual multi-label topic coding and separate response stances |
| 6. Integration and focus | How do ratings and comments inform the same decision? | Paired cross-team profiles, fairness breadth, comment links and focused groups |
| 7. Network | Which topics are mentioned together? | An exploratory same-answer map with prompt-dependence controls |
| 8. Review | Are the decisions traceable and the claims accurate? | Second assistant reading, before/after counts, unresolved cases and recalculated facts |
| 9. Action | Who could do what, when, and how would we assess it? | 0–90-day pilot roadmap, KPI definitions and decision gates |

## 0. The organisational purpose

The assignment asks what the survey reveals about employee experience and culture, what Safewater Lines should preserve, where improvements are needed, and how HR/business leaders can turn findings into measurable interventions. Required outputs include analysis, an evidence-backed organisational story, understandable visuals, prioritised recommendations, a roadmap and an executive presentation. Submission/presentation is 30 October 2026 at TISS; a presentation duration was not supplied.

Our decision chain is: organisational question → survey evidence → bounded interpretation → proposed action → accountable owner → baseline/success measure → review decision. A plausible explanation is not automatically a demonstrated cause.

## 1. Start with the source and the unit of analysis

Source: `data/raw/Your Voice- Responses 21 OCT - FINAL.xlsx`. We analyse `SWL - MASTERDATA`, which contains 327 response rows and 43 original columns after the two-row header. It has 30 rating items, six comment questions, one single-choice HR priority and six demographic/identity fields including an optional name. Removing the name field leaves five demographics. The clean table has 56 columns after adding documented derived variables.

The five language exports total 330 rows, while the master has 327. There is no verified row-level deletion log, so we do not claim exactly three test cases were removed. The language sheets contain tenure bands converted into dates; the consolidated master is the analysis source. `Masterdata - do not refer` is excluded. `Sheet2` contributes an HR-option theme mapping, not its old pivot counts.

A row is a supplied response record, used as the available proxy for a contributor. We have not independently verified unique employee identities. An individual item answer, a comment, a response record and a group are different units; do not mix their denominators.

There are 9,810 valid rating answers (327 × 30), not that many independent employees. There are 1,892 nonblank comment records from 321 source records. Eligible workforce size, workforce composition, collection procedures, earlier waves and observed turnover/performance outcomes were not supplied. The original response rate and representativeness cannot be calculated from these files.

## 2. Variables, types and transformations

| Variable | Analytical type | How to understand it |
| --- | --- | --- |
| location / department / gender | Nominal category | Labels without numerical order; useful for descriptive grouping |
| designation | Free-text category | Inconsistent role labels; keyword-based level is an analyst approximation |
| tenure | Ordered category | 0–3, 3–5, 5–10, 10–15, 15+ years; bands, not exact service years |
| CRE1…OVR5 | Ordinal item, stored as 1–5 | Ordered frequency categories; equal spacing is not guaranteed |
| oe_leaders_trust / oe_feel_valued / oe_fairness_concern | Qualitative text | Leadership trust, support/value/respect and fairness feedback |
| oe_value_most / oe_teamwork / oe_one_change | Qualitative text | Strengths to preserve, teamwork suggestions and one change |
| hr_priority / hr_theme | Single-choice category / grouped category | One chosen HR improvement, mapped into eight themes |
| region / level / dept_group | Derived categories | Cities grouped geographically; approximate levels; departments with fewer than 10 responses pooled into Other |
| straightliner / gave_name | Boolean flags | Same rating throughout / name supplied; neither is a diagnosis of invalid or biased answers |
| CRE / RES / FAI / PRI / CAM / OVR | Working numerical summaries | Equal-weight means of five specified items per block |
| CULTURE_MEAN / fav_pct | Derived mean / percentage | 25-item culture summary / respondent's favourable share across all 30 items |

We standardised case/label variants and mapped Usually/Often together. The scale is 1 Almost never, 2 Rarely, 3 Sometimes, 4 Usually/Often, 5 Almost always/Always. Sometimes is not neutral. CSV stores category labels; ordering is established explicitly in the notebook where needed.

The dedicated full_name field is dropped from the processed survey. Free-text answers can still contain identifying information: the processed survey remains confidential and must not be treated as anonymised. Presentation exports contain aggregate findings and no raw comments or case-level audit IDs. The raw workbook remains unchanged.

### What the quality checks found

All 30 rating items and demographic fields are nonblank in the supplied master; nondisclosure labels still occur, so this does not establish that all demographic information is known or that the form forced answers. Optional names are supplied in 227 records (69.4%); missing comments vary by question. No exact duplicate rows were found after excluding names. Fifty-four records (16.5%) use the same category throughout; 51 use all 5s, two all 4s and one all 3s. Keep them in the primary analysis and label any exclusion as sensitivity. These checks do not prove careless responses, a halo effect or social-desirability bias.

## 3. Define measures before ranking anything

Item favourable % = count selecting 4–5 / valid item answers ×100. Unfavourable % uses 1–2; top-box uses 5. Keep Sometimes separately. Block favourable percentages pool the answers to the five items; they are not the percentage of employees given a particular engagement classification.

A block mean averages five items per record, then records. This uses equal item weights and a working equal-spacing assumption. CULTURE_MEAN averages 25 items in CRE/RES/FAI/PRI/CAM, excluding OVR; it is not an official Trust Index or a validated engagement scale. PRI3 intention to stay is inside it, so a composite–PRI3 correlation would have part–whole overlap and should not be treated as a driver result.

Across all 30 items, 84.92% of rating answers are favourable. Recognition RES4 illustrates the denominator: 237/327 favourable (72.48%), 56 Sometimes and 34 unfavourable. A 72.5% favourable share does not mean the other 27.5% are all dissatisfied. Different ranking metrics can produce different orders.

## 4. What the base ratings reveal

| Code | Survey block | Mean / 5 | Favourable answer % | Alpha |
| --- | --- | --- | --- | --- |
| PRI | Pride | 4.58 | 91.19 | 0.84 |
| OVR | Overall employee experience | 4.48 | 89.42 | 0.90 |
| CRE | Credibility | 4.35 | 84.77 | 0.88 |
| CAM | Camaraderie | 4.35 | 83.30 | 0.79 |
| RES | Respect | 4.32 | 82.63 | 0.88 |
| FAI | Fairness | 4.17 | 78.23 | 0.86 |

Pride is the highest-scoring supplied block and Fairness the lowest on the working mean. These are within-survey comparisons, not external pass/fail thresholds or certification results. Employees can feel proud and supported while asking for more consistent decisions and recognition.

### Lowest favourable shares worth examining

| Item | Question | Favourable % | Sometimes n | Unfavourable n |
| --- | --- | --- | --- | --- |
| RES4 | My efforts and contributions are appreciated and recognised | 72.48 | 56 | 34 |
| CAM5 | People here celebrate each other's successes and achievements. | 72.78 | 68 | 21 |
| FAI3 | People-related decisions are made consistently by the Leadership team without favoritism or bias. | 74.62 | 54 | 29 |
| FAI5 | I understand how decisions affecting employees are made. | 75.54 | 56 | 24 |
| FAI1 | Performance, recognition and rewards are fair and based on performance. | 76.15 | 45 | 33 |
| CRE5 | Leaders are willing to listen to employee feedback and act on it. | 79.82 | 39 | 27 |

The strengths include contribution clarity PRI2 (95.72% favourable), company pride PRI1 (92.35%) and within-team support CAM1 (91.13%). Overall growth OVR2 is also positive (90.52%); comment requests about access/progression do not erase that strength.

See [the strength/gap figure](figures/strengths_and_opportunities.png) and [all item counts](tables/item_evidence_profile.csv). The charts retain category distributions rather than hiding them behind averages.

## 5. How much further do statistical methods let us go?

Cronbach alpha is approximately 0.79–0.90 within blocks and 0.97 across all 30 items. It indicates shared variation/internal consistency under assumptions, not validity, one factor, separate dimensions or a proven halo effect. We did not automatically remove items or fit factor analysis merely because alpha is high.

Spearman correlation asks whether higher ratings on one item tend to accompany higher ratings on another. OVR2 career/learning and PRI3 intention to stay have rho ≈ 0.57. This is exploratory association, not proof that changing career provision would cause a known turnover reduction. PRI3 is intention, not observed turnover; OVR1 is five-point advocacy, not standard eNPS.

Kruskal–Wallis explores rank-distribution differences between eligible independent response groups. BY adjustment is applied to the 11 listed overlapping full/sensitivity comparisons. Tenure has the clearest signal after this adjustment (adjusted p approximately 0.028 in full and sensitivity views). This is an omnibus result, not proof of a specific pairwise difference, a cause or workforce generalisability. Department/region/name-disclosure comparisons are less conclusive after adjustment; a large p-value does not prove equality.

| Tenure | Response n | Culture mean | Growth mean OVR2 | Intention to stay PRI3 |
| --- | --- | --- | --- | --- |
| 0 - 3 | 124 | 4.30 | 4.40 | 4.41 |
| 3 - 5 | 53 | 4.21 | 4.30 | 4.25 |
| 5 - 10 | 56 | 4.38 | 4.59 | 4.61 |
| 10 - 15 | 41 | 4.70 | 4.83 | 4.90 |
| 15 & Above | 53 | 4.32 | 4.49 | 4.51 |

The 3–5-year group is descriptively lower than the other tenure groups on the culture mean; it has 53 responses. Customer Service has a comparatively low culture mean (4.09, n=51), but the department interpretation is exploratory. Do not automatically label a segment an attrition risk. Small-group scores are suppressed using a provisional n<10 rule; the focused follow-up uses groups n≥30 and suppresses counts 1–4. These rules are not guarantees of anonymity or precision.

Removing straight-liners lowers block means by approximately 0.07–0.15, while Pride remains highest and Fairness lowest. The exclusion changes the sample and does not recover a known unbiased truth. HR-priority Cramér's V is descriptive; routine chi-square p-values were withheld because all five examined tables had sparse expected counts.

## 6. What employees selected as HR's one priority

| Selected HR theme | Records | Percent |
| --- | --- | --- |
| Communication | 80 | 24.46 |
| Grievances | 64 | 19.57 |
| Development | 51 | 15.60 |
| Benefits & Facilities | 51 | 15.60 |
| R&R | 30 | 9.17 |
| Process & Policies | 20 | 6.12 |
| Approachable | 18 | 5.50 |
| Engagement | 13 | 3.98 |

This is one selected priority per record. It is not directly comparable with multi-label comment counts. For example, a person may request recognition in one comment but select communication as their single HR priority; that is not a contradiction.

## 7. From comments to contextual topics

We use applied codebook-based thematic content analysis. The assistant reads each answer in question context and stores explicit topic assignments, rather than treating keyword hits or a sentiment score as completed interpretation. The original ledger is retained, guarded by a hash of comment text/order; documented review edits are then applied before aggregating outputs.

There are 15 topic categories, with inclusion/exclusion rules. Several can apply to one answer. Response stance is separate: current strength, request/concern, mixed, no concern/no change proposed, no valued aspect, nonresponse, unclear or unresolved reference. A negative answer to the fairness-concern prompt is preserved as no concern; nothing in the preserve prompt has a different meaning. No text length or polish proves authorship or truthfulness.

After review, 1,590 of 1,892 nonblank answers receive at least one topic. That is coverage, not accuracy. Request counts below deduplicate each source record per topic across questions. Preserve counts use explicit team/organisation strengths in the preserve prompt. Both can occur for one record and topics overlap; totals do not add to 100%. The main request percentages divide by all 327 response records, not the workforce or only dissatisfied employees.

| Topic | Request records | Request % of 327 | Preserve records |
| --- | --- | --- | --- |
| Communication and decision explanations | 194 | 59.33 | 12 |
| Recognition and performance feedback | 179 | 54.74 | 4 |
| Teamwork and cross-team coordination | 176 | 53.82 | 119 |
| Support and respectful treatment | 139 | 42.51 | 77 |
| Career growth and learning | 136 | 41.59 | 18 |
| Employee voice and follow-through | 134 | 40.98 | 10 |
| Fair treatment and decision consistency | 114 | 34.86 | 3 |
| Role clarity and work processes | 91 | 27.83 | 7 |
| Workload, boundaries and flexibility | 78 | 23.85 | 6 |
| Pay, incentives and benefits | 51 | 15.60 | 9 |
| Trust, integrity and autonomy | 49 | 14.98 | 61 |
| Facilities, tools and staffing | 39 | 11.93 | 0 |
| Activities and social connection | 38 | 11.62 | 4 |
| Business identity and customer service | 10 | 3.06 | 22 |
| Work culture and belonging | 8 | 2.45 | 75 |

The highest request topics include communication/explanation, recognition/feedback and teamwork/coordination. Team/colleague-related strengths are prominent in the preserve question (119 records). Some simply identify valued teams/colleagues; do not claim all 119 explicitly describe consistent helpful behaviour. In the fairness question, 73 replies report no current concern. These different experiences remain part of the story.

### What n-grams contribute

Bigrams contain two adjacent words; trigrams three. Examples include career growth, regular feedback, knowledge sharing and work life balance. We preserve original word adjacency/negation, do not cross sentences/comments/questions, count a phrase once per record within a question, and filter prompt boilerplate/known name tokens. A minimum support of five is a readability threshold, not statistical significance. English-focused surface forms miss paraphrases and mixed-language variants. N-grams help navigate and inspect the comments; they do not independently validate themes or classify sentiment.

## 8. Deepen the fairness and cross-team findings

### Cross-team execution

Within-team support CAM1 is 298/327 favourable (91.13%); cross-team collaboration CAM2 is 269/327 (82.26%); access to other-team colleagues CAM4 is 262/327 (80.12%). The CAM1/CAM2 favourable difference is 8.87 percentage points.

The paired view keeps the same records together: 45/327 (13.76%) rate CAM1 favourably but CAM2 at 1–3; 16 show the reverse. On the original categories, 90 rate CAM1 higher, 203 the same and 34 lower. Identical-category respondents cannot fall in the discordant group, so the 45 remaining after their exclusion is not an independent robustness result.

The teamwork prompt has 53 request answers discussing roles/processes/accountability/shared goals, 124 communication, and 32 activities; categories overlap. This supports examining ownership, handover information, escalation, response expectations and backup instead of assuming an outing addresses the operational issue. We have not identified which department pair or work step causes a delay; a real workflow baseline is needed.

### Fairness of people decisions

| Item | question | favourable_n | sometimes_n | unfavourable_n | favourable_pct | mean |
| --- | --- | --- | --- | --- | --- | --- |
| FAI1 | Performance, recognition and rewards are fair and based on performance. | 249 | 45 | 33 | 76.15 | 4.07 |
| FAI2 | Employees have equal opportunities to grow and develop their careers. | 267 | 35 | 25 | 81.65 | 4.24 |
| FAI3 | People-related decisions are made consistently by the Leadership team without favoritism or bias. | 244 | 54 | 29 | 74.62 | 4.12 |
| FAI4 | I believe workload and responsibilities are distributed fairly within my team. | 272 | 36 | 19 | 83.18 | 4.31 |
| FAI5 | I understand how decisions affecting employees are made. | 247 | 56 | 24 | 75.54 | 4.09 |

Across five fairness items, 137/327 (41.90%) rate at least one at 1–3, 97 have two or more, and 16 rate all five at 1–3. Fifty-one rate both decision consistency FAI3 and understanding decisions FAI5 at 1–3. Since Sometimes is included, none of these is the prevalence of discrimination or unfair treatment.

In the fairness prompt, revised request counts are 67 career/learning, 66 recognition, 64 communication/explanation and 36 workload, with overlap. They point to several different questions: who gets opportunities, how rewards relate to contribution, whether decisions are consistent, why a decision happened and how work is allocated. Seventy-three no-concern replies prevent an overly uniform account.

The priorities overlap but are distinct: 47 of 58 records rating CAM2 at 1–3 also have a fairness item at 1–3; another 90 have a fairness item at 1–3 while CAM2 is favourable. These are descriptive cross-patterns, not a causal pathway.

### Related themes and apparent disagreements

Recognition/feedback supports fairness; role clarity/workload/backup supports execution and allocation; voice with visible action supports both. Career opportunity stays inside fairness/progression. High scores and requests can coexist: 126 of the 179 recognition/feedback request records also rate RES4 favourably. The item and the broader topic are imperfect matches, and the prompt explicitly asks for improvement. We do not diagnose hidden dissatisfaction from that combination.

Specific facilities, equipment, respectful-treatment and time-boundary accounts remain on a confidential verification track. Their presence in text can be checked, but the occurrence/severity of reported events has not been independently verified. Broad topic counts are not incident counts.

## 9. What the VOSviewer-style feature adds—and does not add

The primary map uses 1,230 topic-coded suggestion/mixed answers from 305 response records, 13 displayed topics and 34 links supported by at least ten answers. Nodes are topics, not employees. Links count topics mentioned in the same answer; different answers by one record do not by themselves create a link. A record can still contribute several comments.

Node area shows unique contributor-record support, line width shows answer co-mentions, and colors are exploratory custom communities. Association strength divides pair frequency by the product of topic frequencies; the displayed scaled ratio is not a p-value. The force-directed layout and greedy weighted-modularity grouping are local implementations, not native VOSviewer algorithms. Isolates are placed separately; axes and distance from isolated topics have no substantive meaning.

Prompt sensitivity matters: communication/teamwork co-occurs in 98 answers from 93 records, with 85 from the teamwork prompt. Fairness/career co-occurs in 46 answers from 43 records, with 41 from the fairness prompt; excluding it leaves 5. The map cannot serve as independent confirmation of the same prompted coding used to construct it.

The [interactive map](network/topic_network.html) provides search, topic focus, threshold filtering, zoom/pan, question-exclusion views, details and SVG export. Static [PNG](figures/topic_cooccurrence_network.png) and [SVG](figures/topic_cooccurrence_network.svg), aggregate JSON and local-import map/network files are supplied. No raw comments or names are in the network; nothing was uploaded. Parameter sensitivity is in the notebook and exported tables.

## 10. Review findings and changes

A second reading by the same assistant covers 568 unique comments: every initial flag and the specified core cohorts. All 104 initial flags were reread; 53 coding/status decisions changed. Original text, original assignments, revised assignments and reasons remain traceable in the notebook. This is not a second person or a blind review.

| Topic | Requests before | Requests after | Preserve before | Preserve after |
| --- | --- | --- | --- | --- |
| Career growth and learning | 143 | 136 | 21 | 18 |
| Fair treatment and decision consistency | 113 | 114 | 3 | 3 |
| Support and respectful treatment | 138 | 139 | 77 | 77 |
| Pay, incentives and benefits | 51 | 51 | 10 | 9 |

The main corrections remove inferred career development from unspecified opportunities, distinguish no-information/declined answers from ambiguous content, code an explicit short respect request, and avoid forcing unclear provision/retention wording into a particular topic. A mixed answer can preserve something current while proposing improvement.

75 cases still need clarification/context confirmation (ambiguous words, mixed-language interpretation or references); those cases were not simply skipped. Independent human/native-speaker validation is not performed, and no coding-accuracy, saturation or inter-rater reliability statistic is reported. The original five-theme direction, paired rating findings, fairness breadth and 73 no-concern replies remain intact. All major numerical claims are recomputed in the finding-verification register.

## 11. Proposed implementation pathway: from evidence to action

Day 0 is organisational approval/start, not the student deadline. Owners below are proposed roles and must be named by the organisation. Start with one workflow and a defined set of roles; use the first 14 days for the pilot baseline, scope and capacity decisions. This makes the plan feasible and measurable without claiming a survey correlation guarantees an intervention effect.

| action_id | workstream | timing_from_approval | proposed_accountable_owner | action | proposed_standard_or_decision_gate |
| --- | --- | --- | --- | --- | --- |
| G0 | Governance and scope | Days 0–7 | HR lead + executive sponsor | Name an accountable sponsor, choose one cross-functional workflow and pilot roles, confirm resources and employee communication | Baseline and capacity decision by Day 7 |
| T-A | Cross-team execution | Days 0–14 | Operations/functional head | Map one real handover path, required information, receiving owner, urgency rules, escalation and rework; collect a baseline | Agree workflow-specific response expectations by Day 14 |
| T-B | Cross-team execution | Days 15–30 | Operations/functional head | Pilot a simple handover checklist, receiving acknowledgement, shared status and escalation route | Proposed standard: 100% of in-scope handover types documented by Day 30 |
| T-C | Cross-team execution | Days 31–60 | Operations/functional head | Review delayed/reworked handovers weekly, fix the recurring obstacle and check that tracking is not adding excessive admin | Proposed pilot standard: ≥95% required-field completeness; efficiency target agreed from the Day-14 baseline |
| P1-A | Fairness of people decisions | Days 0–14 | HR head | Review existing appraisal, progression and reward criteria against how decisions are explained; listen to contrasting employee experiences | Agree what can be clarified now and what requires policy review by Day 14 |
| P1-B | Fairness of people decisions | Days 15–30 | HR head | Publish understandable criteria for pilot roles, brief eligible employees and state how to seek clarification or review | Proposed standard: criteria/explanation available for 100% of pilot roles by Day 30 |
| P1-C | Fairness of people decisions | Days 31–60 | HR head | Review a defined set of pilot decisions for documented criteria, explanation and consistent application; correct verified gaps | Proposed standard: every reviewed decision has a documented reason and identified owner; report exceptions openly in aggregate |
| P1-R | Recognition and feedback | Days 15–60 | Pilot functional managers | Offer each pilot employee a specific feedback conversation and explain non-monetary recognition criteria; review access across roles | Proposed standard: every eligible pilot employee offered a feedback conversation each 30-day cycle |
| S2 | Role clarity, workload and backup | Days 0–30; review to Day 60 | Pilot functional head | Document critical task owners and backup, priorities, leave coverage and legitimate escalation needs outside normal hours | Proposed standard: 100% of agreed critical tasks have primary, backup and escalation owners by Day 30 |
| P2 | Voice and visible follow-through | Days 0–30; ongoing | HR lead | Create a simple concern/action log, acknowledge normal concerns, assign an owner and update employees on progress and closure | Proposed normal-concern standards: acknowledge within 2 business days; owner and next-update date within 5; sensitive/urgent matters follow existing routes |
| V1 | Verification of specific accounts | Days 0–7; then case-dependent | HR lead / Administration or IT head by issue | Confidentially verify facilities/equipment and respectful-treatment/time-boundary accounts, triage confirmed issues and route them appropriately | Initial triage in the first week; remediation dates depend on verified urgency, scope and resources |
| G1 | Pilot learning review | Day 30 | Executive sponsor | Check pilot readiness, process coverage, workload burden and unresolved verification issues | Proceed only with usable baseline, assigned owners and feasible operating standards |
| G2 | Experience and process review | Days 60–90 | HR lead + executive sponsor | Repeat the selected exact questions, report valid n/category shares and respondent composition, compare operational measures and listen to examples of actual change | Set outcome targets by Day 14; assess at Days 60/90; decide scale, adapt or stop at Day 90 |

See [the compact implementation timeline](figures/implementation_roadmap.png).

### How success will be measured

Distinguish implementation from experience. A completed checklist or published criterion is an output; better handovers or improved perceptions are outcomes. Both matter. The survey reference values describe the current response pool; collect a comparable pilot baseline instead of applying the whole-company sample value to any selected group.

**Experience outcomes and strengths guardrails:** the common formula is favourable answers (4–5) / valid answers ×100; retain Sometimes, unfavourable shares and n. Numerical experience targets are agreed from the pilot baseline at Day 14, with follow-up at Days 60/90.

| kpi_id | measure | source_item_or_system | current_reference_baseline |
| --- | --- | --- | --- |
| O1 | Cross-team collaboration | CAM2 | 269/327 = 82.26% in the supplied response pool |
| O2 | Access to colleagues in other teams | CAM4 | 262/327 = 80.12% in the supplied response pool |
| O3 | Consistency of people decisions | FAI3 | 244/327 = 74.62% in the supplied response pool |
| O4 | Understanding people decisions | FAI5 | 247/327 = 75.54% in the supplied response pool |
| O5 | Fair reward/performance decisions | FAI1 | 249/327 = 76.15% in the supplied response pool |
| O6 | Recognition of contributions | RES4 | 237/327 = 72.48% in the supplied response pool |
| O7 | Celebrating achievements | CAM5 | 238/327 = 72.78% in the supplied response pool |
| O8 | Workload fairness | FAI4 | 272/327 = 83.18% in the supplied response pool |
| O9 | Listening and action on employee feedback | CRE5 | 261/327 = 79.82% in the supplied response pool |
| G-Pride | Pride to preserve | PRI1 | 302/327 = 92.35% in the supplied response pool |
| G-Support | Within-team support to preserve | CAM1 | 298/327 = 91.13% in the supplied response pool |

**Operational process measures:** these have no current survey baseline. Establish scope/denominators in the first 14 days and use the following explicitly proposed standards.

| kpi_id | measure | definition_and_denominator | proposed_target_or_target_setting_rule |
| --- | --- | --- | --- |
| P-Complete | Handover completeness | In-scope handovers with all agreed required fields / all logged in-scope handovers ×100 | Proposed pilot standard ≥95% by Day 60; revise if the baseline shows a different bottleneck |
| P-Time | Handover timeliness | Handovers completed within the agreed workflow/urgency-specific expectation / eligible logged handovers ×100 | Define the expectation and improvement target after the first 14-day log; no arbitrary universal shipping deadline |
| P-Criteria | Criteria access | Pilot roles with accessible current criteria and a review route / all agreed pilot roles ×100 | Proposed standard 100% by Day 30 |
| P-Reasons | Decision explanation coverage | Reviewed pilot decisions with documented criterion-based reason and owner / all decisions in the agreed review set ×100 | Proposed standard 100%; report and resolve exceptions rather than equating documentation with fairness |
| P-Feedback | Feedback access | Eligible pilot employees offered a feedback conversation / all eligible pilot employees ×100 | Proposed standard 100% offered each 30-day cycle; track completion and voluntary declines separately |
| P-Backup | Critical-task backup coverage | Agreed critical tasks with primary, backup and escalation owners / all agreed critical tasks ×100 | Proposed standard 100% by Day 30 |
| P-Ack | Concern acknowledgement | Normal concerns acknowledged within 2 business days / all eligible normal concerns ×100 | Proposed operating expectation: acknowledge each normal concern within 2 business days; distinguish exceptions/urgent routes |
| P-Owner | Concern ownership and next update | Normal concerns with owner and next-update date within 5 business days / all eligible normal concerns ×100 | Proposed operating expectation: owner and update date within 5 business days; not a resolution promise |

Proposed process standards (such as all pilot roles having criteria access or ≥95% handover-field completeness) are explicit pilot design choices, not values inferred from this survey or commitments already approved. Normal concern acknowledgement and ownership standards do not promise resolution in five days. Workflow urgency rules need operational input; urgent/sensitive matters retain existing routes.

Numerical improvement targets for experience outcomes are agreed at Day 14 using the pilot baseline, population, uncertainty and resources. Do not invent a five-point increase, turnover saving or ROI merely to make the roadmap look precise. Maintain a small main panel, with the full KPI dictionary as reference. Repeat exact question wording/options, show valid n, response participation and composition, and retain Sometimes separately.

| gate | required_decision | interpretation_rule |
| --- | --- | --- |
| Day 0 | Approve scope, name accountable people, confirm capacity and communication | Pilot cannot start merely because this report exists |
| Day 14 | Approve baseline, denominators, exact outcome questions, workflow expectations and numerical outcome targets | Targets are chosen with context, not fabricated from correlations or qualitative counts |
| Day 30 | Check process readiness and owner coverage; adapt the pilot if burden or gaps are excessive | Record reasons for continue/adapt decisions |
| Day 60 | Review operational progress and employee evidence; resolve observed implementation gaps | Retain contrary and no-concern accounts; report nonresponse and composition |
| Day 90 | Decide scale, adapt or stop using process, experience, resource and guardrail evidence | Do not attribute all change to the pilot without a defensible comparison |

A relevant comparison or staged rollout may help interpretation if feasible. Before/after differences alone cannot isolate the pilot's effect. At Day 90 decide scale, adapt or stop using process evidence, employee experience, resource use and the pride/team-support guardrails together.

## 12. Tools and why we chose the methods

Python and Jupyter organise reproducible analysis in one notebook. pandas/openpyxl load and reshape Excel data; NumPy performs numerical calculations; SciPy supports rank tests, FDR adjustment, correlations and network optimisation; Matplotlib/seaborn draw the charts. Standard-library helpers manage hashing, counts and exports. Plain offline HTML/SVG/JavaScript implements the network controls. Dependencies are pinned through uv.lock. No additional model API, automatic sentiment service, scikit-learn model or native VOSviewer execution is used.

| Method | Question it answers | Choice made | Limit |
| --- | --- | --- | --- |
| Workbook/codebook audit | Identify source rows, question wording, labels and missingness | Use the supplied master and retain a documented transformation trail | Does not verify unique employee identities or why raw/master counts differ |
| Counts, distributions and favourable shares | Describe the base before aggregates | Primary reporting evidence; valid-answer denominators always explicit | Favourable is 4–5; Sometimes is not neutral; a percentage is not a diagnosis |
| Working means and block summaries | Summarise experience beside the distribution | Equal category spacing and item weights are stated assumptions | Custom CULTURE_MEAN is descriptive, not a validated/official engagement index |
| Cronbach alpha / item–total checks | Inspect item coherence within the supplied blocks | Diagnostic, not automatic item removal | Does not establish one factor, validity, distinct dimensions or a halo effect |
| Spearman correlations | Explore which ratings move together | Rank association suits the ordered coding and exploratory question | No causal/independent-driver interpretation; avoid part–whole overlap |
| Kruskal–Wallis and BY adjustment | Explore relevant group differences | 11 overlapping full/sensitivity comparisons adjusted together | Assumptions remain; omnibus differences do not identify pairwise causes |
| Response-style sensitivity | Check dependence on identical-category respondents | Keep all records primary; show labelled exclusions | Exclusion is not a correction to a known truth; paired discordance cannot include straight-liners |
| HR counts and Cramér's V | Describe the one HR priority selected | Recompute from master; inspect expected cells before inference | Sparse-table asymptotic p-values withheld; no unsupported department-effect claim |
| Codebook-based thematic content analysis | Understand specific strengths, concerns and suggested changes | 15 explicit overlapping topic labels plus separate stance/status; original and revised ledger retained | AI-assisted and interpretive; not independently human-validated or reflexive TA |
| Exact bigrams/trigrams | Find recurring phrases to navigate comments | Original token adjacency, negation and unique-record support; prompt/name filtering | Not a theme/sentiment classifier or proof of independent experiences; English-focused |
| Paired item / rating–comment profiles | Connect what the same records say in different forms | Describe distributions, matches and differences with clear denominators | Positive ratings and improvement requests need not contradict each other |
| VOSviewer-inspired topic network | Explore same-answer topic connections | Full-count pairs, association normalization, custom layout/grouping and prompt sensitivity | Not native VOSviewer algorithms, a causal map, an employee network or independent validation |
| Assistant re-review / source verification | Tighten coding boundaries and check important claims | 568 comments reread; 53 changes; calculated facts recomputed; original decisions preserved | No inter-rater reliability, coding-accuracy estimate or confirmation that accounts occurred |
| 0–90-day pilot roadmap / KPI dictionary | Turn findings into owned, measurable proposals | Separate observed survey references from unknown operational baselines; define decision gates | Standards are proposals; approval, capacity and numerical outcome targets are not invented |

Fuzzy analysis was assessed rather than added for appearance. A frequency-based equal-weight construction scored 1–5 exactly equals the ordinary mean for these complete data; that calculation adds no information. A substantive calibrated fuzzy model, factor model, employee clustering or causal/attrition model was not justified by the current decision need and available outcomes. This is not a claim that those methods are universally invalid.

Method references used for definitions and fit include [CIPD people analytics](https://www.cipd.org/uk/knowledge/guides/analytics-practitioner-guide/), [Civil Service survey methodology](https://www.gov.uk/government/publications/civil-service-people-survey-2025-results/quality-and-methodology-information-for-the-civil-service-people-survey-2025), [SciPy BY adjustment](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.false_discovery_control.html), [Framework Method](https://pmc.ncbi.nlm.nih.gov/articles/PMC3848812/), [Braun & Clarke's method distinctions](https://www.thematicanalysis.net/understanding-ta/), [NLTK phrase documentation](https://www.nltk.org/howto/collocations.html) and [official VOSviewer conventions](https://app.vosviewer.com/docs/user-interface/main-panel/). Practitioner/forum material informed practical questions, not statistical validation. The notebook retains the fuller research trail.

## 13. Claims we can make, and claims to avoid

We can describe how these records answered, identify relative strengths/gaps, show within-record and group patterns, report contextual coded topics with limitations, and propose evidence-linked improvements. We cannot claim workforce representativeness, proven causes of engagement/turnover, official Trust Index/eNPS results, independent qualitative validation, verified misconduct, incident prevalence, automatic department blame or guaranteed intervention effects/ROI.

## 14. Output map and next work

The [notebook](../notebooks/00_data_understanding_eda.ipynb) is the analytical source. The [short final synthesis](FINAL_ANALYSIS_SYNTHESIS.md) is a concise companion. The [roadmap CSV](tables/implementation_roadmap_0_90_days.csv), [KPI dictionary](tables/roadmap_kpi_dictionary.csv), [decision gates](tables/roadmap_decision_gates.csv), [review before/after table](tables/coding_review_before_after.csv) and [finding-verification register](tables/finding_verification_register.csv) support review. Existing figures and tables are regenerated from current assignments, including the network.

The requested assistant review and practical roadmap draft are complete. Genuine independent review, clarification of ambiguous cases, verification of specific accounts and organisational approval remain honestly labelled. The executive PowerPoint and dashboard now follow the Step 7 priority order (section 15). No additional statistical method is required unless it resolves a specific remaining decision question.

<!-- STEP7_PRIORITISATION -->

## 15. Prioritisation check (Step 7, 30 October 2026)

Relative weights on 19 actionable items explain 65% of the variation in an outcome built from recommend, satisfaction and intention to stay (pride and belonging excluded as near-outcomes). Fairness carries 31% of the dimension-level link. Fix-first items (above-median link, below-median score): CRE5, FAI2, CAM2, FAI1, FAI3, FAI5. The ranking is unchanged without straight-liners (ρ = 1.00); among the 100 anonymous respondents it shifts (ρ = 0.59): recognition rises and cross-team drops.

| theme | Score | Outcome link | HR choice | 'One change' | Strong (of 4) |
| --- | --- | --- | --- | --- | --- |
| Fair, explainable people decisions & growth | Strong | Strong | Strong | Strong | 4 |
| Leaders listen and visibly act | Strong | Strong | Strong | Strong | 4 |
| Recognition of contributions | Strong | Weak | Medium | Strong | 2 |
| Cross-team collaboration | Medium | Strong | — | Weak | 1 |
| Support when problems arise | Weak | Weak | Strong | Medium | 1 |
| Workload & role clarity | Weak | Medium | Weak | Strong | 1 |
| Pay, benefits & facilities | — | — | Strong | Medium | 1 |

**Revised order:** Priority 1 is fair, explainable people decisions and growth, with recognition inside it. Priority 2 is leaders listening and visibly acting. Cross-team handovers become a targeted pilot starting in Customer Service. Pay, benefits and facilities go to the annual review.

**Named vs anonymous:** 91.6% of named and 78.0% of anonymous respondents intend to stay 3–5 years. This is consistent with, not proof of, more guarded answers when named; report both and drop the name field next time.

Associations are not causes. Grading thresholds were fixed before reading the result. Tables: priority_matrix.csv, priority_triangulation.csv, hr_priority_counts.csv, one_change_topics.csv, named_vs_anonymous.csv, group_hotspots.csv, driver_model_summary.csv.
