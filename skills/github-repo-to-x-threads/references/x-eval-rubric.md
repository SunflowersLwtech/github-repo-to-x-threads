# X Eval Rubric

This rubric scores a posting pack before publishing and calibrates the strategy after publishing. It is not a real X ranking oracle. It is a local approximation that combines:

- public X recommendation-system signals,
- posting-pack safety gates,
- Grok semantic judgment,
- the user's own historical outcomes.

## Pre-Publish Scores

Use 0.0-1.0 scores.

| Score | Meaning |
| --- | --- |
| `claim_safety` | Public claims are sourced, ownership is clear, no fake metrics or unsupported superlatives. |
| `hook_strength` | The first post gives a concrete reason to stop scrolling within the first sentence. |
| `angle_freshness` | The thread has a sharp, repeatable thesis instead of a generic summary opener. |
| `specificity_density` | The post contains concrete technical details, examples, names, or mechanisms without becoming cluttered. |
| `audience_fit` | The thread matches the intended technical audience and avoids generic AI slop. |
| `bookmark_value` | Readers can save the post for a concrete technical idea, tool, repo, paper, or workflow. |
| `reply_potential` | The post invites useful discussion without baiting low-quality controversy. |
| `media_quality` | Images are governed, high-quality, relevant, accessible, and clearly conceptual when generated. |
| `structure_fit` | Thread length, sequencing, links, caveats, and post lengths fit X ergonomics. |
| `voice_authenticity` | The copy sounds like a real technical reader with taste, not a rigid generated template. |
| `risk_control` | Low spam/template/link/controversy/downranking risk. |

Default weighted score:

```text
final_score =
  0.18 * claim_safety
+ 0.12 * hook_strength
+ 0.14 * angle_freshness
+ 0.12 * specificity_density
+ 0.08 * audience_fit
+ 0.10 * bookmark_value
+ 0.06 * reply_potential
+ 0.08 * media_quality
+ 0.05 * structure_fit
+ 0.04 * voice_authenticity
+ 0.03 * risk_control
```

Recommended gates:

- `final_score >= 0.80`: ready if cross-check and image gates pass.
- `0.65 <= final_score < 0.80`: revise before publishing.
- `< 0.65`: block or rewrite.
- Any `claim_safety < 0.75`: revise, regardless of final score.
- Any `angle_freshness < 0.62`: revise, even if the thread is accurate.
- Any `specificity_density < 0.65`: revise.
- Any `voice_authenticity < 0.58`: revise.
- Any `media_quality < 0.65` when images are required: regenerate or remove image references.

The harsh rule: a safe, accurate summary is not automatically ready. If it reads like a paper abstract split into numbered tweets, it should go through draft tournament or rewrite.

## Grok Evaluation Role

Use Grok for semantic judgment:

- Is the hook specific and non-generic?
- Does the thread sound like a real technical reader wrote it?
- Does it overclaim?
- Is the caveat visible enough?
- Which post is most likely to create bookmark/reply value?
- Which line should be cut before publishing?
- What is the one thesis a reader would remember or repost?

Grok should return JSON. Treat it as a reviewer, not as evidence. If Grok says a factual claim is true, still require the claim ledger or source context.

## Draft Tournament

When the user says the post feels weak, rigid, generic, or not worth publishing, run:

```bash
python -B scripts/x_draft_tournament.py <repo-run-dir> \
  --prompt "Short description of the user's taste feedback" \
  --write-proposed-pack
```

This writes:

```text
draft_tournament.json
draft_tournament.md
posting_pack.proposed.md
```

The tournament should produce multiple angles first, then thread variants. The winning version still needs the normal claim, image, and publish gates.

## Text-Only Early Screening

For GitHub Trending or large-scale experiments, run copy quality before media quality:

```bash
python -B scripts/x_eval_post.py <repo-run-dir> --text-only-eval
```

In text-only mode:

- ignore image/media suggestions,
- focus on hook, angle, specificity, caveats, claim safety, and voice,
- accept a rewrite only if the score improves,
- deep clone, image generation, alt text, and media gates happen only after a candidate survives the screen.

If repeated rounds do not cross the ready threshold, do not publish. Convert the common fixes into strategy rules.

## Post-Publish Metrics

Collect metrics from X API when possible, then aggregate:

- impressions,
- likes,
- reposts / retweets / quotes,
- replies,
- bookmarks,
- profile clicks,
- URL clicks when available.

Outcome score can use:

```text
outcome_score =
  (likes + 2*reposts + 1.5*replies + 1.5*bookmarks + profile_clicks) / max(impressions, 1)
```

Use outcome scores to calibrate strategy memory. Do not use performance as proof that a public claim was accurate.

## Report Files

Pre-publish eval:

```text
post_eval.json
x_eval_report.md
```

Post-publish metrics:

```text
x_metrics_snapshot.json
post_outcome.json
```

Calibration:

```text
repo-to-x-workspace/strategy-memory/outcomes.jsonl
repo-to-x-workspace/strategy-memory/strategy_profile.json
```
