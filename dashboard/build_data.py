"""Package aggregate presentation data. No raw comments/employee records enter dist/."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DIST = HERE / "dist"
DIST.mkdir(exist_ok=True)

DIMS = {"CRE": "Credibility", "RES": "Respect", "FAI": "Fairness", "PRI": "Pride",
        "CAM": "Camaraderie", "OVR": "Overall experience"}
TENURES = ["0 - 3", "3 - 5", "5 - 10", "10 - 15", "15 & Above"]
SHORT = {
    "CRE1": "Open, honest leadership communication", "CRE2": "Leaders keep their promises",
    "CRE3": "Confidence in organisational direction", "CRE4": "Timely communication of important changes",
    "CRE5": "Leaders listen and act on feedback", "RES1": "Manager support and wellbeing",
    "RES2": "Resources and support to work well", "RES3": "Comfort sharing views or concerns",
    "RES4": "Efforts and contributions recognised", "RES5": "Dignity and respect across roles",
    "FAI1": "Rewards based on performance", "FAI2": "Equal career-growth opportunities",
    "FAI3": "Consistent decisions without favouritism", "FAI4": "Fair workload and responsibilities",
    "FAI5": "Understanding employee-related decisions", "PRI1": "Proud to work for Safewater Lines",
    "PRI2": "Understanding contribution to the business", "PRI3": "Intention to stay for 3–5 years",
    "PRI4": "Positive impact on customers and business", "PRI5": "Motivation beyond basic duties",
    "CAM1": "Help and support within own team", "CAM2": "Teams work well across the organisation",
    "CAM3": "Belonging to the organisation", "CAM4": "Support from colleagues in other teams",
    "CAM5": "Celebrating others’ achievements", "OVR1": "Recommend as a great place to work",
    "OVR2": "Opportunities to learn and build a career", "OVR3": "Resources to perform and contribute",
    "OVR4": "Satisfaction with overall experience", "OVR5": "Meaningful and fulfilling work",
}

source = ROOT / "data/processed/survey_clean.csv"
df = pd.read_csv(source)
codebook = pd.read_csv(ROOT / "data/processed/codebook.csv").set_index("col")
reference = pd.read_csv(ROOT / "reports/tables/item_evidence_profile.csv").set_index("item")
topics = pd.read_csv(ROOT / "reports/tables/employee_voice_topic_summary.csv").set_index("topic_code")
items = [f"{d}{i}" for d in DIMS for i in range(1, 6)]
oe = [c for c in df if c.startswith("oe_")]
assert df.shape == (327, 56) and len(items) == 30
assert df[items].isin([1, 2, 3, 4, 5]).all().all()
assert np.allclose(df[items].ge(4).mean() * 100, reference.loc[items, "fav_%"])
MIN_N = 10


def summarise(frame):
    n = len(frame)
    if n < MIN_N:
        return {"status": "empty" if n == 0 else "suppressed", "n": 0 if n == 0 else None}
    answer_count = int(frame[items].count().sum().sum())
    result = {
        "status": "ready", "n": n, "validAnswers": answer_count,
        "favourable": float(frame[items].ge(4).to_numpy().mean() * 100),
        "culture": float(frame["CULTURE_MEAN"].mean()),
        "commentContributors": int(frame[oe].notna().any(axis=1).sum()),
        "dimensions": [], "items": {},
    }
    for dim, label in DIMS.items():
        cols = [f"{dim}{i}" for i in range(1, 6)]
        result["dimensions"].append({"code": dim, "label": label,
            "mean": float(frame[cols].to_numpy().mean()),
            "favourable": float(frame[cols].ge(4).to_numpy().mean() * 100)})
        result["items"][dim] = []
        for item in cols:
            s = frame[item]
            counts = [int(s.le(2).sum()), int(s.eq(3).sum()), int(s.ge(4).sum())]
            result["items"][dim].append({"code": item, "label": SHORT[item],
                "question": str(codebook.loc[item, "question"]), "n": int(s.count()),
                "mean": float(s.mean()), "counts": counts,
                "shares": [count / int(s.count()) * 100 for count in counts]})
    return result


def group_data(frame, variable, order):
    out = []
    for label in order:
        subset = frame.loc[frame[variable].eq(label)]
        if not len(subset):
            continue
        out.append({"label": label, "n": len(subset) if len(subset) >= MIN_N else None,
                    "mean": float(subset.CULTURE_MEAN.mean()) if len(subset) >= MIN_N else None})
    return out


departments = sorted(df.dept_group.unique())
cohorts = {}
for dept in ["all"] + departments:
    for tenure in ["all"] + TENURES:
        subset = df
        if dept != "all": subset = subset.loc[subset.dept_group.eq(dept)]
        if tenure != "all": subset = subset.loc[subset.tenure.eq(tenure)]
        summary = summarise(subset)
        if summary["status"] == "ready":
            summary["groups"] = {
                "tenure": group_data(subset, "tenure", TENURES),
                "department": group_data(subset, "dept_group", departments),
            }
        cohorts[dept + "|" + tenure] = summary

all_data = cohorts["all|all"]
pair = {
    "bothLower": int((df.CAM1.le(3) & df.CAM2.le(3)).sum()),
    "reverse": int((df.CAM1.le(3) & df.CAM2.ge(4)).sum()),
    "gap": int((df.CAM1.ge(4) & df.CAM2.le(3)).sum()),
    "bothFavourable": int((df.CAM1.ge(4) & df.CAM2.ge(4)).sum()),
}
assert pair == {"bothLower": 13, "reverse": 16, "gap": 45, "bothFavourable": 253}
fair_items = [f"FAI{i}" for i in range(1, 6)]
fair_count = df[fair_items].le(3).sum(axis=1)
assert int(fair_count.gt(0).sum()) == 137

voice_short = {"r": "Recognition / feedback", "d": "Career / learning", "v": "Voice / follow-through",
               "f": "Fair treatment / consistency", "p": "Role clarity / processes", "w": "Workload / boundaries"}
voice = [{"code": key, "label": label, "n": int(topics.loc[key, "request_record_n"])}
         for key, label in voice_short.items()]
voice.sort(key=lambda row: -row["n"])

# Step 7 prioritisation results (notebook): aggregate tables only.
tables = ROOT / "reports/tables"
model = pd.read_csv(tables / "driver_model_summary.csv", index_col=0)["value"]
nva = pd.read_csv(tables / "named_vs_anonymous.csv", index_col=0)
hr = pd.read_csv(tables / "hr_priority_counts.csv", index_col=0)
hot = pd.read_csv(tables / "group_hotspots.csv").set_index("group")
hr_short = {"Listening to employees and their concerns": "Listening to concerns", "Help employees progress in their careers": "Career progression",
            "Improve employee benefits and facilities": "Benefits & facilities", "Help resolve employee problems": "Resolving problems",
            "Recognising and appreciating good work": "Recognising good work", "Supporting employees when they need help": "Support when needed",
            "Making rules and processes simple": "Simpler rules & processes", "Being available and easy to approach": "Being approachable",
            "Employee activities and engagement": "Activities & engagement", "Keeping employees informed": "Keeping people informed"}
assert int(hr["respondents"].iloc[0]) == 67 and set(hr.index) == set(hr_short)
priorities = {
    "stayAll": float(df.PRI3.ge(4).mean() * 100), "stayAnonymous": float(nva.loc["Anonymous", "stay_3_5_yrs_fav"]),
    "anonymousN": int(nva.loc["Anonymous", "n"]), "fairnessShare": float(model["dim_FAI"]), "r2": float(model["actionable_r2"]),
    "hrChoice": [{"label": hr_short[k], "n": int(r.respondents), "listen": k in ("Listening to employees and their concerns", "Keeping employees informed")}
                 for k, r in hr.iterrows()],
    "listenHrPct": float(hr.loc[["Listening to employees and their concerns", "Keeping employees informed"], "pct"].sum()),
    "customerServiceCross": float(hot.loc["Customer Service", "Cross-team"]),
}
payload = {
    "meta": {"organisation": "Safewater Lines", "survey": "Your Voice",
        "analysisSnapshot": "30 October 2026", "responsesAsOf": "21 October",
        "sourceHash": hashlib.sha256(source.read_bytes()).hexdigest(),
        "recordN": len(df), "itemN": len(items), "minimumGroupN": MIN_N,
        "eligibleWorkforce": None, "commentN": 1892, "reviewedCommentN": 568,
        "remainingContextN": 75, "independentlyValidated": False},
    "filters": {"departments": departments, "tenures": TENURES},
    "cohorts": cohorts, "focus": {"pair": pair,
        "crossGapPP": float((df.CAM1.ge(4).mean() - df.CAM2.ge(4).mean()) * 100),
        "fairAnyN": int(fair_count.gt(0).sum()), "fairTwoN": int(fair_count.ge(2).sum()),
        "fairNoConcernN": 73, "voice": voice, "priorities": priorities},
}
# The browser package is an aggregate snapshot: never copy the source CSV or comments.
encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
(DIST / "data.js").write_text("window.DASHBOARD_DATA = " + encoded + ";\n")
index = (HERE / "src/index.html").read_text()
(DIST / "index.html").write_text(index.replace('src="../dist/data.js"', 'src="data.js"'))
for name in ["styles.css", "app.js", "assistant.css", "assistant.js"]:
    shutil.copyfile(HERE / "src" / name, DIST / name)
print(f"Built {len(cohorts)} aggregate filter combinations in {DIST}; no raw survey records or comments packaged.")
