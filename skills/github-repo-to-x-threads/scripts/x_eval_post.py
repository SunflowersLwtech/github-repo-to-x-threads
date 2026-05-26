#!/usr/bin/env python3
"""Score a governed posting pack before publishing to X."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from x_publish_thread import extract_ready_to_post, load_env, read_json  # noqa: E402


XAI_CHAT_URL = "https://api.x.ai/v1/chat/completions"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


MEDIA_FEEDBACK_RE = re.compile(r"(image|images|media|screenshot|diagram|visual|GPT|图片|截图|配图|视觉)", re.I)


def strip_thread_number(post: str) -> str:
    return re.sub(r"^\(\d+/\d+\)\s*", "", post).strip()


def load_strategy_decision(repo_run_dir: Path) -> dict[str, Any]:
    for parent in [repo_run_dir, *repo_run_dir.parents]:
        path = parent / "strategy_decision.json"
        if path.exists():
            return read_json(path)
    return {}


def cross_check_status(repo_run_dir: Path) -> str:
    path = repo_run_dir / "cross_check_review.md"
    if not path.exists():
        return "missing"
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    if "status: pass" in text:
        return "pass"
    if "status: block" in text:
        return "block"
    if "status: revise" in text:
        return "revise"
    return "unknown"


def claims_summary(repo_run_dir: Path) -> dict[str, Any]:
    path = repo_run_dir / "claims_ledger.json"
    if not path.exists():
        return {"exists": False, "claim_count": 0, "unsafe_count": 0, "needs_source_count": 0}
    data = read_json(path)
    claims = data.get("claims") if isinstance(data.get("claims"), list) else []
    verified = data.get("verified_facts") if isinstance(data.get("verified_facts"), list) else []
    unsafe = data.get("unknown_or_unsafe") if isinstance(data.get("unknown_or_unsafe"), list) else []
    needs_source = [claim for claim in claims if str(claim.get("status", "")).lower() == "needs_source"]
    placeholder = [claim for claim in claims if not str(claim.get("claim", "")).strip()]
    return {
        "exists": True,
        "claim_count": len(claims) + len(verified),
        "verified_fact_count": len(verified),
        "unsafe_count": len(unsafe),
        "needs_source_count": len(needs_source),
        "placeholder_count": len(placeholder),
    }


def image_summary(repo_run_dir: Path) -> dict[str, Any]:
    path = repo_run_dir / "images_manifest.json"
    if not path.exists():
        return {"exists": False, "image_count": 0, "actual_count": 0, "approved_count": 0, "gpt_count": 0}
    data = read_json(path)
    images = data.get("images") if isinstance(data.get("images"), list) else []
    actual = [image for image in images if image.get("path")]
    approved = [image for image in images if image.get("review_status") == "approved"]
    gpt = [
        image
        for image in images
        if str(image.get("source_type", "")).startswith("gpt_") or "gpt-image" in str(image.get("model", ""))
    ]
    missing_alt = [image for image in actual if not image.get("alt_text")]
    missing_disclosure = [image for image in actual if not image.get("disclosure")]
    missing_file = [image for image in actual if not (repo_run_dir / str(image.get("path"))).exists()]
    return {
        "exists": True,
        "image_count": len(images),
        "actual_count": len(actual),
        "approved_count": len(approved),
        "gpt_count": len(gpt),
        "missing_alt_count": len(missing_alt),
        "missing_disclosure_count": len(missing_disclosure),
        "missing_file_count": len(missing_file),
    }


def text_features(posts: list[str]) -> dict[str, Any]:
    full = "\n\n".join(posts)
    first = posts[0] if posts else ""
    first_body = strip_thread_number(first)
    lengths = [len(post) for post in posts]
    urls = re.findall(r"https?://\S+", full)
    hashtags = re.findall(r"(?<!\w)#\w+", full)
    mentions = re.findall(r"(?<!\w)@\w+", full)
    questions = full.count("?") + full.count("？")
    cta_words = re.findall(r"\b(follow|retweet|like|share|subscribe|dm|click|join)\b", full, flags=re.I)
    ai_slop = re.findall(
        r"\b(game[- ]changer|revolutionary|future is here|unlock|supercharge|10x|best|only|ultimate)\b",
        full,
        flags=re.I,
    )
    caveat_terms = re.findall(
        r"(caveat|limitation|requires|depends on|experimental|not affiliated|not official|not production|not verified|not a benchmark|unofficial|非官方|不是官方|风险|限制|边界|我不是|个人|注意|无关|合规|社区项目|仅|只看|未验证|不代表|前提|依赖|必须|否则|实验|复核|不保证)",
        full,
        flags=re.I,
    )
    generic_openers = re.findall(
        r"^(最近|刚看|值得|很有意思|interesting|worth reading|quick thread|this repo is|这个(项目|库|repo)(是|其实|主要)?)",
        first_body,
        flags=re.I,
    )
    repo_note_openers = re.findall(
        r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\s+(is|是|的|把|证明|shows|turns)",
        first_body,
        flags=re.I,
    )
    template_phrases = re.findall(
        r"(核心问题很直接|技术上.*practical|更有意思|caveat.*重要|我的个人 takeaway|下面是|pre-flight)",
        full,
        flags=re.I,
    )
    summary_phrases = re.findall(
        r"(是一个|是个|它做的是|主要(提供|支持|包含)|提供了?|支持|内置|包含|works with|supports|includes|features|allows you to|lets you)",
        full,
        flags=re.I,
    )
    concrete_markers = re.findall(
        r"(\b[A-Z][A-Za-z0-9_.-]{2,}\b|Qwen|LiveCodeBench|best@k|pass@1|GRPO|VPO|ToolRL|MuSiQue|EUREQA|test case|unit test|verifier|代码题|multi-hop|工具)",
        full,
        flags=re.I,
    )
    contrast_markers = re.findall(r"(不是.*而是|not .* but|instead of|rather than|反而|但|but|however)", full, flags=re.I)
    thesis_markers = re.findall(
        r"(不是.{0,36}而是|not .{0,48} but|instead of|rather than|关键设计|核心设计|真正.{0,16}是|问题.{0,16}不是|把.{1,36}变成|turns? .{1,48} into|changes? .{1,48} into|>| vs\.? |versus|trade[- ]off|constraint)",
        full,
        flags=re.I,
    )
    first_thesis_markers = re.findall(
        r"(不是.{0,36}而是|not .{0,48} but|instead of|rather than|关键设计|核心设计|真正.{0,16}是|问题.{0,16}不是|把.{1,36}变成|turns? .{1,48} into|changes? .{1,48} into|>| vs\.? |versus|trade[- ]off|constraint)",
        first_body,
        flags=re.I,
    )
    example_markers = re.findall(
        r"(例如|比如|举例|例子|真实映射|before/after|diff|example|->|→|=>|`[^`]+`|/[A-Za-z0-9_.-]+|[A-Za-z0-9_.-]+\.(json|toml|ya?ml|py|ts|tsx|js|md)|\bnpx\b|\bpip\b|\bcargo\b|\bgo\b|\bT\d{4}\b)",
        full,
        flags=re.I,
    )
    first_example_markers = re.findall(
        r"(例如|比如|举例|例子|before/after|diff|example|->|→|=>|`[^`]+`|/[A-Za-z0-9_.-]+|[A-Za-z0-9_.-]+\.(json|toml|ya?ml|py|ts|tsx|js|md)|\bnpx\b|\bpip\b|\bcargo\b|\bgo\b|\bT\d{4}\b)",
        first_body,
        flags=re.I,
    )
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", full))
    english_function_words = re.findall(
        r"\b(the|and|for|with|without|this|that|why|how|what|but|not|just|because|into|from|to|of|in|on)\b",
        full,
        flags=re.I,
    )
    voice_drift = cjk_chars > 40 and len(english_function_words) > max(5, len(posts) * 2)
    total_chars = sum(lengths)
    return {
        "post_count": len(posts),
        "lengths": lengths,
        "total_chars": total_chars,
        "max_length": max(lengths) if lengths else 0,
        "over_280_count": sum(1 for length in lengths if length > 280),
        "under_45_count": sum(1 for length in lengths if length < 45),
        "url_count": len(urls),
        "root_url_count": len(re.findall(r"https?://\S+", first)),
        "hashtag_count": len(hashtags),
        "mention_count": len(mentions),
        "question_count": questions,
        "cta_count": len(cta_words),
        "ai_slop_count": len(ai_slop),
        "caveat_count": len(caveat_terms),
        "generic_opener_count": len(generic_openers),
        "repo_note_opener_count": len(repo_note_openers),
        "template_phrase_count": len(template_phrases),
        "summary_phrase_count": len(summary_phrases),
        "concrete_marker_count": len(concrete_markers),
        "contrast_marker_count": len(contrast_markers),
        "thesis_marker_count": len(thesis_markers),
        "first_thesis_marker_count": len(first_thesis_markers),
        "example_marker_count": len(example_markers),
        "first_example_marker_count": len(first_example_markers),
        "english_function_word_count": len(english_function_words),
        "voice_drift_count": int(voice_drift),
        "first_post_chars": len(first),
        "first_body_chars": len(first_body),
    }


def deterministic_scores(
    posts: list[str],
    cross_status: str,
    claims: dict[str, Any],
    images: dict[str, Any],
    features: dict[str, Any],
) -> dict[str, float]:
    claim_safety = 0.45
    if cross_status == "pass":
        claim_safety = 0.95
    elif cross_status == "revise":
        claim_safety = 0.45
    elif cross_status == "block":
        claim_safety = 0.05
    if not claims.get("exists"):
        claim_safety -= 0.25
    if claims.get("needs_source_count", 0):
        claim_safety -= 0.25
    if claims.get("placeholder_count", 0) and claims.get("verified_fact_count", 0) == 0:
        claim_safety -= 0.15

    hook_strength = 0.5
    if 80 <= features["first_post_chars"] <= 260:
        hook_strength += 0.18
    if features["root_url_count"] == 0:
        hook_strength += 0.05
    if features["first_thesis_marker_count"] > 0:
        hook_strength += 0.14
    if features["first_example_marker_count"] > 0:
        hook_strength += 0.07
    if features["caveat_count"] > 0:
        hook_strength += 0.03
    if re.search(r"值得|interesting|why|核心|问题|takeaway|不是|but|however", posts[0] if posts else "", flags=re.I):
        hook_strength += 0.12
    if features["generic_opener_count"]:
        hook_strength -= 0.16
    if features["repo_note_opener_count"]:
        hook_strength -= 0.12
    if features["summary_phrase_count"] >= max(3, features["post_count"]):
        hook_strength -= 0.08
    if features["first_body_chars"] < 70 and not features["first_thesis_marker_count"]:
        hook_strength -= 0.08
    if features["ai_slop_count"]:
        hook_strength -= min(0.25, 0.05 * features["ai_slop_count"])

    angle_freshness = 0.48
    if features["contrast_marker_count"] > 0:
        angle_freshness += 0.18
    if features["thesis_marker_count"] > 0:
        angle_freshness += 0.14
    if features["first_thesis_marker_count"] > 0:
        angle_freshness += 0.06
    if features["example_marker_count"] > 0:
        angle_freshness += 0.08
    if features["concrete_marker_count"] >= max(6, features["post_count"]):
        angle_freshness += 0.12
    if features["generic_opener_count"]:
        angle_freshness -= 0.18
    if features["repo_note_opener_count"]:
        angle_freshness -= 0.10
    if features["summary_phrase_count"] >= max(4, features["post_count"] + 1):
        angle_freshness -= 0.12
    if features["template_phrase_count"] > 2:
        angle_freshness -= min(0.22, features["template_phrase_count"] * 0.04)

    audience_fit = 0.58
    if re.search(r"\b(repo|paper|api|model|rl|agent|benchmark|代码|论文|开源|训练|搜索)\b", "\n".join(posts), flags=re.I):
        audience_fit += 0.2
    if features["post_count"] > 15:
        audience_fit -= 0.1

    specificity_density = 0.45
    specificity_density += min(0.28, features["concrete_marker_count"] * 0.018)
    specificity_density += min(0.14, features["example_marker_count"] * 0.035)
    if features["url_count"]:
        specificity_density += 0.04
    if features["template_phrase_count"] > 3:
        specificity_density -= 0.08

    bookmark_value = 0.5
    if features["caveat_count"] > 0:
        bookmark_value += 0.1
    if features["thesis_marker_count"] > 0 and features["example_marker_count"] > 0:
        bookmark_value += 0.10
    if re.search(r"\b(pattern|workflow|checklist|架构|方法|takeaway|结论|路径|rubric)\b", "\n".join(posts), flags=re.I):
        bookmark_value += 0.22

    reply_potential = 0.45 + min(0.2, features["question_count"] * 0.08)
    if features["cta_count"] > 2:
        reply_potential -= 0.08

    media_quality = 0.35
    if images.get("exists"):
        if images.get("actual_count", 0):
            media_quality += 0.25
        if images.get("gpt_count", 0):
            media_quality += 0.15
        if images.get("approved_count", 0) >= images.get("actual_count", 0) > 0:
            media_quality += 0.15
        media_quality -= 0.08 * images.get("missing_alt_count", 0)
        media_quality -= 0.08 * images.get("missing_disclosure_count", 0)
        media_quality -= 0.2 * images.get("missing_file_count", 0)

    structure_fit = 0.8
    if features["over_280_count"]:
        structure_fit -= min(0.45, 0.15 * features["over_280_count"])
    if features["post_count"] == 0:
        structure_fit = 0.0
    elif features["post_count"] > 14:
        structure_fit -= 0.1
    elif features["post_count"] < 4 and features["total_chars"] < 420:
        structure_fit -= 0.08
    if features["hashtag_count"] > 2:
        structure_fit -= 0.12
    if features["mention_count"] > 4:
        structure_fit -= 0.08

    voice_authenticity = 0.62
    if features["template_phrase_count"]:
        voice_authenticity -= min(0.30, features["template_phrase_count"] * 0.045)
    if features["generic_opener_count"]:
        voice_authenticity -= 0.12
    if features["repo_note_opener_count"]:
        voice_authenticity -= 0.08
    if features["summary_phrase_count"] >= max(4, features["post_count"] + 1):
        voice_authenticity -= 0.10
    if features["voice_drift_count"]:
        voice_authenticity -= 0.10
    if features["caveat_count"] and features["concrete_marker_count"] >= 6:
        voice_authenticity += 0.10
    if features["first_thesis_marker_count"] and features["example_marker_count"]:
        voice_authenticity += 0.06
    if features["cta_count"] > 1:
        voice_authenticity -= 0.08

    risk_control = 0.82
    if features["url_count"] > 3:
        risk_control -= 0.12
    if features["root_url_count"] > 1:
        risk_control -= 0.08
    if features["ai_slop_count"]:
        risk_control -= min(0.25, 0.05 * features["ai_slop_count"])
    if features["hashtag_count"] > 2:
        risk_control -= 0.12
    if not features["caveat_count"]:
        risk_control -= 0.05

    return {
        "claim_safety": clamp(claim_safety),
        "hook_strength": clamp(hook_strength),
        "angle_freshness": clamp(angle_freshness),
        "specificity_density": clamp(specificity_density),
        "audience_fit": clamp(audience_fit),
        "bookmark_value": clamp(bookmark_value),
        "reply_potential": clamp(reply_potential),
        "media_quality": clamp(media_quality),
        "structure_fit": clamp(structure_fit),
        "voice_authenticity": clamp(voice_authenticity),
        "risk_control": clamp(risk_control),
    }


WEIGHTS = {
    "claim_safety": 0.18,
    "hook_strength": 0.12,
    "angle_freshness": 0.14,
    "specificity_density": 0.12,
    "audience_fit": 0.08,
    "bookmark_value": 0.10,
    "reply_potential": 0.06,
    "media_quality": 0.08,
    "structure_fit": 0.05,
    "voice_authenticity": 0.04,
    "risk_control": 0.03,
}


def weighted_score(scores: dict[str, float]) -> float:
    return sum(scores[key] * weight for key, weight in WEIGHTS.items())


def grok_eval(
    api_key: str,
    model: str,
    posts: list[str],
    deterministic: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    system = (
        "You are a strict X/Twitter pre-publish evaluation agent for technical threads. "
        "Be harsh: a merely accurate, safe summary should usually score below 0.72. "
        "Score a pack as ready only if it has a sharp angle, concrete technical density, and a non-template voice. "
        "Score distribution potential and safety, but never treat engagement optimization as evidence. "
        "Return only valid JSON."
    )
    user = {
        "task": "Evaluate this governed X posting pack before publishing.",
        "rubric": list(WEIGHTS.keys()),
        "requirements": [
            "Return scores from 0.0 to 1.0.",
            "Penalize unsupported claims, generic AI hype, unclear hooks, weak caveats, and fake evidence.",
            "Penalize rigid template writing, generic openers, and posts that read like a paper abstract broken into numbered tweets.",
            "Reward concrete technical value, bookmark value, high-quality media, and responsible attribution.",
            "Reward a memorable thesis that a technical reader could repeat after reading the thread.",
            "Do not recommend unsafe manipulation or clickbait.",
        ],
        "text_only_eval_instruction": (
            "If deterministic_snapshot.text_only_eval is true, ignore media/image quality and do not suggest image fixes. "
            "Judge only copy, angle, claims, structure, and voice. Do not mention images, screenshots, diagrams, visuals, or media in top_fixes."
        ),
        "posts": posts,
        "deterministic_snapshot": deterministic,
        "output_schema": {
            "scores": {key: "float 0..1" for key in WEIGHTS},
            "final_score": "float 0..1",
            "decision": "ready|revise|block",
            "top_strengths": ["string"],
            "top_fixes": ["string"],
            "best_post_index": "integer",
            "weakest_post_index": "integer",
            "reasoning_summary": "string",
        },
    }
    payload = {
        "model": model,
        "temperature": 0.2,
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
    parsed = json.loads(strip_code_fence(content))
    parsed["_raw_usage"] = data.get("usage", {})
    return parsed


def merge_scores(rule_scores: dict[str, float], grok_result: dict[str, Any] | None) -> tuple[dict[str, float], float]:
    if not grok_result:
        final = weighted_score(rule_scores)
        return rule_scores, final
    grok_scores = grok_result.get("scores") if isinstance(grok_result.get("scores"), dict) else {}
    merged: dict[str, float] = {}
    for key in WEIGHTS:
        g = grok_scores.get(key)
        if isinstance(g, (int, float)) and not math.isnan(float(g)):
            merged[key] = clamp(0.55 * rule_scores[key] + 0.45 * float(g))
        else:
            merged[key] = rule_scores[key]
    return merged, weighted_score(merged)


def grok_weighted_score(grok_result: dict[str, Any] | None, text_only_eval: bool) -> float | None:
    if not grok_result:
        return None
    grok_scores = grok_result.get("scores") if isinstance(grok_result.get("scores"), dict) else {}
    if not grok_scores:
        return None
    semantic_scores: dict[str, float] = {}
    for key in WEIGHTS:
        value = grok_scores.get(key)
        if not isinstance(value, (int, float)) or math.isnan(float(value)):
            return None
        semantic_scores[key] = clamp(float(value))
    if text_only_eval:
        semantic_scores["media_quality"] = max(semantic_scores.get("media_quality", 0.0), 0.75)
    return weighted_score(semantic_scores)


def decision_from_score(final_score: float, scores: dict[str, float], ignore_media_gate: bool = False) -> str:
    if scores.get("claim_safety", 0) < 0.75:
        return "revise"
    if not ignore_media_gate and scores.get("media_quality", 0) < 0.65:
        return "revise"
    if scores.get("angle_freshness", 0) < 0.62:
        return "revise"
    if scores.get("specificity_density", 0) < 0.65:
        return "revise"
    if scores.get("structure_fit", 0) <= 0.65:
        return "revise"
    if scores.get("voice_authenticity", 0) < 0.58:
        return "revise"
    if final_score >= 0.80:
        return "ready"
    if final_score >= 0.65:
        return "revise"
    return "block"


def filter_media_feedback(items: list[Any]) -> list[str]:
    return [str(item) for item in items if str(item).strip() and not MEDIA_FEEDBACK_RE.search(str(item))]


def unique_items(items: list[str], limit: int = 8) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        clean = item.strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        out.append(clean)
        if len(out) >= limit:
            break
    return out


def rule_top_fixes(features: dict[str, Any], scores: dict[str, float], text_only_eval: bool) -> list[str]:
    fixes: list[str] = []
    if features.get("generic_opener_count") or features.get("repo_note_opener_count"):
        fixes.append("Replace the repo-note opener with a thesis-first hook before naming metadata.")
    if scores.get("hook_strength", 0) < 0.62 or not features.get("first_thesis_marker_count"):
        fixes.append("Make post 1 a repeatable technical thesis, not a setup sentence.")
    if not features.get("example_marker_count"):
        fixes.append("Add one concrete example: file path, command, API, mapping, or before/after.")
    if not features.get("caveat_count"):
        fixes.append("Add a visible caveat or ownership/source boundary.")
    if features.get("summary_phrase_count", 0) >= max(4, features.get("post_count", 0) + 1):
        fixes.append("Cut README-summary phrasing; explain the mechanism and workflow implication instead.")
    if features.get("voice_drift_count"):
        fixes.append("Keep one language voice; reserve English for technical names or one deliberate hook line.")
    if features.get("post_count", 0) < 4 and features.get("total_chars", 0) < 420:
        fixes.append("Expand only if there is new substance: mechanism, example, caveat, or link.")
    if features.get("over_280_count"):
        fixes.append("Split any post over 280 characters before marking the pack ready.")
    if not text_only_eval and scores.get("media_quality", 1) < 0.65:
        fixes.append("Fix image governance before publishing: actual file, alt text, disclosure, and review status.")
    return fixes


def write_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# X Eval Report",
        "",
        f"- Created at: {result['created_at']}",
        f"- Decision: `{result['decision']}`",
        f"- Final score: `{result['final_score']:.3f}`",
        f"- Grok used: `{result['grok']['used']}`",
        "",
        "## Scores",
        "",
    ]
    for key, value in result["scores"].items():
        lines.append(f"- `{key}`: {value:.3f}")
    lines.extend(["", "## Fixes", ""])
    for fix in result.get("top_fixes", []):
        lines.append(f"- {fix}")
    lines.extend(["", "## Strengths", ""])
    for strength in result.get("top_strengths", []):
        lines.append(f"- {strength}")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            result.get("reasoning_summary") or "Rule-based evaluation completed.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_run_dir", help="Run source directory containing posting_pack.md")
    parser.add_argument("--pack-file", default="", help="Optional posting pack filename/path to evaluate")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--model", default="")
    parser.add_argument("--no-grok", action="store_true")
    parser.add_argument("--text-only-eval", action="store_true", help="Neutralize media scoring for early copy experiments")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--min-ready-score", type=float, default=0.80)
    args = parser.parse_args()

    repo_run_dir = Path(args.repo_run_dir).expanduser().resolve()
    posting_pack = Path(args.pack_file).expanduser() if args.pack_file else repo_run_dir / "posting_pack.md"
    if args.pack_file and not posting_pack.is_absolute():
        posting_pack = repo_run_dir / posting_pack
    if not posting_pack.exists():
        raise SystemExit(f"posting_pack.md not found: {posting_pack}")
    posts = extract_ready_to_post(posting_pack.read_text(encoding="utf-8"))
    if not posts:
        raise SystemExit("Could not extract Ready To Post block from posting_pack.md")

    cross_status = cross_check_status(repo_run_dir)
    claims = claims_summary(repo_run_dir)
    images = image_summary(repo_run_dir)
    features = text_features(posts)
    strategy = load_strategy_decision(repo_run_dir)
    rule_scores = deterministic_scores(posts, cross_status, claims, images, features)
    if args.text_only_eval:
        rule_scores["media_quality"] = 0.75
    deterministic = {
        "cross_check_status": cross_status,
        "claims": claims,
        "images": images,
        "features": features,
        "rule_scores": rule_scores,
        "strategy": strategy.get("recommended_strategy", {}),
        "text_only_eval": args.text_only_eval,
    }

    env, _ = load_env([repo_run_dir / ".env", Path.cwd() / ".env", Path(args.env_file)])
    api_key = env.get("GROK_API_KEY") or env.get("XAI_API_KEY") or ""
    model = args.model or env.get("GROK_MODEL") or env.get("XAI_MODEL") or "grok-4.3"
    grok_result: dict[str, Any] | None = None
    grok_error = ""
    if api_key and not args.no_grok:
        try:
            grok_result = grok_eval(api_key, model, posts, deterministic, args.timeout)
        except Exception as exc:  # noqa: BLE001
            grok_error = str(exc)

    scores, final_score = merge_scores(rule_scores, grok_result)
    if args.text_only_eval:
        scores["media_quality"] = max(scores.get("media_quality", 0.0), 0.75)
        final_score = weighted_score(scores)
    decision = decision_from_score(final_score, scores, ignore_media_gate=args.text_only_eval)
    if final_score < args.min_ready_score and decision == "ready":
        decision = "revise"
    semantic_score = grok_weighted_score(grok_result, args.text_only_eval)
    semantic_decision = str((grok_result or {}).get("decision") or "").lower()
    if semantic_decision == "block":
        decision = "block"
    elif decision == "ready" and semantic_decision == "revise":
        if semantic_score is None or semantic_score < args.min_ready_score:
            decision = "revise"
    grok_fixes = (grok_result or {}).get("top_fixes", [])
    if args.text_only_eval:
        grok_fixes = filter_media_feedback(grok_fixes)
    combined_fixes = unique_items([*map(str, grok_fixes), *rule_top_fixes(features, scores, args.text_only_eval)])
    result = {
        "schema_version": 1,
        "created_at": utc_now(),
        "repo_run_dir": str(repo_run_dir),
        "decision": decision,
        "final_score": final_score,
        "scores": scores,
        "weights": WEIGHTS,
        "rule_scores": rule_scores,
        "semantic_score": semantic_score,
        "deterministic": deterministic,
        "grok": {
            "used": bool(grok_result),
            "model": model if grok_result else "",
            "error": grok_error,
            "result": grok_result or {},
        },
        "top_strengths": (grok_result or {}).get("top_strengths", []),
        "top_fixes": combined_fixes,
        "reasoning_summary": (grok_result or {}).get("reasoning_summary", ""),
    }
    if posting_pack.name == "posting_pack.md":
        eval_path = repo_run_dir / "post_eval.json"
        report_path = repo_run_dir / "x_eval_report.md"
    else:
        suffix = re.sub(r"[^A-Za-z0-9_.-]+", "-", posting_pack.stem).strip("-") or "candidate"
        eval_path = repo_run_dir / f"post_eval.{suffix}.json"
        report_path = repo_run_dir / f"x_eval_report.{suffix}.md"
    write_json(eval_path, result)
    write_report(report_path, result)
    print(f"Decision: {decision}")
    print(f"Final score: {final_score:.3f}")
    print(f"Wrote: {eval_path}")
    print(f"Wrote: {report_path}")
    if grok_error:
        print(f"Grok warning: {grok_error}", file=sys.stderr)
    return 0 if decision in {"ready", "revise", "block"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
