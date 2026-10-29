# Safewater Lines — executive presentation

Open the **[editable PowerPoint](output/Safewater_Lines_People_Experience.pptx)** or the **[PDF exported by PowerPoint](output/Safewater_Lines_People_Experience_PowerPoint.pdf)**. The deck uses a white 16:9 canvas, Arial, charcoal text and a muted blue accent. Charts, tables and labels are editable PowerPoint shapes rather than screenshots.

There are **13 main slides and four reference slides**. A suggested rehearsal length is 12–15 minutes for the main story; the assignment did not specify a presentation duration. Every slide has speaker notes and an aggregate source reference. Team names were not supplied and have not been invented.

## Storyline

| Slides | Purpose |
| --- | --- |
| 1–2 | Introduce the organisational question and recommended direction |
| 3–5 | Establish the response base, preserve strengths and explain the survey landscape |
| 6–8 | Examine cross-team execution, fairness and employee requests |
| 9–10 | Connect supporting practices to two bounded, accountable pilots |
| 11–13 | Propose a 90-day roadmap, success measures and concrete leadership decisions |
| 14–17 | Reference: method choices, sensitivity/review status, group follow-up and topic connections |

Read [SPEAKER_GUIDE.md](SPEAKER_GUIDE.md) for the narrative, interpretation limits and source references. Use the [dashboard](../dashboard/dist/index.html) for interactive questions before or after the main presentation.

## Interpretation retained in the deck

- Findings describe **327 supplied response records**, not a verified workforce census. Participation rate is unknown.
- Favourable means **4–5**; **3 is Sometimes**, not neutral. Fairness counts at 1–3 must not be restated as unfair-treatment prevalence.
- Qualitative request topics overlap, and requests are not incident counts. The documented assistant re-review does not constitute independent human validation.
- Proposed owners, actions and operating standards are **proposals**, not commitments or predicted effects. Day 0 begins on organisational approval. Numerical experience-outcome targets require a pilot baseline and a Day-14 decision.
- The topic-network appendix is a **selected five-topic excerpt**. Positions are schematic, node area represents unique-record support within the primary map context and line widths indicate same-answer co-mentions. Prompt dependence is explicit.

No employee names, source-row IDs or verbatim comments are included.

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

The build reopens the saved PPTX, checks all 17 slides have notes, verifies shapes lie inside the canvas and checks text wrapping using Arial font metrics. It checks selected source facts and renders all 17 pages of the companion PDF for visual inspection.

The deck was also opened and exported using **Microsoft PowerPoint for macOS**. All 17 pages contain the expected text, with no text outside the slide canvas. Native slide previews are in [preview/native/](preview/native/), with a [contact sheet](preview/native/contact-sheet.png) and [verification results](native_qa_results.json). Inherited theme shadows were explicitly removed and the final native rendering was inspected.

The additional [companion PDF](output/Safewater_Lines_People_Experience.pdf) and top-level preview PNGs are generated directly from the shared layout model using ReportLab and PyMuPDF. For the actual PowerPoint appearance, prefer the native PDF and native previews above. The Python build alone does not refresh the native export; run the optional AppleScript export and `verify_native.py` after changing the deck.

## Rebuild

From the repository root, install the separate presentation dependencies into the project environment if needed:

```sh
uv pip install --python .venv/bin/python -r presentation/requirements.txt
.venv/bin/python presentation/build_presentation.py
```

The current build uses the Arial font files installed under `/System/Library/Fonts/Supplemental` on macOS. No online service, model call or data upload is needed for generation. The build reads the processed survey and existing aggregate exports; it does not rerun or modify the analytical notebook.

Rebuilding replaces the generated PPTX, companion PDF, previews and guide. If editing slides directly in PowerPoint, save that revised deck under a separate filename before rebuilding.
