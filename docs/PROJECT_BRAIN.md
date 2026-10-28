# Safewater Lines — working project brain

Last updated: 28 October 2026.

## Current status

Step 1 (analytical foundation, method research and selection rules) is now implemented after the EDA summary in `notebooks/00_data_understanding_eda.ipynb`. Keep all analytical work in that notebook and maintain its methodology reference as the final Markdown cell. Build the executive PowerPoint after the evidence, findings and proposed roadmap are complete.

The notebook now records the organisational question map, base-data checks, metric definitions, relevant HR concepts, research sources (including practitioner discussion), and used/planned/conditional methods. The existing EDA was streamlined and unsupported interpretations were corrected. Names remain excluded from processed data. The custom `TRUST_INDEX` column is now named `CULTURE_MEAN`; it is a descriptive 25-item summary, not an official or validated Trust Index.

Fuzzy analysis was explicitly considered. An executed check demonstrates that an equal-weight, response-frequency evaluation scored 1–5 exactly reproduces the ordinary mean for these complete data. This specific construction adds no information. A substantive calibrated fuzzy model remains conditional on a decision need, justified memberships/weights and sensitivity checks; no such model has been completed.

Read this file and [PROJECT_BRIEF.md](PROJECT_BRIEF.md) before extending the analysis. This is our shared record of purpose, principles, decisions, questions, and next steps. Update it as evidence changes; distinguish organisation requirements from our proposals.

## What we are trying to achieve

Help Safewater Lines understand the employee experience, identify strengths to preserve and concerns to address, and choose practical improvements it can measure.

Each eventual recommendation should connect:

**Business question → evidence → interpretation → proposed action → owner → measure of success.**

A compelling story must follow the evidence. Do not decide the story first and select results to fit it.

## User's working instructions

- Work step by step. First document the brief and approach; research methods next.
- Start from the base: understand the survey, the population, individual questions, response distributions, denominators, and basic measures before combining scores or fitting models.
- Research how people approach people analytics using the web, forums, practitioner platforms, and relevant research.
- Choose methods because their assumptions and purpose fit this problem. Popularity is not a justification.
- Avoid combining methods or interpretations that contradict one another. Explain any different assumptions or questions before using different approaches together.
- Learn and explain relevant people analytics and HR terms, principles, and philosophies where they help us reason or make decisions.
- Keep the organisational objective central; technical complexity is not a deliverable by itself.
- Keep the analysis in one notebook, remove redundant or unsupported material, and maintain a methodology table at the end. Produce the PowerPoint after completing the analysis and findings.

## What currently exists

- `notebooks/00_data_understanding_eda.ipynb`: an existing exploratory notebook, including cleaning, scores, reliability, relationships, segment comparisons, and preliminary interpretations.
- `data/raw/Your Voice- Responses 21 OCT - FINAL.xlsx`: source workbook.
- `data/processed/survey_clean.csv` and `data/processed/codebook.csv`: existing processed outputs.
- The README and notebook identify `SWL - MASTERDATA` as the analysis source and report 327 responses, 30 rating items, six open-ended questions, and one HR-priority question.
- The notebook groups rating items into five culture dimensions plus an Overall Employee Experience block. These are survey labels; statistical distinctness has not been established merely by naming the groups.

These are starting materials. Existing calculations, interpretations, and cleaning decisions still need review against the brief and our method choices. Do not treat the current notebook as a validated final analysis.

## Work sequence

### 1. Establish the brief and approach — completed preparation

Record the assignment, decision principles, known limitations, and research questions. Do not add new statistical methods during this step.

### 2. Research and select methods — foundation completed, extend as needed

Research practical people analytics workflows, employee survey measurement, qualitative analysis, and translating findings into interventions.

Use primary research and original technical guidance to substantiate methodological claims. Use forums and practitioner discussions to discover implementation problems, alternative approaches, and lessons from practice; trace factual claims to stronger evidence before adopting them.

For each candidate method, record:

| Field | What we need to establish |
|---|---|
| Question | Which organisational question does it answer? |
| Inputs | What variables and data structure does it require? |
| Assumptions | What must hold, and can we assess it here? |
| Suitability | Does it fit our sample, item types, missingness, and group sizes? |
| Interpretation | What would its result mean to HR or business leaders? |
| Limits | What claims would it not support? |
| Alternatives | Is there a simpler, clearer way to answer the question? |
| Decision | Adopt, defer, or reject, with reasons and source links |

The notebook records current method decisions. Distributions, explicit denominators, descriptive working means, exploratory rank associations, group comparisons with a joint BY adjustment, and response-style sensitivity are used. Factor analysis, regression and calibrated fuzzy models remain conditional. Codebook-based comment analysis is planned and must not be labelled completed or confused with reflexive thematic analysis.

### 3. Audit the base data and measures

- Establish who was eligible, who responded, the survey period, and how responses were collected, where that information is available.
- Distinguish respondent count from response rate. A response rate requires an eligible-employee denominator.
- Review exact question wording, response options, language equivalence, missingness, duplicates, and cleaning choices.
- Examine individual item counts and distributions before aggregate indices. Define the denominator for every percentage.
- Establish what each proposed score represents and whether aggregation is justified. Distinguish individual responses from group summaries.
- Check sample sizes and representation before comparing employee groups. If workforce composition is unavailable, state that limitation.
- Review repetitive answers without assuming they are invalid. Any exclusion needs a documented reason and, where useful, a sensitivity comparison.
- Keep raw data unchanged and document transformations. Remove names from analytical exports; review comments and small groups for potential identification before presentation.

### 4. Build and test the organisational story

- Identify strengths worth preserving as well as improvement areas.
- Explore variation across relevant groups, considering uncertainty and practical importance.
- Read comments in context and build a transparent theme-coding approach. Check automated classifications against actual comments if automation is used.
- Connect quantitative patterns with qualitative themes; investigate disagreements instead of hiding them.
- Separate observations, possible explanations, and claims requiring additional evidence.
- Treat correlations as associations. A cross-sectional survey alone does not establish what causes engagement, retention, or performance.
- Do not equate intention to stay with observed employee turnover.
- Do not interpret high reliability as proof of validity or distinct dimensions.
- A named-versus-unnamed score difference may have several explanations; it does not by itself prove social-desirability bias or establish that scores are an upper bound.
- Do not label results good or bad using invented thresholds or an unverified external benchmark.
- If significance testing is useful, justify it and account for the number of comparisons. A p-value alone does not establish business importance.

### 5. Translate evidence into a practical pathway

For each priority, specify the evidence, affected employee experience, proposed intervention, accountable owner, timing, feasibility, baseline, success measure, and review point.

Prioritise using explicit reasons such as employee impact, extent of the concern, strength of evidence, feasibility, and organisational relevance. Any numerical weighting must be justified. Set proposed targets with management input and observed baselines; do not invent targets to make the roadmap look precise.

Present interventions as proposals to test and learn from. Separate implementation measures, such as actions completed, from outcome measures, such as whether employee perceptions improve.

### 6. Produce the integrated executive output

Create a concise evidence-backed narrative, legible visuals, prioritised recommendations, and an actionable roadmap. Include enough methodological explanation and limitations for the audience to judge the findings.

## Terms and philosophies to understand during research

This is a learning agenda, not a list of settled definitions or chosen measures.

| Topic | Why it matters here |
|---|---|
| People analytics and evidence-based HR | Combining employee data, research, organisational context, and professional judgement |
| Employee voice and listening | Understanding whether employees can speak, are heard, and see follow-through |
| Engagement, satisfaction, commitment, and employee experience | Avoiding interchangeable labels for different concepts |
| Organisational culture and climate | Understanding what a one-time perception survey can tell us about each |
| Organisational justice | Distinguishing fairness of outcomes, procedures, treatment, and explanations |
| Psychological safety and trust | Understanding related concepts without assuming the survey directly measures all of them |
| Measurement validity and reliability | Checking whether a score measures the intended concept and does so consistently |
| Likert items and composite scales | Choosing defensible summaries and analyses for individual items versus aggregates |
| Representation, nonresponse, and response bias | Understanding whose experience is visible and what remains unknown |
| Practical significance, uncertainty, and causal inference | Separating meaningful differences from statistical signals and causal claims |
| Qualitative coding and mixed-method integration | Using comments systematically and connecting them with survey patterns |
| Action planning, theory of change, and evaluation | Explaining why an intervention might help and how improvement will be assessed |

Add sourced definitions and relevant frameworks during research. Do not impose a famous HR framework without showing its fit to these questions and data.

## Open questions

- What is the eligible workforce size and its composition by major employee groups?
- When and how was the survey administered, and how was confidentiality communicated?
- Is there a prior survey, a comparable benchmark, or relevant HR data available?
- Which business constraints, existing initiatives, and owners should inform recommendations?
- What presentation duration and submission format are expected?

These questions do not prevent descriptive analysis. Record unavailable context and limit conclusions accordingly.

## Decision log

| Date | Decision | Reason |
|---|---|---|
| 28 October 2026 | Use the organisation's supplied brief as the project objective | The assignment requires a story and measurable organisational pathway |
| 28 October 2026 | Document first, then research methods, then review analysis from the base | Explicit user instruction |
| 28 October 2026 | Treat existing notebook findings as provisional | Calculations and claims need review before informing recommendations |
| 28 October 2026 | No additional analytical method selected | Selection must follow the question, evidence, assumptions, and available data |
| 28 October 2026 | Implement Step 1 in the existing notebook and keep the methodology table last | Explicit user instruction to work in one notebook |
| 28 October 2026 | Rename the custom summary to CULTURE_MEAN; correct causal/bias and eNPS claims | Prevent unvalidated measurement and interpretation claims |
| 28 October 2026 | Use a joint BY adjustment for the 11 listed exploratory full/sensitivity comparisons; withhold sparse HR-table p-values | Overlapping tests and sparse expected counts need explicit handling |
| 28 October 2026 | Do not report an equivalent frequency-weighted mean as an extra fuzzy finding | Executed equivalence check shows no additional information; other fuzzy models remain conditional |

## Immediate next step

Use the reviewed EDA to build a denominator-aware strength/gap profile, examine relevant variations, and begin contextual codebook-based analysis of the six comment questions. Integrate comments with rating patterns and selected HR priorities before choosing interventions. Revisit advanced or fuzzy methods only where they answer an unresolved question better than the baseline. The PowerPoint follows the completed findings and roadmap.
