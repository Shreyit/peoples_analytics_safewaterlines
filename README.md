# Safewater Lines — People Analytics ("Your Voice" survey)

## Project direction

- [Assignment brief](docs/PROJECT_BRIEF.md): organisation objectives, deliverables, deadline, and confidentiality requirements.
- [Working project brain](docs/PROJECT_BRAIN.md): our approach, research agenda, decisions, and next steps. Read this before extending the analysis.

```
data/
  raw/          original workbook (read-only, never edit)
  processed/    survey_clean.csv, codebook.csv  ← written by notebook 00
notebooks/
  00_data_understanding_eda.ipynb   one working notebook: EDA, methods, employee voice, integrated evidence
  archive/                          old / superseded notebooks
reports/figures/                    exported charts for the deck
reports/tables/                     aggregate findings, codebook, phrase references and action options
reports/network/                    offline interactive topic map, aggregate JSON and VOSviewer-compatible files
reports/FINAL_ANALYSIS_SYNTHESIS.md  consolidated findings and actions for presentation planning
reports/ANALYSIS_FROM_DATA_TO_ACTION.md  complete base-to-findings guide, review results and proposed roadmap
src/                                reusable helpers (once code repeats across notebooks)
```

## Setup
```bash
uv sync                      # creates .venv from uv.lock
```
In VS Code, select the `.venv (Python 3.14)` kernel and run notebooks top to bottom.

## Data notes
- Use the `SWL - MASTERDATA` sheet only. The language sheets have tenure bands auto-converted to dates by Excel,
  and `Masterdata - do not refer` is an older copy.
- Likert scale: Almost never 1 · Rarely 2 · Sometimes 3 · Usually/Often 4 · Almost always/Always 5
- `full_name` is personal data: it's dropped in processing and must never be exported.
- Free-text comments may still contain identifiers; the processed survey remains confidential. Presentation exports contain aggregates rather than raw comments or case IDs.
- `CULTURE_MEAN` is our descriptive 25-item summary (formerly `TRUST_INDEX`), not an official or validated Trust Index.
- Step 1 follows the EDA summary. The final Markdown cell contains the methodology reference, distinguishing used, planned, and conditional methods. Prepare the executive PowerPoint after the findings and action roadmap are complete.
- Steps 2–4 add thematic content coding, supporting bigrams/trigrams, paired and tenure profiles, and an evidence/action-options register. Qualitative counts are exploratory single-assistant coding; independent review is outstanding. The source-order hash protects the embedded coding ledger from silent reuse on changed comments.
- Step 5 deepens cross-team execution and fairness, adds three supporting themes, and generates the final analysis synthesis and a VOSviewer-inspired interactive network. Its layout/grouping is custom; question dependence is visible in the sensitivity controls. Presentation structure/storyline and the PowerPoint follow this analysis package.
- Step 6 documents the assistant re-review (568 comments, including all 104 initial flags; 53 edits), regenerates the findings and drafts the 0–90-day roadmap, KPI dictionary and decision gates. The full walkthrough is [From Data to Action](reports/ANALYSIS_FROM_DATA_TO_ACTION.md). Independent human validation remains separate; 75 cases still need clarification/context confirmation.
