---
name: github-repo-to-x-threads
description: Use this skill whenever the user gives a GitHub repository URL, owner/repo string, or local repo path and asks to analyze it for an X/Twitter post, thread, launch/share post, responsible developer recommendation, project writeup, or social media copy. This skill clones or reads the repo, cross-checks local code/docs with live GitHub metadata, separates verified facts from inference and personal vision, drafts responsible X threads, and prepares or generates GPT Image 2 / image-generation-style visual assets for posting.
---

# GitHub Repo to X Threads

Turn a GitHub repository into a responsible, high-signal X thread. The goal is not hype. The goal is a post that earns technical trust: accurate claims, clear attribution, useful framing, and a strong hook.

## Use When

Use this skill when the user asks things like:

- "把这个 repo 写成 X thread"
- "分析这个 GitHub 项目，帮我发 X"
- "I want to share this repo on Twitter/X responsibly"
- "给这个项目做一组推文和配图"
- "帮我把 repo + 我的 vision 组织成 thread"
- "这个项目不是我的，只是分享，别写成官方口吻"

## Inputs To Resolve

Infer these from the prompt when possible. Ask only if the missing answer would cause a misleading post.

- **Repo source**: GitHub URL, `owner/repo`, or local path.
- **User relationship to the repo**: default to `independent sharer` unless the user clearly says they are the author, maintainer, contributor, or company/team member.
- **Posting language**: match the user's language; for Chinese prompts, write Chinese by default with technical English terms where natural.
- **User angle**: optional personal vision, use case, comparison, build plan, demo plan, or critique.
- **Output size**: default to one main X thread with 6-10 posts.
- **Visuals**: default to 1-3 image concepts; generate images with GPT Image 2 or the available image generation tool if the user asked for generated assets.
- **Final-mile preference**: default to a paste-ready posting pack, not a prose-only critique. The user should be able to publish with minimal manual cleanup.

## Core Workflow

### 1. Collect Repo Evidence

Do not write the thread from memory or from the repo name alone.

If the user gives a remote GitHub repo:

1. Clone it into a temporary or workspace analysis directory.
2. Read local files from the clone.
3. Fetch live metadata from GitHub.

If the user gives a local repo path:

1. Read the local working tree.
2. Resolve its `origin` remote if present.
3. Fetch live metadata from GitHub when the remote is available.

Prefer the bundled helper when useful:

```bash
python scripts/collect_repo_context.py <github-url-or-owner/repo-or-local-path> --out /tmp/repo-to-x-context
```

Then inspect the generated `repo_context.json` and `file_manifest.txt`.

Minimum evidence to collect:

- README and top-level docs.
- License file and package metadata (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, etc.).
- Source tree structure and obvious entry points.
- Examples, demos, docs, screenshots, papers, or benchmark files if present.
- GitHub metadata: description, stars, forks, topics, license, default branch, latest release, pushed/updated times, homepage, archived/fork status.

If a metadata source fails, state that it was unavailable. Do not invent stars, maintainers, releases, affiliations, benchmarks, or roadmap items.

### 2. Cross-Check Claims

Create a short internal claim ledger before drafting. You do not have to show every detail, but the final answer should reflect this separation:

- **Verified repo fact**: directly supported by local files or GitHub metadata.
- **Reasonable inference**: derived from code structure, dependencies, or examples.
- **User vision**: the user's own plan, interpretation, or deployment path.
- **Unknown / unsafe**: attractive claim that is not supported enough for X.

Examples:

- Safe: "The README describes support for Discord and Telegram."
- Unsafe unless proven: "This is the most complete open-source robotics agent framework."
- Safe with boundary: "My personal read is that this could fit a living-room robotics workflow."
- Unsafe: "The RoboClaw team plans to target living-room deployment" unless the repo says so.

### 3. Preserve Ownership Boundaries

This is the most important reputation safeguard.

If the project is not the user's:

- Credit the maintainers/lab/company in the first post.
- Use "I found", "I am looking at", "my read", "my personal vision", not "we built" or "our roadmap".
- Do not recruit contributors on behalf of the project.
- Do not imply official endorsement, official roadmap, partnership, or affiliation.
- Invite discussion around the user's thinking, not PRs/issues unless the user explicitly wants that.

If the user is the author or maintainer:

- It is fine to use "we" or "I", but still separate shipped features from future plans.
- Label roadmap, experiments, and aspirations as such.

### 4. Decide The Thread Strategy

Choose one strategy and state it briefly before the draft.

Good default strategies:

- **Independent technical share**: best when the repo is not the user's.
- **Repo + personal vision**: best when the user wants to use the repo as a jumping-off point for their own thinking.
- **Launch thread**: best when the user owns the repo or is releasing a project.
- **Builder notes**: best when the user tested or read the repo and wants to share practical lessons.

For the user's common target style, prefer:

- technically accurate,
- respectful to original authors,
- concrete enough to show the user actually read the repo,
- modest about uncertainty,
- strong enough to be worth reposting.

### 5. Draft The X Thread

Default structure:

1. Hook + exact attribution + repo link.
2. What the repo actually does.
3. Why it matters technically.
4. Evidence-backed feature breakdown.
5. The user's personal angle or vision, clearly labeled.
6. Deployment path, use case, or implication.
7. Caveats / early-stage boundary / what not to overclaim.
8. Closing question or discussion prompt.

Length guidance:

- Keep each post short enough to paste into X comfortably.
- For standard X accounts, aim for roughly 240-270 visible characters per post.
- If a post needs more nuance, split it rather than compressing into vague language.
- Number posts as `(1/8)`, `(2/8)`, etc. when the user wants a thread.

Avoid:

- "best", "first", "only", "most complete" unless strongly verified.
- Excessive emojis.
- "AI robot future is here" style hype.
- Fake certainty about project maturity.
- Hidden affiliation.
- Asking people to contribute to a project the user does not own.

### 6. Build The Final-Mile Posting Pack

The final output should reduce the user's posting friction. After drafting, convert the thread into a practical publishing pack.

Include:

- **Paste-ready thread**: one clean code block containing only the posts, with no commentary inside.
- **Per-post length audit**: mark each post as `OK`, `Tight`, or `Split` based on visible length. Do not force exact counts when multilingual text makes counting unreliable; use a conservative estimate and split posts that are clearly too long.
- **Image placement**: specify which image goes with which post, usually image 1 on the hook post and optional supporting images on later posts.
- **Alt text**: one short alt text per image, ready to paste into X.
- **Disclosure text**: one short line when images are generated or conceptual.
- **Pre-flight checklist**: 5-8 short checks the user can scan before posting.
- **Optional short version**: when useful, provide a single-post version for quick posting.

Keep this section practical. Avoid long explanations after the user has a paste-ready draft.

Suggested final-mile template:

````markdown
**Ready To Post**
```text
(1/N) ...

(2/N) ...
```

**Posting Map**
- Post 1: attach image 1, alt text: ...
- Post 4: attach image 2, alt text: ...
- Disclosure: Generated conceptual visual, not an official project screenshot.

**Length Audit**
- 1/N: OK
- 2/N: Tight, do not add more text
- 3/N: OK

**Pre-Flight**
- Repo owner credited.
- Personal vision labeled as personal.
- No unsupported "best/first/only" claim.
- Images are conceptual or attributed.
- Link works.
````

### 7. Produce GPT Image 2 Visual Assets

When the user asks for GPT Image 2 or GPT Image-style generated images, use the available image generation tool after the text strategy is clear.

Responsible visual rules:

- Do not generate fake screenshots of the repo, GitHub stars, dashboards, papers, benchmark tables, or robot results.
- Do not imply the generated image is an official project asset.
- Prefer conceptual visuals, clean diagrams, workflow boards, or "builder desk" scenes over fake product evidence.
- If using an official logo or screenshot from the repo, only use assets that are actually present and cite/label the source in the final response.
- Provide alt text for every image.

Good image concepts:

- Architecture/workflow: `GitHub repo -> evidence extraction -> claims ledger -> X thread -> generated visuals`.
- Domain visual: a realistic but clearly conceptual scene matching the project domain.
- Vision visual: a staged roadmap from current repo capabilities to the user's personal deployment idea.
- Evidence visual: only when built from verified repo artifacts, and never as a fake screenshot.

For each image, output:

- Purpose: where it fits in the thread.
- Prompt: ready for GPT Image 2 / image generation.
- Alt text: concise, accessible description.
- Disclosure line: e.g. "Generated conceptual visual, not an official project screenshot."

If image generation is available and the user requested actual images, generate 1-3 images. Do not stop at prompts. If image generation is not available, provide ready-to-run prompts and make that limitation explicit.

Default Image 2 pack:

1. **Hero image** for post 1: visually communicates the repo domain and the user's angle without pretending to be an official asset.
2. **Architecture or workflow image** for a middle post: explains how the repo works or how the user's analysis pipeline works.
3. **Vision image** for a later post: shows the user's personal deployment path or future framing.

Image prompt rules:

- Include aspect ratio preference. For X, default to `16:9` for landscape technical diagrams or `4:5` for high-feed visual weight.
- Specify clean composition, readable spacing, no fake UI text unless the text is generic and minimal.
- Avoid logos unless the repo provides one and usage is appropriate.
- Prefer "conceptual illustration" or "technical diagram" language when the image is not evidence.
- Add "no fake screenshots, no fake GitHub metrics, no fake benchmark tables" to the prompt when relevant.

### 8. Final Output Format

Use this format unless the user asks otherwise:

````markdown
**Evidence**
- Repo: ...
- Local source checked: ...
- Live metadata checked: ...
- Public-safe facts: ...
- Caveats: ...

**Posting Strategy**
...

**Ready To Post**
```text
(1/N) ...

(2/N) ...

...
```

**Posting Map**
- Post 1: attach image 1, alt text: ...
- Disclosure: ...

**Length Audit**
- 1/N: OK
- 2/N: OK

**Images**
1. Purpose: ...
   Prompt: ...
   Alt text: ...
   Disclosure: ...

**Do Not Say**
- ...
````

If the answer is for immediate posting, the `Ready To Post` block is the primary artifact. Keep surrounding analysis brief enough that the user can quickly find the copyable thread.

## Quality Bar

Before finalizing, run this checklist:

- Does the first post clearly credit the repo owner?
- Are all strong claims backed by repo files or GitHub metadata?
- Are personal opinions and visions labeled as personal?
- Does the thread avoid sounding like an official announcement when the user is only sharing?
- Does it include a useful technical reason to care?
- Does it include at least one caveat or maturity boundary when appropriate?
- Would a maintainer of the repo feel accurately represented?
- Are generated images clearly conceptual rather than fake evidence?
- Can the user publish from the `Ready To Post` block without rewriting formatting?
- Are image placement, alt text, and generated-image disclosure clear?

## Example: Independent Share + Personal Vision

Use this pattern when the user says the project is not theirs:

```text
(1/8) 最近看到一个很有意思的开源项目：<repo> by <owner>.

它做的是 <verified project scope>. 我不是项目成员，只是从开发者视角觉得这个方向值得认真看一下。

<repo URL>

下面是我的个人理解和一点延伸思考。
```

Then continue with verified facts first, and the user's vision second.
