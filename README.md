# Safewater Lines — People Analytics

An analysis of the **Your Voice employee survey**, connecting employee experience to practical organisational improvements. **Priority 1** is **fair, explainable people decisions and growth**, with recognition; **Priority 2** is **leaders listening and visibly acting**. Cross-team handovers are a targeted fix starting in Customer Service. Pride, belonging and own-team support are strengths to protect. The order comes from the notebook's Step 7 prioritisation check, which uses four sources of evidence.

**Current outputs:** one analytical notebook, a two-page offline dashboard, an editable executive PowerPoint, detailed findings and a proposed 90-day implementation roadmap. Presentation deadline: **30 October 2026, at TISS**.

## Start here — important files

| Deliverable | Open this file | What it contains |
| --- | --- | --- |
| **20-minute pitch (plain English)** | **[Safewater_Lines_Pitch_20min.pptx](presentation/output/Safewater_Lines_Pitch_20min.pptx)** | The deck to present: 19 slides, large text, simple wording, no internal file references, timed script in the notes ([PDF](presentation/output/Safewater_Lines_Pitch_20min_PowerPoint.pdf), [script](presentation/PITCH_SPEAKER_GUIDE.md)). A [team copy with sources](presentation/output/Safewater_Lines_Pitch_20min_TEAM_with_sources.pptx) shows the evidence file behind each slide |
| **Full reference report (team only)** | **[Safewater_Lines_Full_Reference.pdf](presentation/output/Safewater_Lines_Full_Reference.pdf)** | 38-page A4 report: summary, full analysis, figures, evidence tables, roadmap/KPIs, questionnaire, glossary, methodology |
| **PowerPoint presentation** | **[Safewater_Lines_People_Experience.pptx](presentation/output/Safewater_Lines_People_Experience.pptx)** | Main executive deliverable: 16 main slides + four appendix slides, editable charts, speaker notes and source references |
| **Presentation PDF** | **[PowerPoint-exported PDF](presentation/output/Safewater_Lines_People_Experience_PowerPoint.pdf)** | The slide appearance exported and checked in Microsoft PowerPoint |
| **Main analytical notebook** | **[00_data_understanding_eda.ipynb](notebooks/00_data_understanding_eda.ipynb)** | The single source for data understanding, cleaning, analysis, comment coding, findings, roadmap and the final methodology table |
| **Interactive dashboard** | **[dashboard/dist/index.html](dashboard/dist/index.html)** | Two pages: survey overview with filters, followed by the two priorities, the targeted cross-team fix and the proposed pilot; opens offline |
| **Complete findings and methods** | **[ANALYSIS_FROM_DATA_TO_ACTION.md](reports/ANALYSIS_FROM_DATA_TO_ACTION.md)** | Walkthrough from the source data and base measures through deeper findings, review and implementation |
| **Concise findings synthesis** | [FINAL_ANALYSIS_SYNTHESIS.md](reports/FINAL_ANALYSIS_SYNTHESIS.md) | Strengths, primary priorities, supporting themes, evidence and interpretation limits |
| **Presentation speaker guide** | [SPEAKER_GUIDE.md](presentation/SPEAKER_GUIDE.md) | Slide-by-slide narrative, evidence and talking points; suggested 15-minute rehearsal plan |
| **Slide overview** | [Native PowerPoint contact sheet](presentation/preview/native/contact-sheet.png) | All 20 slides at a glance |

To review the project, open the **PowerPoint or PDF** first, use the **dashboard** to explore questions, then consult the **findings guide and notebook** for the evidence.

## Folder structure

```text
peoples_analytics_safewaterlines/
├── README.md                              Project navigation and setup
├── pyproject.toml                         Core analysis dependencies
├── uv.lock                                Locked analysis environment
├── .python-version                        Project Python version
│
├── docs/
│   ├── PROJECT_BRIEF.md                    Assignment, deliverables and deadline
│   └── PROJECT_BRAIN.md                    Working approach, decisions and status
│
├── data/
│   ├── raw/
│   │   └── Your Voice- Responses 21 OCT - FINAL.xlsx
│   └── processed/
│       ├── survey_clean.csv               Confidential cleaned response data
│       └── codebook.csv                   Variable labels and question wording
│
├── notebooks/
│   └── 00_data_understanding_eda.ipynb     MAIN ANALYSIS NOTEBOOK
│
├── reports/
│   ├── ANALYSIS_FROM_DATA_TO_ACTION.md     Complete findings/methods walkthrough
│   ├── FINAL_ANALYSIS_SYNTHESIS.md         Concise organisational story
│   ├── tables/                            Aggregate evidence, review and roadmap CSVs
│   ├── figures/                           Exported analysis charts
│   └── network/
│       ├── topic_network.html             Offline interactive topic map
│       ├── topic_network_data.json        Aggregate network data
│       ├── topics_map.txt                 VOSviewer-compatible map file
│       └── topics_network.txt             VOSviewer-compatible network file
│
├── dashboard/
│   ├── README.md                          Opening, measures and sizing instructions
│   ├── build_data.py                      Refresh aggregate dashboard data
│   ├── dist/
│   │   ├── index.html                     OPEN THIS DASHBOARD
│   │   ├── data.js                        Aggregate data snapshot
│   │   ├── app.js                         Packaged dashboard interactions
│   │   └── styles.css                     Packaged responsive layout
│   ├── src/                               Editable HTML, JavaScript and CSS
│   └── qa/
│       ├── verify.mjs                     Browser layout/interaction checks
│       ├── results.json                   Recorded verification results
│       └── screenshots/                   Both pages at tested laptop viewports
│
├── presentation/
│   ├── README.md                          Deck structure, verification and rebuilds
│   ├── SPEAKER_GUIDE.md                    Slide-by-slide presentation notes
│   ├── build_presentation.py              Generate editable PPTX and companion PDF
│   ├── requirements.txt                   Separate presentation dependencies
│   ├── export_native.applescript          Export through macOS PowerPoint
│   ├── verify_native.py                   Check PowerPoint-rendered PDF
│   ├── slide_content.json                 Structured slide content and layout
│   ├── qa_results.json                    Build/layout verification results
│   ├── native_qa_results.json             Native PowerPoint verification results
│   ├── output/
│   │   ├── Safewater_Lines_People_Experience.pptx
│   │   ├── Safewater_Lines_People_Experience_PowerPoint.pdf
│   │   └── Safewater_Lines_People_Experience.pdf  Companion PDF from shared layout
│   └── preview/
│       ├── native/                        Actual PowerPoint slide PNGs/contact sheet
│       └── ...                            Companion slide PNGs/contact sheet
│
└── src/                                   Reserved for reusable analysis helpers
```

The tree highlights the maintained deliverables and supporting files; it omits local environment files, caches and individual chart/table exports.

## Analysis and evidence

The notebook starts from the supplied master data and question wording, then moves through base distributions, working summaries, contextual employee-comment coding, paired comparisons, focused group profiles and integrated recommendations. Step 7 checks the priority order against four sources of evidence and compares named with anonymous respondents. It also records exploratory measurement checks and sensitivity analyses. The **last Markdown cell is the methodology reference**.

| Reference | Purpose |
| --- | --- |
| [Assignment brief](docs/PROJECT_BRIEF.md) | Organisational objectives, expected outputs, timeline and confidentiality requirements |
| [Project brain](docs/PROJECT_BRAIN.md) | Agreed approach, method-selection principles, decisions and current status |
| [Item evidence profile](reports/tables/item_evidence_profile.csv) | Valid answers, category shares, means and response-style sensitivity |
| [Finding verification register](reports/tables/finding_verification_register.csv) | Source-traced checks for headline findings |
| [Priority evidence check](reports/tables/priority_triangulation.csv) | Step 7: each theme graded on score, link to outcomes, HR choice and "one change" comments |
| [Priority matrix](reports/tables/priority_matrix.csv) | Step 7: relative-weights link to outcomes vs favourable share, with bootstrap and sensitivity checks |
| [Named vs anonymous](reports/tables/named_vs_anonymous.csv) | Headline measures for named and anonymous respondents |
| [Focus evidence and actions](reports/tables/final_focus_evidence_and_actions.csv) | The two priorities, recognition, the targeted cross-team fix and role clarity, connected to action options |
| [Employee voice summary](reports/tables/employee_voice_topic_summary.csv) | Overlapping request/preserve topics with labelled denominators |
| [Comment review changes](reports/tables/coding_review_before_after.csv) | Topic counts before and after the documented assistant re-review |
| [Interactive topic network](reports/network/topic_network.html) | VOSviewer-inspired exploration of same-answer topic connections and prompt dependence |

## Roadmap and measures

| File | Purpose |
| --- | --- |
| [0–90-day implementation roadmap](reports/tables/implementation_roadmap_0_90_days.csv) | Proposed actions, accountable roles, timing, dependencies and operating standards |
| [KPI dictionary](reports/tables/roadmap_kpi_dictionary.csv) | Definitions, denominators, survey references, operational baseline needs and review schedules |
| [Decision gates](reports/tables/roadmap_decision_gates.csv) | Day-0/14/30/60/90 decisions, including whether to scale, adapt or stop |

**Day 0 means organisational approval/start.** Proposed owners and process standards are not approved commitments. Numerical experience-outcome targets must be set after the pilot baseline.

## Open the dashboard and presentation

**No Python installation is needed to view the outputs.** Open the PPTX in PowerPoint, the PDF in a PDF reader, or `dashboard/dist/index.html` in a desktop browser. When moving the dashboard, copy the entire `dashboard/dist/` folder so its data and assets remain together.

The dashboard has department/tenure filters, selectable dimension diagnostics and a separate study-wide findings page. Its layout passed both-page checks at five browser viewports, including references for 13-, 14- and 15-inch laptops. During editing, `dashboard/src/index.html` also works and reads its data from `../dist/data.js`. See the [dashboard guide](dashboard/README.md) for sizing assumptions and controls.

The presentation uses a white 16:9 layout with restrained colours. All 20 slides have speaker notes and source references. The PPTX was exported through PowerPoint; expected text and slide bounds were checked. See the [presentation guide](presentation/README.md) for the storyline, previews and verification details.

## Run or refresh the project

Run commands from the repository root.

### Analysis environment

```sh
uv sync
```

In VS Code, select the **`.venv` / Python 3.14** notebook kernel and run [the main notebook](notebooks/00_data_understanding_eda.ipynb) from top to bottom. It produces the processed data and analytical exports. Keep analytical changes in this notebook.

### Dashboard snapshot

After refreshing the analytical exports:

```sh
.venv/bin/python dashboard/build_data.py
```

### Presentation outputs

Presentation dependencies are maintained separately from the analysis environment:

```sh
uv pip install --python .venv/bin/python -r presentation/requirements.txt
.venv/bin/python presentation/build_presentation.py
```

The current presentation build uses macOS Arial font files. This Python command refreshes the PPTX, companion PDF, notes and companion previews. **The native PowerPoint PDF/previews require a separate PowerPoint export and verification**; instructions and the export script are in [presentation/](presentation/README.md).

Save any manual PowerPoint revisions under a separate filename before rebuilding, since the build replaces its generated outputs. If analysis changes, refresh the notebook exports, then the dashboard and presentation so all deliverables describe the same evidence.

## Data and interpretation notes

- **Source:** use the `SWL - MASTERDATA` sheet in the supplied workbook. Language-sheet tenure bands were auto-converted to dates by Excel; `Masterdata - do not refer` is an older copy. Keep the raw workbook unchanged.
- **Response base:** 327 supplied master records, 30 complete rating items and 1,892 nonblank comments from 321 records. Eligible workforce size and representativeness are unknown.
- **Scale:** 1 Almost never · 2 Rarely · 3 Sometimes · 4 Usually/Often · 5 Almost always/Always. Favourable means 4–5. A count at 1–3 includes Sometimes and must not be presented as incident or unfair-treatment prevalence.
- **Working summary:** `CULTURE_MEAN` is an equal-weight, descriptive 25-item summary, excluding overall experience. It is not an official Trust Index or validated engagement index.
- **Qualitative review:** the same assistant reread 568 unique comments, including all 104 original flags, and revised 53 decisions. There are 75 remaining context-confirmation cases. Independent human validation remains outstanding; request topics overlap and are not dissatisfaction diagnoses.
- **Network:** the map is VOSviewer-inspired with custom layout/grouping and prompt-sensitivity controls. It is not a native VOSviewer run, an employee network, a causal map or independent validation.
- **Confidentiality:** names are dropped from processed columns, but free text may still identify employees. Raw/processed survey data remain confidential. Presentation and dashboard packages use aggregates and exclude employee names, raw comment text and source-row IDs. Follow the assignment's NDA and individual confidentiality requirements for access.
