# Thread Quality Checklist

Use this when the repo facts are collected but before final output.

## Reputation Safety

- The repo owner is credited in the first post.
- The user relationship is clear: author, contributor, or independent sharer.
- The post does not imply endorsement, official roadmap, or affiliation unless verified.
- The post does not ask for contributors unless the user owns the project or explicitly wants to promote contribution.
- Any user's own vision is labeled as personal thinking.

## Evidence Safety

- Stars, forks, releases, dates, and license come from live metadata or are omitted.
- Capabilities come from README/docs/code, not repo name vibes.
- Benchmarks, production readiness, and hardware support are stated only if directly supported.
- "Best", "first", "only", and "most complete" are avoided unless there is strong evidence.
- Missing or failed metadata is disclosed briefly when relevant.

## Thread Shape

- The hook is specific and not clickbait.
- Each post adds a new reason to care.
- Technical terms are concrete enough for developers but not written like README paste.
- Caveats make the post more credible, not weaker.
- The ending invites discussion, not blind hype.

## Final-Mile Posting

- The user has a single clean copy-paste block with only the posts.
- Every post has a rough length status: OK, Tight, or Split.
- The thread includes a posting map for image placement.
- Alt text is ready to paste into X.
- Generated-image disclosure is ready when needed.
- A one-post short version is included when it would materially reduce publishing friction.

## Visual Safety

- Generated visuals are labeled as conceptual.
- No fake UI screenshots, fake robot evidence, fake benchmark charts, or fake GitHub metrics.
- Alt text is included.
- Official assets are used only when actually present and attributed.
- Every image referenced in the posting map has a matching `images_manifest.json` entry.
- Generated image files live under `images/` with `sha256` and `mime_type`.

## GPT Image 2 Quality

- If image generation is available and the user requested images, the agent generates images rather than only writing prompts.
- Prompts specify aspect ratio, composition, and the post where the image will be used.
- Prompts explicitly avoid fake screenshots, fake GitHub metrics, and fake benchmark tables when relevant.
- The first image supports the hook; later images explain architecture, workflow, or personal vision.
- If the image tool cannot expose a file path, the manifest records a `prompt_only` entry and the final answer says that actual image generation could not be governed locally.
