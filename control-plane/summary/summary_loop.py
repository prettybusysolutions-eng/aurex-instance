import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import schedule

REPORTS_DIR = Path(os.environ.get("REPORTS_DIR", "./reports"))
SOURCES_FILE = Path(os.environ.get("SOURCES_FILE", "./sources.json"))
KEYWORDS = [
    "incentivized testnet",
    "developer grant",
    "node rewards",
    "early access",
]


def load_sources():
    if not SOURCES_FILE.exists():
        return []
    try:
        return json.loads(SOURCES_FILE.read_text())
    except Exception:
        return []


def fetch_text(url: str):
    try:
        response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        return response.text[:50000]
    except Exception as exc:
        return f"ERROR: {exc}"


def keyword_hits(text: str):
    lowered = text.lower()
    return [kw for kw in KEYWORDS if kw in lowered]


def build_summary():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    sources = load_sources()
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "market_alpha": [],
        "flagged_entries": [],
        "tasks_completed": [],
        "notes": [
            "This summary tracks official public sources only.",
            "No autonomous reward farming or claim automation is included.",
        ],
    }

    for source in sources:
        url = source.get("url")
        if not url:
            continue
        content = fetch_text(url)
        preview = content[:1500]
        hits = keyword_hits(content)
        entry = {
            "label": source.get("label", url),
            "url": url,
            "kind": source.get("kind", "unknown"),
            "content_preview": preview,
            "keyword_hits": hits,
        }
        summary["market_alpha"].append(entry)
        if hits:
            summary["flagged_entries"].append(entry)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    (REPORTS_DIR / f"summary-{timestamp}.json").write_text(json.dumps(summary, indent=2))
    (REPORTS_DIR / "summary-latest.json").write_text(json.dumps(summary, indent=2))

    alpha_lines = [
        "# Alpha Report",
        "",
        f"Generated: {summary['generated_at']}",
        "",
        "## Top flagged opportunities",
        "",
    ]
    if summary["flagged_entries"]:
        for item in summary["flagged_entries"][:3]:
            alpha_lines.extend(
                [
                    f"### {item['label']}",
                    f"- URL: {item['url']}",
                    f"- Keyword hits: {', '.join(item['keyword_hits'])}",
                    f"- Preview: {item['content_preview'][:400].replace(chr(10), ' ')}",
                    "",
                ]
            )
    else:
        alpha_lines.extend(
            [
                "No keyword-matching official opportunities were found in the current source set.",
                "",
                "## Monitored lanes",
                "",
            ]
        )
        for item in summary["market_alpha"][:3]:
            alpha_lines.extend(
                [
                    f"### {item['label']}",
                    f"- URL: {item['url']}",
                    f"- Keyword hits: none",
                    "",
                ]
            )

    (REPORTS_DIR / "alpha_report.md").write_text("\n".join(alpha_lines))


def main():
    build_summary()
    schedule.every(24).hours.do(build_summary)
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
