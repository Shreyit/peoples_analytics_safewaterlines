"""Build the methodology sheet (A4 PDF) for Q&A on the 20-minute pitch.

Every figure is read from the notebook's exported tables or the processed survey,
so the sheet stays consistent with the decks. Layout is done by WeasyPrint (CLI).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import markdown
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TABLES = ROOT / "reports/tables"
BUILD = HERE / "build"
BUILD.mkdir(exist_ok=True)
PDF = HERE / "output/Safewater_Lines_Methodology_Sheet.pdf"

df = pd.read_csv(ROOT / "data/processed/survey_clean.csv")
pm = pd.read_csv(TABLES / "priority_matrix.csv", index_col=0)
model = pd.read_csv(TABLES / "driver_model_summary.csv", index_col=0)["value"]
tri = pd.read_csv(TABLES / "priority_triangulation.csv", index_col=0)
nva = pd.read_csv(TABLES / "named_vs_anonymous.csv", index_col=0)
hr = pd.read_csv(TABLES / "hr_priority_counts.csv", index_col=0)
cov = pd.read_csv(TABLES / "qualitative_coding_coverage.csv", index_col=0)
review = pd.read_csv(TABLES / "assistant_review_coverage.csv", index_col=0)
codebook = pd.read_csv(TABLES / "qualitative_topic_codebook.csv")
edges = pd.read_csv(TABLES / "topic_network_edges.csv").set_index(["a", "b"])

ITEMS = [c for c in df.columns if c[:3] in ("CRE", "RES", "FAI", "PRI", "CAM", "OVR") and c[-1].isdigit()]
assert len(ITEMS) == 30 and len(df) == 327
avg_fav = (df[ITEMS] >= 4).to_numpy().mean() * 100
comments = int(cov["nonblank_n"].sum())
straight = int(df["straightliner"].sum())
mf, mi = pm["fav_pct"].median(), pm["importance_pct"].median()
fix_first = pm[pm["quadrant"].eq("Fix first")].sort_values("importance_pct", ascending=False)
rho = pm[["importance_pct", "imp_no_straightliners", "imp_anonymous_only"]].corr(method="spearman")
named = df["gave_name"]


def fisher(col):
    a = int((df.loc[named, col] >= 4).sum()); c = int((df.loc[~named, col] >= 4).sum())
    return stats.fisher_exact([[a, named.sum() - a], [c, (~named).sum() - c]]).pvalue


p_stay, p_rec = fisher("PRI3"), fisher("OVR1")
p_culture = stats.mannwhitneyu(df.loc[named, "CULTURE_MEAN"], df.loc[~named, "CULTURE_MEAN"]).pvalue
ct, fd = edges.loc[("c", "t")], edges.loc[("d", "f")]

NAMES = {"CRE5": "Leaders act on feedback", "FAI2": "Equal growth opportunities", "CAM2": "Teams work well together",
         "FAI1": "Fair rewards and recognition", "FAI3": "Consistent decisions", "FAI5": "Understand how decisions are made"}
fix_rows = "\n".join(f"| {c} | {NAMES[c]} | {r.fav_pct:.1f}% | {r.importance_pct:.1f}% ({r.imp_ci_low:.1f}–{r.imp_ci_high:.1f}) | {r.p_top5:.2f} |"
                     for c, r in fix_first.iterrows())
tri_rows = "\n".join(f"| {t} | {r.score} | {r.outcome_link} | {r.hr_choice} | {r.one_change} | {int(r.strong_lenses)} |"
                     for t, r in tri.iterrows())

TEXT = f"""
<p class="kicker">SAFEWATER LINES / YOUR VOICE SURVEY</p>

# Methodology sheet

<p class="lede">Team copy for questions on the 20-minute pitch. Each section gives the plain answer first, then the detail. All figures come from the analysis notebook (<code>00_data_understanding_eda.ipynb</code>) and its exported tables.</p>

## At a glance

| Pitch slide | What it claims | Method | Key number |
|---|---|---|---|
| 2 | What we analysed | Cleaned survey export | 327 responses, 30 rated questions, {comments:,} comments |
| 3–4 | Strengths and gaps | Favourable share (answers 4–5) | Average question {avg_fav:.0f}% positive |
| 5 | Anonymous answers are less positive | Named vs anonymous comparison, Fisher exact test | Stay 3–5 yrs: {nva.loc['Named','stay_3_5_yrs_fav']:.0f}% vs {nva.loc['Anonymous','stay_3_5_yrs_fav']:.0f}% (p = {p_stay:.3f}) |
| 6 | What links most to staying and recommending | Relative-weights regression, 500 bootstraps | R² = {model['actionable_r2']:.2f}; fairness {model['dim_FAI']:.0f}% of the link |
| 7 | Comments form three groups | Topic co-occurrence map (VOSviewer-style) | {ct.comments} communication–teamwork co-mentions |
| 8 | Two themes pass four checks | Triangulation with pre-set pass marks | 2 of 7 themes strong on all four |
| 10, 13 | What people asked HR for | Forced single choice, counts | Listening: {int(hr.iloc[0].respondents)} people ({hr.iloc[0].pct:.0f}%) |
| 11 | Start in Customer Service | Favourable share by group (n ≥ 10) | Lowest group on fair decisions, recognition and plan to stay |

## 1. Data and preparation

- **Source:** the survey workbook with responses to 21 October. **327 response records**, 30 rated questions on a 1–5 scale (Credibility, Respect, Fairness, Pride, Camaraderie, Overall), 6 open questions, 1 forced-choice HR question and 5 profile fields.
- **Comments:** {comments:,} non-blank answers across the 6 open questions, in English, Hindi, Marathi, Tamil and Malayalam.
- **Cleaning:** answer labels mapped to 1–5; profile fields standardised; departments under 10 people grouped as “Other”. **Names were removed** from the analysis file; only a yes/no flag for “gave a name” was kept.
- **Straight-liners:** {straight} people ({straight / 327:.1%}) gave the identical answer to all 30 questions. They are kept in the headline results and every key result is re-checked without them.
- **Not available:** total headcount (so no response rate) and any employee ID linking to HR records.

## 2. How scores are read

- **Positive (favourable) = 4 or 5**, “Usually” or “Almost always”. 3 (“Sometimes”) is *not* counted as positive, and 1–3 is not called “unfavourable”.
- This is the standard way large employee surveys report results (for example, the UK Civil Service People Survey). It is easier to explain than averages and does not assume equal gaps between answer options.
- The average question is {avg_fav:.0f}% positive. The five lowest (recognition, celebrating success, consistent decisions, understanding decisions, fair rewards) sit around 72–76%.

## 3. “Link to staying”: relative-weights analysis (slide 6)

**Plain answer:** we measured how strongly each question moves together with whether people want to stay, would recommend the company and are satisfied, then split the credit fairly between questions that overlap.

1. **Outcome per person** = average of three answers: *I would recommend this organization as a great place to work* (OVR1), *I am satisfied with the overall employee experience* (OVR4), *I see myself continuing to work here over the next 3–5 years* (PRI3).
2. **Explanatory questions:** the 19 questions leaders can act on, from Credibility, Respect, Fairness and Camaraderie. Pride and belonging are excluded because they are almost the outcome itself.
3. **Fit:** a linear regression of the outcome on the 19 questions explains **R² = {model['actionable_r2']:.2f}** of the variation ({model['r2_no_straightliners']:.2f} without straight-liners).
4. **Fair split (Johnson’s relative weights, 2000):** the questions are converted into uncorrelated versions of themselves, the regression is run on those, and the explained variation is mapped back to the original questions. Each question’s share is rescaled to sum to 100%. This avoids ordinary regression arbitrarily giving the credit to one of several overlapping questions.
5. **Uncertainty:** 500 bootstrap resamples of the 327 people give a 95% range for each share and the probability that a question ranks in the top five (P(top 5)).
6. **By survey block** (each block averaged into one score, same method): Fairness {model['dim_FAI']:.0f}%, Respect {model['dim_RES']:.0f}%, Credibility {model['dim_CRE']:.0f}%, Camaraderie {model['dim_CAM']:.0f}%.

**Robustness:** the ranking is essentially unchanged without straight-liners (Spearman ρ = {rho.iloc[0, 1]:.2f}). Among the 100 anonymous respondents it shifts (ρ = {rho.iloc[0, 2]:.2f}): recognition rises into the top tier and cross-team work drops, which is why recognition sits inside Priority 1.

## 4. The priority chart (slide 6)

- **Horizontal:** survey score (% positive). **Vertical:** link share from section 3.
- **Lines are the medians** of the 19 questions: {mf:.1f}% positive and {mi:.1f}% link. If all questions mattered equally each would carry 100 / 19 = 5.3%.
- **Fix first** = below-median score *and* at-or-above-median link. **Protect** = high link, high score. **Monitor** = low score, lower link. **Maintain** = high score, lower link.

| Code | Question (short) | Positive | Link share (95% range) | P(top 5) |
|---|---|---|---|---|
{fix_rows}

Ranges overlap, so the chart is read as tiers, not an exact order. Two questions sit on a median line: *Understand decisions* (link {pm.loc['FAI5','importance_pct']:.2f}%, counted as fix first) and *Safe to share views* (score {pm.loc['RES3','fav_pct']:.1f}%, counted as protect).

## 5. Comment analysis (slides 7, 10, 13)

- **Codebook:** {len(codebook)} topics with written include/exclude rules (e.g. communication, recognition, career growth, fairness, voice and follow-through, cross-team work, pay and benefits).
- **Coding:** each answer read in context and given **one or more topics** (multi-label). Answers were also classed as suggestion, current strength, no concern, no change proposed or unclear.
- **Who coded:** an AI assistant, followed by a documented second reading by the same assistant ({int(review['reread_n'].sum())} re-reads, {int(review['revised_n'].sum())} labels revised). This is **not** an independent human double-coding, so there is no inter-rater agreement statistic. A small number of translations ({int(review['translation_confirmation_pending_n'].sum())}) still await confirmation.
- **Counting:** topics are counted **once per person**, not per mention, so one long answer cannot inflate a topic. (The topic map in section 6 counts answers instead.)

## 6. Topic map (slide 7)

- **Plain answer:** a circle is a topic; a line means two topics were raised in the same answer at least 10 times. Colours are groups of topics that tend to appear together.
- **Data:** 1,230 topic-coded suggestion answers from 305 people. Topics shown if raised in at least 20 answers (13 topics; tools and facilities had no strong links and is omitted from the slide).
- **Method:** circle size = number of people; line width = shared mentions. Layout uses association strength (pair count ÷ product of topic counts) with our own force-directed placement; groups come from weighted modularity clustering. It is **inspired by VOSviewer**, not a native VOSviewer run.
- **Key caution, prompt dependence:** {ct.dominant_prompt_n} of the {ct.comments} communication–teamwork co-mentions came from the teamwork question, and {fd.dominant_prompt_n} of the {fd.comments} fairness–career co-mentions came from the fairness question. The map organises what people said; it is not independent proof of the priorities.

## 7. HR choice question (slides 10, 13)

Everyone picked **one** answer to “If HR could do one thing better…”. Counts are of people (n = 327). Top three: listening to employees ({int(hr.iloc[0].respondents)}), career progression ({int(hr.iloc[1].respondents)}), benefits and facilities ({int(hr.iloc[2].respondents)}). Because the options were fixed, it shows relative preference, not everything people want.

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
{tri_rows}

A dash means the source has no matching question (e.g. there is no rated pay question, and no HR option for cross-team work).

## 9. Named vs anonymous (slide 5)

| | n | Plan to stay 3–5 yrs | Would recommend | Fix-first questions |
|---|---|---|---|---|
| Gave a name | {int(nva.loc['Named','n'])} | {nva.loc['Named','stay_3_5_yrs_fav']:.1f}% | {nva.loc['Named','recommend_fav']:.1f}% | {nva.loc['Named','fix_first_items_fav']:.1f}% |
| Anonymous | {int(nva.loc['Anonymous','n'])} | {nva.loc['Anonymous','stay_3_5_yrs_fav']:.1f}% | {nva.loc['Anonymous','recommend_fav']:.1f}% | {nva.loc['Anonymous','fix_first_items_fav']:.1f}% |

Differences are statistically significant: Fisher exact test p = {p_stay:.3f} (stay) and p = {p_rec:.3f} (recommend); Mann–Whitney on the overall culture score p = {p_culture:.3f}. This is **consistent with** more careful answers when named, but the two groups may also simply be different people. Either way, the headline scores are probably a little optimistic.

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

**How sure is the order?** The 500-resample bootstrap ranges overlap, so we read tiers. Leaders act on feedback and equal growth are in the top five in {pm.loc['CRE5','p_top5']:.0%} and {pm.loc['FAI2','p_top5']:.0%} of resamples.

**Does this prove fairness causes people to leave?** No. It shows which questions move together with wanting to stay. The pilot is the test.

**Were the comments read by people?** They were coded by an AI assistant with a documented second reading against a written codebook. We recommend a short human spot-check before decisions rely on topic counts.

**Is the topic map VOSviewer?** It follows VOSviewer’s idea (topic co-occurrence, association strength, clustering) with our own implementation, and links depend on question wording.

**Why Customer Service?** With 51 people it is the lowest group on fair decisions, leaders acting, recognition and plan to stay. That makes it the place a pilot can show the clearest change.

**Why is pay not a priority?** There is no rated pay question and a 90-day pilot cannot change pay. 51 people chose it as HR’s main job, so we route it to the yearly pay and facilities review and say so openly.

**Why say “positive” only for 4–5?** “Sometimes” is not an endorsement. Counting it would hide the gap. This matches common practice in large employee surveys.

<p class="foot">Tools: Python (pandas, NumPy, SciPy, Matplotlib), run in one reproducible notebook with pinned dependencies (uv). No data was uploaded to any external service for the analysis; no names appear in any output.</p>
"""

CSS = """
@page { size: A4; margin: 16mm 16mm 16mm 16mm;
  @bottom-left { content: "Safewater Lines · Methodology sheet · team copy"; font: 7.5pt Arial; color: #6b7b88 }
  @bottom-right { content: counter(page) " / " counter(pages); font: 7.5pt Arial; color: #6b7b88 } }
body { font-family: Arial, Helvetica, sans-serif; font-size: 9.2pt; line-height: 1.42; color: #243441; }
.kicker { color: #2f5d7c; font-weight: bold; font-size: 8pt; letter-spacing: .04em; margin: 0 }
h1 { font-size: 22pt; margin: 2pt 0 4pt; }
.lede { color: #5b6b78; font-size: 10pt; margin-top: 0 }
h2 { font-size: 12pt; color: #2f5d7c; border-top: 1px solid #d5dde3; padding-top: 7pt; margin: 14pt 0 5pt; break-after: avoid }
p, li { margin: 3pt 0 }
ul, ol { padding-left: 15pt; margin: 3pt 0 }
table { border-collapse: collapse; width: 100%; margin: 6pt 0; font-size: 8.4pt; break-inside: avoid }
th { background: #eef2f5; color: #2f5d7c; text-align: left; font-size: 7.6pt; text-transform: uppercase; letter-spacing: .02em }
th, td { padding: 3.5pt 5pt; border-bottom: 1px solid #e1e7eb; vertical-align: top }
code { font-size: 8.2pt }
strong { color: #1d2b36 }
.foot { color: #6b7b88; font-size: 8pt; margin-top: 14pt; border-top: 1px solid #d5dde3; padding-top: 6pt }
"""

if __name__ == "__main__":
    # Markdown copy: the dashboard assistant reads it as context.
    (HERE / "METHODOLOGY_SHEET.md").write_text(TEXT.replace('<p class="kicker">', "<p>").strip() + "\n")
    body = markdown.markdown(TEXT, extensions=["tables", "sane_lists"])
    src = BUILD / "methodology.html"
    src.write_text(f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Methodology sheet</title><style>{CSS}</style></head><body>{body}</body></html>")
    subprocess.run(["weasyprint", "--quiet", str(src), str(PDF)], check=True)
    print(f"Created {PDF}")
