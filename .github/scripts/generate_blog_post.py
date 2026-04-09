#!/usr/bin/env python3
"""Generate SparkOS Docusaurus blog post from GitHub issue payload.

- Uses LLM when OPENAI_API_KEY is present.
- Falls back to deterministic generation when unavailable.
- Writes one .mdx file under blog/ and emits workflow outputs.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import textwrap
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ALLOWED_AUTHORS = {"sparkteam", "releasebot"}
ALLOWED_TAGS = {"release", "changelog", "security", "hotfix", "maintenance", "misc"}
DEFAULT_SUPPORT = [
    "Community: https://t.me/SparkOSCommunity",
    "Channel: https://t.me/SparkOSChannel",
    "GitHub: https://github.com/Spark-Rom",
]


FIELD_ALIASES = {
    "release type": "release_type",
    "version": "version",
    "summary": "summary",
    "highlights": "highlights",
    "detailed changelog": "detailed_changelog",
    "known issues": "known_issues",
    "security notes": "security_notes",
    "support links": "support_links",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_issue_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    pattern = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(body or ""))
    for idx, m in enumerate(matches):
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        raw_key = m.group(1).strip().lower()
        key = FIELD_ALIASES.get(raw_key)
        if not key:
            continue
        value = (body[start:end] or "").strip()
        value = value.replace("_No response_", "").strip()
        sections[key] = value
    return sections


def to_kebab(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    s = re.sub(r"-+", "-", s)
    return s or "sparkos-release"


def lines_to_bullets(value: str, fallback: str = "TBD") -> list[str]:
    lines = [ln.strip(" -\t") for ln in (value or "").splitlines() if ln.strip()]
    if not lines:
        return [fallback]
    return lines


def pick_tags(release_type: str, security_notes: str) -> list[str]:
    r = (release_type or "").lower()
    tags: list[str]
    if "hotfix" in r:
        tags = ["hotfix", "changelog"]
    elif "maintenance" in r:
        tags = ["maintenance"]
    elif "security" in r:
        tags = ["security", "changelog"]
    elif "misc" in r:
        tags = ["misc"]
    else:
        tags = ["release", "changelog"]

    if security_notes and security_notes.strip().lower() not in {"none", "none."} and "security" not in tags:
        tags.append("security")

    tags = [t for t in tags if t in ALLOWED_TAGS]
    return tags[:3] or ["misc"]


def pick_title(version: str, release_type: str) -> str:
    v = (version or "TBD").strip()
    r = (release_type or "").strip().lower()
    now = dt.datetime.utcnow()
    month_year = now.strftime("%B %Y")

    if "hotfix" in r:
        extra = release_type.strip() if release_type else "Hotfix"
        return f"SparkOS {v} {extra}".strip()
    if "maintenance" in r:
        return f"SparkOS {month_year} Maintenance Update"
    if "security" in r:
        return f"SparkOS Security Update - {month_year}"
    if "misc" in r:
        return f"SparkOS {v} Project Update"
    return f"SparkOS {v} - Official Release Announcement"


def build_mdx(payload: dict[str, Any]) -> str:
    def bullets(items: list[str]) -> str:
        return "\n".join(f"- {x}" for x in items)

    return (
        f"---\n"
        f"slug: {payload['slug']}\n"
        f"title: {payload['title']}\n"
        f"authors: [{', '.join(payload['authors'])}]\n"
        f"tags: [{', '.join(payload['tags'])}]\n"
        f"---\n\n"
        f"{payload['summary']}\n\n"
        f"{{/* truncate */}}\n\n"
        f"## Highlights\n\n"
        f"{bullets(payload['highlights'])}\n\n"
        f"## Detailed Changelog\n\n"
        f"{bullets(payload['detailed_changelog'])}\n\n"
        f"## Known Issues\n\n"
        f"{bullets(payload['known_issues'])}\n\n"
        f"## Support / Reporting\n\n"
        f"{bullets(payload['support_links'])}\n"
    )


def call_openai(
    model: str, api_key: str, guideline_text: str, issue_data: dict[str, Any]
) -> tuple[dict[str, Any] | None, str | None]:
    prompt = {
        "role": "system",
        "content": (
            "You generate a single Docusaurus .mdx blog post payload in JSON only. "
            "No markdown fences, no prose. Follow this guide strictly:\n\n"
            f"{guideline_text}\n\n"
            "Output JSON schema keys exactly: "
            "slug,title,authors,tags,summary,highlights,detailed_changelog,known_issues,support_links,missing_fields"
        ),
    }

    user = {
        "role": "user",
        "content": json.dumps(issue_data, ensure_ascii=False, indent=2),
    }

    req_body = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [prompt, user],
    }

    req = urllib.request.Request(
        url="https://api.openai.com/v1/chat/completions",
        data=json.dumps(req_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode("utf-8")
            data = json.loads(raw)
            content = data["choices"][0]["message"]["content"]
            return json.loads(content), None
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8")
        except Exception:
            body = "<unable to read response body>"
        return None, f"HTTP {e.code}: {body}"
    except (urllib.error.URLError, KeyError, ValueError, json.JSONDecodeError) as e:
        return None, str(e)


def sanitize_payload(payload: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    out = dict(fallback)

    if isinstance(payload.get("slug"), str) and payload["slug"].strip():
        out["slug"] = to_kebab(payload["slug"])

    if isinstance(payload.get("title"), str) and payload["title"].strip():
        out["title"] = payload["title"].strip()

    authors = payload.get("authors")
    if isinstance(authors, list):
        valid_authors = [a for a in authors if isinstance(a, str) and a in ALLOWED_AUTHORS]
        if valid_authors:
            out["authors"] = valid_authors[:2]

    tags = payload.get("tags")
    if isinstance(tags, list):
        valid_tags = [t for t in tags if isinstance(t, str) and t in ALLOWED_TAGS]
        if valid_tags:
            out["tags"] = list(dict.fromkeys(valid_tags))[:3]

    if isinstance(payload.get("summary"), str) and payload["summary"].strip():
        out["summary"] = payload["summary"].strip()

    for k in ["highlights", "detailed_changelog", "known_issues", "support_links"]:
        arr = payload.get(k)
        if isinstance(arr, list):
            cleaned = [x.strip() for x in arr if isinstance(x, str) and x.strip()]
            if cleaned:
                out[k] = cleaned

    mf = payload.get("missing_fields")
    if isinstance(mf, list):
        out["missing_fields"] = [x for x in mf if isinstance(x, str) and x.strip()]

    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-path", required=True)
    parser.add_argument("--guidelines", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    event = read_json(Path(args.event_path))
    issue = event.get("issue") or {}
    issue_number = issue.get("number")
    issue_body = issue.get("body") or ""
    issue_url = issue.get("html_url") or ""

    fields = parse_issue_sections(issue_body)

    missing_fields: list[str] = []
    for k in ["release_type", "version", "summary", "highlights", "detailed_changelog", "known_issues"]:
        if not fields.get(k):
            missing_fields.append(k)

    release_type = fields.get("release_type", "Misc Announcement")
    version = fields.get("version", "TBD")

    fallback = {
        "slug": to_kebab(pick_title(version, release_type)),
        "title": pick_title(version, release_type),
        "authors": ["sparkteam"],
        "tags": pick_tags(release_type, fields.get("security_notes", "")),
        "summary": fields.get("summary", "TBD"),
        "highlights": lines_to_bullets(fields.get("highlights", ""), "TBD"),
        "detailed_changelog": lines_to_bullets(fields.get("detailed_changelog", ""), "TBD"),
        "known_issues": lines_to_bullets(fields.get("known_issues", ""), "None."),
        "support_links": lines_to_bullets(fields.get("support_links", ""), "") or DEFAULT_SUPPORT,
        "missing_fields": missing_fields,
    }
    if not fallback["support_links"] or fallback["support_links"] == [""]:
        fallback["support_links"] = DEFAULT_SUPPORT

    guide_text = Path(args.guidelines).read_text(encoding="utf-8")

    llm_payload = None
    llm_error = None
    generation_mode = "fallback"
    api_key = os.environ.get("OPENAI_API_KEY", "")
    model = os.environ.get("OPENAI_MODEL") or "gpt-5.4-mini"

    print(f"OPENAI_API_KEY present: {'yes' if bool(api_key) else 'no'}")
    print(f"OPENAI_MODEL: {model}")

    if api_key:
        llm_payload, llm_error = call_openai(
            model=model,
            api_key=api_key,
            guideline_text=guide_text,
            issue_data={
                "issue_number": issue_number,
                "issue_url": issue_url,
                "fields": fields,
                "date_utc": dt.datetime.utcnow().strftime("%Y-%m-%d"),
            },
        )
        if llm_payload:
            generation_mode = "ai"
            print("Generation mode: ai")
        else:
            print(f"Generation mode: fallback (LLM call failed: {llm_error})")
    else:
        print("Generation mode: fallback (no API key)")

    payload = sanitize_payload(llm_payload or {}, fallback)

    payload["highlights"] = payload["highlights"] or ["TBD"]
    payload["detailed_changelog"] = payload["detailed_changelog"] or ["TBD"]
    payload["known_issues"] = payload["known_issues"] or ["None."]
    payload["support_links"] = payload["support_links"] or DEFAULT_SUPPORT

    date_prefix = dt.datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"{date_prefix}-{to_kebab(payload['slug'])}.mdx"
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    out_path.write_text(build_mdx(payload), encoding="utf-8")

    pr_title = f"blog: add {payload['slug']} release post"
    missing_lines = payload.get("missing_fields", [])
    missing_block = "".join(f"- {m}\n" for m in missing_lines) if missing_lines else "- None"
    pr_body = textwrap.dedent(
        f"""\
        Automated blog post generated from issue #{issue_number}.

        Closes #{issue_number}

        - Source issue: {issue_url}
        - Generated slug: `{payload['slug']}`
        - Selected tags: `{', '.join(payload['tags'])}`
        - Generation mode: `{generation_mode}`

        Missing/TBD fields detected:
        {missing_block}
        """
    )

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"post_path={out_path.as_posix()}\n")
            f.write(f"branch_slug={to_kebab(payload['slug'])}\n")
            f.write(f"pr_title={pr_title}\n")
            f.write(f"generation_mode={generation_mode}\n")
            f.write("pr_body<<EOF\n")
            f.write(pr_body)
            f.write("EOF\n")

    print(f"Generated: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
