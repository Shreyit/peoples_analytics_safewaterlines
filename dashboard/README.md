# Safewater Lines — People Experience dashboard

A local, two-page dashboard for reviewing the survey before the executive presentation. The restrained layout follows a Tableau-style analytical dashboard: white panels, aligned tables, horizontal bars and explicit measures. It uses the project's actual results.

## Open the dashboard

- **Live Cloud Deployment (with Vertex AI Gemini Assistant):**  
  👉 **[https://safewater-dashboard-66109299840.asia-south1.run.app](https://safewater-dashboard-66109299840.asia-south1.run.app)**  
  Hosted on Google Cloud Run (`asia-south1`). Fully interactive with the "Ask the survey" Gemini Q&A assistant active.

- **Offline / Local File:**  
  Open **[dist/index.html](dist/index.html)** in a desktop browser. It works offline; no installation, account or server is needed. Keep the other files in `dist/` beside it when copying the dashboard to another laptop.

During editing, **[src/index.html](src/index.html)** also opens directly or through an IDE preview server. It loads the shared aggregate snapshot from `../dist/data.js`; rebuild if the snapshot needs refreshing.

Use **Overview** and **Focus findings** to change pages. Both pages fit the browser window without scrolling at the tested sizes below. Use normal browser zoom (100%) and the full-screen button if browser controls leave too little vertical space.

## Survey assistant (optional, Gemini on Vertex AI)

**Ask the survey** opens a side panel that answers questions in plain English, using only the project's aggregate reports as context: the project brief, the analysis report and synthesis, the methodology sheet, the pitch speaker guide and this README. Every answer ends with its source. It needs the small local server below; opening `dist/index.html` directly still works, but without the assistant.

It authenticates with your Google Cloud login (Application Default Credentials). **No API key is used or stored.**

One-time setup:

```sh
brew install --cask google-cloud-sdk
gcloud auth login
gcloud auth application-default login
gcloud services enable aiplatform.googleapis.com --project <your-project-id>
```

Run (from the repository root), then open http://127.0.0.1:8765:

```sh
GOOGLE_CLOUD_PROJECT=<your-project-id> uv run python dashboard/assistant/server.py
```

Optional settings: `GOOGLE_CLOUD_LOCATION` (default `global`), `ASSISTANT_MODEL` (default `gemini-2.5-flash`), `ASSISTANT_PORT` (default 8765). `ASSISTANT_OFFLINE=1` tests the panel and guardrails without contacting Google.

**Guardrails**

| Layer | What it does |
| --- | --- |
| Context | Aggregate Markdown reports only: no raw survey file, comment exports or notebook. The server refuses to start if any respondent's typed name appears in the context (names are read in memory only). |
| Before the model | Refuses, on this machine and without calling Vertex AI, questions over 800 characters, attempts to identify individuals (“who wrote…”, names, contact details, de-anonymising), questions containing a respondent's name, and prompt-injection attempts. Limit of 30 questions per 10 minutes. |
| Model instructions | Answer only from the reports and cite the source; say when something isn't covered; no individuals or groups under 10; associations, not causes; proposals described as proposals; decline off-topic requests. Temperature 0.2, about 200-word answers. |
| After the model | Any answer containing a respondent's name is withheld. |
| Network and logs | Listens on 127.0.0.1 only and rejects other origins. Questions and answers are not logged or stored. |

**Data agreement:** each question sends the report context to Vertex AI in your Google Cloud project. Use a project your team controls and that the NDA permits. Answers can be wrong; check the stated source before relying on one.

## What is included

| Page | Content | Interaction |
| --- | --- | --- |
| 01 · Overview | Response records, favourable answers, culture mean, comment contributors; all six survey blocks; group comparisons; question distributions | Filter by department and tenure; select a dimension to inspect its five questions; compare tenure or department groups; reset filters |
| 02 · Focus findings | Headline intention to stay with its anonymous counterpart; Priority 1 (fair decisions, growth and recognition: six questions); Priority 2 (leaders listen and act: the HR forced-choice question); the targeted cross-team handover fix; the proposed 90-day pilot with owners | Study-wide findings remain fixed at 327 response records; hover over charts for counts and exact item wording |

The **About the measures** button explains scoring, scope and interpretation. Keyboard users can navigate the page tabs with arrow keys.

## Measures and interpretation

- **Favourable** means 4–5 of valid rating answers; **unfavourable** means 1–2. The middle category is **3 · Sometimes**.
- The full study has **327 response records** and **9,810 valid rating answers**. Its **84.9% favourable answer share** is a share of item answers, not the percentage of employees who are engaged.
- **Culture mean, 4.35/5**, averages 25 items across the five culture blocks. It is a descriptive working measure; overall experience is shown separately as the sixth block.
- Workforce eligibility is unavailable, so the dashboard does not invent a survey participation rate.
- The priority order comes from notebook **Step 7**: current score, relative-weights link to recommend / satisfaction / intention to stay (Fairness = 31% of the explained variation, R² 0.65), the HR forced choice, and the open "one change" comments. These are associations, not causes. Anonymous respondents (n = 100) are less favourable: 78.0% intend to stay versus 87.5% overall.
- The cross-team finding uses the same response records: **45** rated own-team support favourably and cross-team collaboration at 1–3. The reverse pattern occurs in **16** records. This is a descriptive comparison.
- **137** records have at least one fairness response at 1–3; **97** have at least two. These counts include Sometimes and should not be described as the prevalence of unfair treatment.
- Employee-request topics overlap. They count unique response records mentioning requests, not dissatisfaction or incident frequency. Comment coding has had a documented assistant re-review; independent human validation remains outstanding.
- Scores and detailed counts for cohorts below **10 response records** are withheld in this dashboard. This is a display rule, not a guarantee against reconstruction from overlapping aggregates. Keep the dashboard within the authorised project audience.

## Laptop sizing references and verification

Physical screen size does not determine browser space: display scaling, browser zoom, menus and toolbars also matter. These real laptop specifications anchor three **assumed browser content sizes** for testing, rather than claims about manufacturer-default browser viewports.

| Reference laptop | Physical screen | Native display resolution | Tested browser content area, CSS pixels | Tested device pixel ratio |
| --- | --- | --- | --- | --- |
| [MacBook Air, M4, 2025](https://support.apple.com/en-us/122209) | 13.6 inches | 2560 × 1664 | 1280 × 720 | 2 |
| [MacBook Pro, M4, 2024](https://support.apple.com/en-us/121552) | 14.2 inches | 3024 × 1964 | 1512 × 850 | 2 |
| [MacBook Air, M4, 2025](https://support.apple.com/en-us/122210) | 15.3 inches | 2880 × 1864 | 1440 × 800 | 2 |
| Additional laptop viewport | — | — | 1366 × 768 | 1 |
| Reduced-height check | — | — | 1280 × 640 | 1 |

The three laptop cases assume a 2:1 native-to-logical display mapping, then reserve 112–132 CSS pixels of vertical space for the operating system and browser controls. They are engineering test assumptions. Apple documents that users can [change display resolution and scaling](https://support.apple.com/en-ie/guide/mac-help/mchl86d72b76/27/mac/27).

Both pages were checked in a real Chromium browser at all five content sizes: **10 page/viewport cases passed without document or panel overflow**. Filters, score withholding, dimension selection, group comparison, page navigation and the measures dialog also passed. Screenshots are in [qa/screenshots/](qa/screenshots/); the recorded results are in [qa/results.json](qa/results.json).

The layout adapts to available width and height. Below 1120 × 640 it displays a message to use a larger viewport or full screen. The checks above establish the supported presentation sizes; they do not imply that arbitrary zoom levels or every browser configuration have been tested.

## Files and rebuilding

```text
dashboard/
  dist/                 Ready-to-open offline dashboard and aggregate snapshot
  src/                  Editable HTML, CSS and browser JavaScript
  build_data.py         Validates survey results and creates dist/
  assistant/server.py   Local server: dashboard + Vertex AI survey assistant with guardrails
  qa/verify.mjs         Browser layout and interaction checks
  qa/results.json       Latest recorded checks
  qa/screenshots/       Both pages at each tested viewport
```

To refresh the dashboard after an approved analytical update, run from the repository root:

```sh
.venv/bin/python dashboard/build_data.py
```

The build reads `data/processed/survey_clean.csv`, the codebook, `reports/tables/item_evidence_profile.csv` and `reports/tables/employee_voice_topic_summary.csv`. It verifies the current survey shape, rating values, item favourable shares and the paired comparison before packaging 54 department/tenure scopes. If those assumptions change, review the build and dashboard wording together.

The browser package contains aggregate figures only. It does not include raw survey rows, employee names or verbatim comments, and it makes no external network requests. The original analytical files remain the source of truth; this folder presents their current snapshot.

For optional browser verification, `qa/verify.mjs` uses an existing local Playwright installation and Chromium. Its defaults refer to the development machine; on another machine, provide absolute paths through `DASHBOARD_PLAYWRIGHT_MODULE` (the `playwright-core/index.mjs` file) and `DASHBOARD_BROWSER_PATH` (the Chromium executable), then run:

```sh
node dashboard/qa/verify.mjs
```

No Playwright installation is required to open or use the dashboard.

## Cloud deployment (Google Cloud Run)

To deploy or update the live dashboard on Cloud Run:

```sh
gcloud run deploy safewater-dashboard \
  --source . \
  --region asia-south1 \
  --project veris-507205 \
  --allow-unauthenticated
```

Live service: **[https://safewater-dashboard-66109299840.asia-south1.run.app](https://safewater-dashboard-66109299840.asia-south1.run.app)**
