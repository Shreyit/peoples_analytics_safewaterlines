# Safewater Lines — People Experience dashboard

A local, two-page dashboard for reviewing the survey before the executive presentation. The restrained layout follows a Tableau-style analytical dashboard: white panels, aligned tables, horizontal bars and explicit measures. It uses the project's actual results.

## Open the dashboard

Open **[dist/index.html](dist/index.html)** in a desktop browser. It works offline; no installation, account or server is needed. Keep the other files in `dist/` beside it when copying the dashboard to another laptop.

During editing, **[src/index.html](src/index.html)** also opens directly or through an IDE preview server. It loads the shared aggregate snapshot from `../dist/data.js`; rebuild if the snapshot needs refreshing.

Use **Overview** and **Focus findings** to change pages. Both pages fit the browser window without scrolling at the tested sizes below. Use normal browser zoom (100%) and the full-screen button if browser controls leave too little vertical space.

## What is included

| Page | Content | Interaction |
| --- | --- | --- |
| 01 · Overview | Response records, favourable answers, culture mean, comment contributors; all six survey blocks; group comparisons; question distributions | Filter by department and tenure; select a dimension to inspect its five questions; compare tenure or department groups; reset filters |
| 02 · Focus findings | Within-team support versus cross-team work, the paired comparison, fairness items, recognition, related employee requests and a proposed 90-day pilot pathway | Study-wide findings remain fixed at 327 response records; hover over charts for counts and exact item wording |

The **About the measures** button explains scoring, scope and interpretation. Keyboard users can navigate the page tabs with arrow keys.

## Measures and interpretation

- **Favourable** means 4–5 of valid rating answers; **unfavourable** means 1–2. The middle category is **3 · Sometimes**.
- The full study has **327 response records** and **9,810 valid rating answers**. Its **84.9% favourable answer share** is a share of item answers, not the percentage of employees who are engaged.
- **Culture mean, 4.35/5**, averages 25 items across the five culture blocks. It is a descriptive working measure; overall experience is shown separately as the sixth block.
- Workforce eligibility is unavailable, so the dashboard does not invent a survey participation rate.
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
