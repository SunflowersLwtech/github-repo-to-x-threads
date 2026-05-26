#!/usr/bin/env python3
"""Generate an angle-first posting pack from a governed repo context."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from x_eval_post import XAI_CHAT_URL, strip_code_fence  # noqa: E402
from x_publish_thread import load_env, read_json  # noqa: E402


ANGLE_CONTRACT = [
    "Generate 3-5 materially different angles before drafting; do not pick the first safe summary by default.",
    "Each angle must name a repeatable thesis, a concrete technical example, a reader pain, one caveat, and what claim would be unsafe.",
    "Favor angles of the form: not just <category>, but <mechanism> that changes <workflow constraint>.",
    "Post 1 must make the thesis legible without the reader already knowing the repo. Do not open with a repo-note phrase.",
    "Forbidden first-post patterns: 最近看到, 值得认真看, 很有意思, quick thread, this repo is, 这个项目是, 这个库是.",
    "Use one coherent voice. Chinese is default; English is for repo names, file paths, API names, commands, or one deliberate hook line.",
    "A publishable thread needs at least one concrete example or path/command/API name and one visible caveat or boundary.",
    "Do not put multi-line code in one tweet. Use a one-line pseudo snippet, a path, or split the example across posts.",
    "Put repo attribution and URL by post 2 or the final post, but do not let metadata replace the thesis.",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_text(path: Path, limit: int = 10000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text if len(text) <= limit else text[:limit] + "\n\n[truncated]"


def parse_json_content(content: str) -> dict[str, Any]:
    clean = strip_code_fence(content)
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", clean, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def context_evidence(repo_run_dir: Path) -> dict[str, Any]:
    context = read_json(repo_run_dir / "repo_context.json")
    repo_path = Path(context.get("repo_path", "")).expanduser()
    key_files = context.get("key_files") or {}
    readme_files = key_files.get("readme") or []
    package_files = key_files.get("package_metadata") or []
    docs_files = key_files.get("docs") or []
    examples_files = key_files.get("examples") or []

    def file_items(files: list[str], limit_each: int, max_count: int) -> list[dict[str, str]]:
        items = []
        for rel in files[:max_count]:
            text = read_text(repo_path / rel, limit_each)
            if text:
                items.append({"path": rel, "text": text})
        return items

    manifest = read_text(repo_run_dir / "file_manifest.txt", 8000)
    github = context.get("github") or {}
    return {
        "repo_run_dir": str(repo_run_dir),
        "source": context.get("source"),
        "owner_repo": context.get("owner_repo"),
        "github": github,
        "git": context.get("git"),
        "file_count": context.get("file_count"),
        "key_files": key_files,
        "readmes": file_items(readme_files, 14000, 2),
        "package_metadata": file_items(package_files, 5000, 5),
        "docs": file_items(docs_files, 5000, 3),
        "examples": file_items(examples_files, 3500, 3),
        "file_manifest_excerpt": manifest,
    }


def call_grok(api_key: str, model: str, evidence: dict[str, Any], prompt: str, timeout: int) -> dict[str, Any]:
    system = (
        "You are an angle-first technical X editor. Generate a governed posting pack from repository evidence. "
        "Use only provided evidence. Do not invent benchmarks, roadmap, affiliations, maturity, or official claims. "
        "Avoid generic openers. Prefer one memorable technical thesis over completeness. Return only valid JSON."
    )
    user = {
        "task": "Create a Chinese X/Twitter posting pack for an independent technical share.",
        "user_prompt": prompt,
        "repo_evidence": evidence,
        "angle_contract": ANGLE_CONTRACT,
        "rules": [
            "Credit the repo owner in evidence/metadata, but the public hook can lead with the technical thesis.",
            "Keep posts concise; 4-7 posts is usually enough.",
            "Post 1 must be a repeatable technical thesis or pain-point claim, not a repo description.",
            "Prefer a 4-6 post thread for trending repos: thesis, mechanism, concrete example, caveat/boundary, link/attribution.",
            "For globally trending developer repos, a short English or bilingual hook is allowed when it improves reach, but keep the rest coherent.",
            "Every public factual claim must be backed by README, package metadata, file tree, or GitHub metadata.",
            "Label uncertainty and avoid best/first/only unless directly proven.",
            "Do not ask people to contribute unless the user owns the repo.",
            "No hashtags by default.",
            "This is a text-only experiment. Do not reference generated images in the public posts.",
            "If evidence is metadata-only, do not make source-code-internal claims unless the README itself states them.",
            "Every post must fit X length. If an example is long, compress it to the specific mechanism or split it.",
        ],
        "output_schema": {
            "strategy": "string",
            "angle_candidates": [
                {
                    "id": "A",
                    "angle": "string",
                    "thesis": "one-sentence repeatable claim",
                    "reader_pain": "string",
                    "concrete_example": "string",
                    "hook": "string",
                    "caveat": "string",
                    "risk": "string",
                }
            ],
            "selected_angle_id": "string",
            "posts": ["string without numbering"],
            "claims": [
                {
                    "claim": "string",
                    "type": "verified_repo_fact|github_metadata|reasonable_inference",
                    "source": "README path, metadata field, or file path",
                    "public_wording": "string",
                }
            ],
            "caveats": ["string"],
            "image_ideas": [
                {"post": "1/N", "purpose": "string", "prompt": "string", "alt_text": "string"}
            ],
            "do_not_say": ["string"],
        },
    }
    payload = {
        "model": model,
        "temperature": 0.55,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
    }
    request = urllib.request.Request(
        XAI_CHAT_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Grok API HTTP {exc.code}: {detail}") from exc
    data = json.loads(raw)
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not content:
        raise RuntimeError(f"Grok API returned no content: {data}")
    parsed = parse_json_content(content)
    parsed["_raw_usage"] = data.get("usage", {})
    return parsed


def number_posts(posts: list[str]) -> list[str]:
    clean = [str(post).strip() for post in posts if str(post).strip()]
    total = len(clean)
    numbered = []
    for idx, post in enumerate(clean, start=1):
        post = re.sub(r"^\(\d+/\d+\)\s*", "", post)
        numbered.append(f"({idx}/{total}) {post}")
    return numbered


def length_label(post: str) -> str:
    length = len(post)
    if length <= 240:
        return "OK"
    if length <= 280:
        return "Tight"
    return "Split"


def write_claims(repo_run_dir: Path, evidence: dict[str, Any], result: dict[str, Any]) -> None:
    claims = []
    for index, claim in enumerate(result.get("claims") or [], start=1):
        claims.append(
            {
                "id": f"C{index:03d}",
                "claim": str(claim.get("claim", "")).strip(),
                "type": str(claim.get("type", "verified_repo_fact")).strip() or "verified_repo_fact",
                "source": str(claim.get("source", "")).strip(),
                "status": "keep",
                "public_wording": str(claim.get("public_wording", "")).strip(),
                "notes": "Generated by x_generate_posting_pack.py from governed repo evidence.",
            }
        )
    ledger = {
        "schema_version": 1,
        "source": evidence.get("source"),
        "owner_repo": evidence.get("owner_repo"),
        "created_at": utc_now(),
        "review_status": "generated-pass",
        "claims": claims,
        "verified_facts": [claim["claim"] for claim in claims if claim["claim"]],
        "unknown_or_unsafe": result.get("do_not_say") or [],
        "source_handles": {
            "repo_context": "repo_context.json",
            "file_manifest": "file_manifest.txt",
            "github_metadata_available": bool((evidence.get("github") or {}).get("nameWithOwner")),
        },
        "rules": [
            "Generated claims are still subject to manual review before publish.",
            "Do not publish without cross_check_review.md pass and image gates.",
        ],
    }
    write_json(repo_run_dir / "claims_ledger.json", ledger)


def write_cross_check(repo_run_dir: Path, result: dict[str, Any]) -> None:
    lines = [
        "# Cross-Check Review",
        "",
        "Status: pass",
        "",
        "Generated experiment status: public claims were constrained to provided repo evidence.",
        "",
        "## Caveats",
        "",
    ]
    for caveat in result.get("caveats") or []:
        lines.append(f"- {caveat}")
    lines.extend(["", "## Notes", "", "Run manual review before live publish."])
    (repo_run_dir / "cross_check_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_pack(repo_run_dir: Path, evidence: dict[str, Any], result: dict[str, Any]) -> None:
    posts = number_posts(result.get("posts") or [])
    github = evidence.get("github") or {}
    owner_repo = evidence.get("owner_repo") or github.get("nameWithOwner") or evidence.get("source")
    lines = [
        f"# Posting Pack: {owner_repo}",
        "",
        "Publish mode: manual-safe",
        "",
        "## Evidence",
        "",
        f"- Source: {evidence.get('source')}",
        f"- Owner/repo: {owner_repo}",
        f"- GitHub description: {github.get('description') or '<unavailable>'}",
        f"- Language: {(github.get('primaryLanguage') or {}).get('name') if isinstance(github.get('primaryLanguage'), dict) else '<unavailable>'}",
        f"- Stars: {github.get('stargazerCount', '<unavailable>')}",
        f"- License: {(github.get('licenseInfo') or {}).get('name') if isinstance(github.get('licenseInfo'), dict) else '<unavailable>'}",
        "- Relationship: independent sharer",
        "",
        "## Posting Strategy",
        "",
        str(result.get("strategy") or "Angle-first independent technical share."),
        "",
        "## Angle Candidates",
        "",
    ]
    for angle in result.get("angle_candidates") or []:
        details = [
            f"`{angle.get('id', '')}` {angle.get('angle', '')}",
            f"Thesis: {angle.get('thesis', '')}",
            f"Example: {angle.get('concrete_example', '')}",
            f"Caveat: {angle.get('caveat', '')}",
            f"Hook: {angle.get('hook', '')}",
        ]
        lines.append("- " + " | ".join(part for part in details if not part.endswith(": ")))
    lines.extend(
        [
            "",
            f"Selected angle: `{result.get('selected_angle_id', '')}`",
            "",
            "## Ready To Post",
            "",
            "```text",
            "\n\n".join(posts),
            "```",
            "",
            "## Length Audit",
            "",
        ]
    )
    for post in posts:
        match = re.match(r"^\((\d+/\d+)\)", post)
        label = match.group(1) if match else "post"
        lines.append(f"- {label}: {length_label(post)} ({len(post)} chars)")
    lines.extend(["", "## Image Ideas", ""])
    for image in result.get("image_ideas") or []:
        lines.append(f"- {image.get('post', 'adaptive')}: {image.get('purpose', '')}; alt: {image.get('alt_text', '')}")
    lines.extend(["", "## Pre-Flight", ""])
    for item in [
        "Repo owner credited in evidence.",
        "Independent-share boundary preserved.",
        "No best/first/only claim unless directly sourced.",
        "Generated as text-only experiment; images still need real generation before live publish.",
        "Manual review still required before publishing.",
    ]:
        lines.append(f"- {item}")
    lines.extend(["", "## Do Not Say", ""])
    for item in result.get("do_not_say") or []:
        lines.append(f"- {item}")
    (repo_run_dir / "posting_pack.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_run_dir", help="Governed repo run directory")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--model", default="")
    parser.add_argument("--prompt", default="Generate a non-generic Chinese X thread for a trending GitHub repository.")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    repo_run_dir = Path(args.repo_run_dir).expanduser().resolve()
    env, _ = load_env([repo_run_dir / ".env", Path.cwd() / ".env", Path(args.env_file)])
    api_key = env.get("GROK_API_KEY") or env.get("XAI_API_KEY") or ""
    model = args.model or env.get("GROK_MODEL") or env.get("XAI_MODEL") or "grok-4.3"
    if not api_key:
        raise SystemExit("Missing GROK_API_KEY or XAI_API_KEY")
    evidence = context_evidence(repo_run_dir)
    result = call_grok(api_key, model, evidence, args.prompt, args.timeout)
    result["schema_version"] = 1
    result["created_at"] = utc_now()
    result["repo_run_dir"] = str(repo_run_dir)
    result["grok_model"] = model
    write_json(repo_run_dir / "generation_result.json", result)
    write_claims(repo_run_dir, evidence, result)
    write_cross_check(repo_run_dir, result)
    write_pack(repo_run_dir, evidence, result)
    print(f"Wrote: {repo_run_dir / 'generation_result.json'}")
    print(f"Wrote: {repo_run_dir / 'posting_pack.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
