# Safewater Lines — People Analytics ("Your Voice" survey)

## Project direction

- [Assignment brief](docs/PROJECT_BRIEF.md): organisation objectives, deliverables, deadline, and confidentiality requirements.
- [Working project brain](docs/PROJECT_BRAIN.md): our approach, research agenda, decisions, and next steps. Read this before extending the analysis.

```
data/
  raw/          original workbook (read-only, never edit)
  processed/    survey_clean.csv, codebook.csv  ← written by notebook 00
notebooks/
  00_data_understanding_eda.ipynb   one working notebook: preparation, EDA, analytical foundation; extend here
  archive/                          old / superseded notebooks
reports/figures/                    exported charts for the deck
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
- `CULTURE_MEAN` is our descriptive 25-item summary (formerly `TRUST_INDEX`), not an official or validated Trust Index.
- Step 1 follows the EDA summary. The final Markdown cell contains the methodology reference, distinguishing used, planned, and conditional methods. Prepare the executive PowerPoint after the findings and action roadmap are complete.
