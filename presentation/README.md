# Safewater Lines — presentations and reference report

| Output | Use it for | Files |
| --- | --- | --- |
| **20-minute pitch (plain English) — present this** | Presenting on the day: 19 slides, one idea each, large text, no internal file references on slides or in notes; notes give a time window per slide | [PPTX](output/Safewater_Lines_Pitch_20min.pptx) · [PowerPoint PDF](output/Safewater_Lines_Pitch_20min_PowerPoint.pdf) · [script](PITCH_SPEAKER_GUIDE.md) |
| **20-minute pitch — team copy** | Same slides with the evidence file shown under each slide and in the notes, for preparing answers | [PPTX](output/Safewater_Lines_Pitch_20min_TEAM_with_sources.pptx) · [PDF](output/Safewater_Lines_Pitch_20min_TEAM_with_sources.pdf) |
| **Executive deck** | Detailed review and Q&A: 16 main + 4 reference slides | [PPTX](output/Safewater_Lines_People_Experience.pptx) · [PowerPoint PDF](output/Safewater_Lines_People_Experience_PowerPoint.pdf) · [guide](SPEAKER_GUIDE.md) |
| **Full reference report (team only, not for presenting)** | Reading the whole evidence: A4, 38 pages with contents, summary, full analysis, figures, evidence tables, roadmap/KPIs, questionnaire, glossary and methodology | [PDF](output/Safewater_Lines_Full_Reference.pdf) |

The sections below describe the executive deck; the pitch reuses its layout engine, data checks and fit validation (`build_pitch.py`), and the reference report is assembled from the notebook's generated outputs (`build_reference.py`).

## Executive deck

Open the **[editable PowerPoint](output/Safewater_Lines_People_Experience.pptx)** or the **[PDF exported by PowerPoint](output/Safewater_Lines_People_Experience_PowerPoint.pdf)**. The deck uses a white 16:9 canvas, Arial, charcoal text and a muted blue accent. Charts, tables and labels are editable PowerPoint shapes rather than screenshots.

There are **16 main slides and four reference slides**. A suggested rehearsal length is about 15 minutes for the main story; the assignment did not specify a presentation duration. Every slide has speaker notes and an aggregate source reference. Team names were not supplied and have not been invented.

## Storyline

| Slides | Purpose |
| --- | --- |
| 1–3 | Recommendation, headline figures beside their anonymous counterparts, and how to read the deck |
| 4–5 | Strengths to protect and the survey landscape |
| 6–7 | Why these priorities: priority matrix (link to outcomes vs current score) and the four-source evidence check |
| 8–9 | Priority 1: fair, explainable people decisions, growth and recognition · Priority 2: leaders listen and visibly act |
| 10–12 | Where to start (group hotspots), the targeted cross-team handover fix, and what else employees raised (incl. pay/benefits) |
| 13–16 | One 90-day pilot with owners and effort, roadmap, success measures and three leadership decisions |
| 17–20 | Reference: methods, robustness checks, group follow-up and topic connections |

### What changed in the 30 October revision

The earlier version led with cross-team execution as Priority 1. Notebook **Step 7** tested the order against four sources of evidence: current score, relative-weights link to recommend/satisfaction/intention to stay, the HR forced choice and the open "one change" comments. Fair people decisions with growth, and leaders listening and acting, were strong on all four. Cross-team work ranks 9th of 30, is rarely raised unprompted and drops out of the top tier among anonymous respondents, so it is now a targeted pilot starting in Customer Service. The revision also adds the named-vs-anonymous comparison, the HR-choice chart, group hotspots, pay/benefits acknowledgement, effort per workstream and indicative targets.

Read [SPEAKER_GUIDE.md](SPEAKER_GUIDE.md) for the narrative, interpretation limits and source references. Use the [dashboard](../dashboard/dist/index.html) for interactive questions before or after the main presentation.

## Interpretation retained in the deck

- Findings describe **327 supplied response records**, not a verified workforce census. Participation rate is unknown.
- Favourable means **4–5**; **3 is Sometimes**, not neutral. Fairness counts at 1–3 must not be restated as unfair-treatment prevalence.
- Qualitative request topics overlap, and requests are not incident counts. The documented assistant re-review does not constitute independent human validation.
- Proposed owners, actions and operating standards are **proposals**, not commitments or predicted effects. Day 0 begins on organisational approval. Numerical experience-outcome targets require a pilot baseline and a Day-14 decision.
- The topic-network appendix is a **selected five-topic excerpt**. Positions are schematic, node area represents unique-record support within the primary map context and line widths indicate same-answer co-mentions. Prompt dependence is explicit.

No employee names or source-row IDs are included. Three short verbatim comments (slides 8 and 9) are de-identified, contain no names, places or roles, and are labelled as typical examples rather than evidence of frequency.

## Files and verification

```text
presentation/
  output/                 Editable PPTX, native PowerPoint PDF and PDF companion
  preview/                Companion PNGs; native/ contains PowerPoint-rendered PNGs
  SPEAKER_GUIDE.md        Narrative, boundaries and source references
  build_presentation.py  Aggregate source reads, layout and export
  requirements.txt       Presentation-only Python dependencies
  export_native.applescript  Optional export using installed macOS PowerPoint
  slide_content.json     Structured content and shared layout model
  qa_results.json        Structure, text-metric and geometry checks
  verify_native.py       Native PDF text, page and canvas checks
  native_qa_results.json Results from PowerPoint's exported PDF
```

The build reopens the saved PPTX, checks all 20 slides have notes, verifies shapes lie inside the canvas and checks text wrapping using Arial font metrics. It checks selected source facts and renders all 20 pages of the companion PDF for visual inspection.

The deck was also opened and exported using **Microsoft PowerPoint for macOS**. All 20 pages contain the expected text, with no text outside the slide canvas. Native slide previews are in [preview/native/](preview/native/), with a [contact sheet](preview/native/contact-sheet.png) and [verification results](native_qa_results.json). Inherited theme shadows were explicitly removed and the final native rendering was inspected.

The additional [companion PDF](output/Safewater_Lines_People_Experience.pdf) and top-level preview PNGs are generated directly from the shared layout model using ReportLab and PyMuPDF. For the actual PowerPoint appearance, prefer the native PDF and native previews above. The Python build alone does not refresh the native export; run the optional AppleScript export and `verify_native.py` after changing the deck.

## Rebuild

From the repository root, install the separate presentation dependencies into the project environment if needed:

```sh
uv pip install --python .venv/bin/python -r presentation/requirements.txt
.venv/bin/python presentation/build_presentation.py   # executive deck
.venv/bin/python presentation/build_pitch.py          # 20-minute pitch
.venv/bin/python presentation/build_reference.py      # full reference PDF (needs the WeasyPrint CLI: brew install weasyprint)
```

For the PowerPoint-rendered PDFs, export and verify each deck (the verifier takes `pitch` for the pitch deck):

```sh
osascript presentation/export_native.applescript "$PWD/presentation/output/Safewater_Lines_Pitch_20min.pptx" "$PWD/presentation/output/Safewater_Lines_Pitch_20min_PowerPoint.pdf"
.venv/bin/python presentation/verify_native.py pitch
```

The reference build also checks that no respondent's typed name appears anywhere in the PDF (names are read in memory only).

The current build uses the Arial font files installed under `/System/Library/Fonts/Supplemental` on macOS. No online service, model call or data upload is needed for generation. The build reads the processed survey and existing aggregate exports; it does not rerun or modify the analytical notebook.

Rebuilding replaces the generated PPTX, companion PDF, previews and guide. If editing slides directly in PowerPoint, save that revised deck under a separate filename before rebuilding.
