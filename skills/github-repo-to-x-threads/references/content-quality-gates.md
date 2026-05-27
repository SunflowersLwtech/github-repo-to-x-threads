# Content Quality Gates

Use this when a post is safe but still feels generic, smooth, or low-value.
These gates adapt content-diagnosis patterns for technical X posts, but the
rules here are repo-to-X specific.

## 1. Source Material Gate

Do not optimize a hook before the content has enough material. A publishable
technical post needs at least three of these:

- a concrete inspectable artifact: file path, function, config, command, API,
  benchmark table, paper figure, commit, or issue;
- a number or bounded comparison that is actually sourced;
- a before/after, failure mode, or rejected alternative;
- a reader pain or workflow constraint;
- a caveat that changes how the claim should be interpreted;
- a maintainer/source boundary that prevents hidden affiliation.

If the source only gives a repo name, README tagline, and star count, keep
screening text-only and collect more evidence before drafting.

## 2. Hook Independence Gate

Post 1 must work without a title, card, image, or prior context. It should make
three things legible fast:

- topic: what is being discussed;
- reason to read: the conflict, curiosity gap, risk, or workflow constraint;
- credibility: why this claim is grounded in evidence rather than vibe.

Use psychological triggers only when evidence supports them:

- cognitive conflict: "not X, but Y" when the source really changes a
  workflow assumption;
- curiosity gap: ask the unresolved technical question without hiding basic
  attribution;
- loss/risk: warn only about a real footgun or caveat;
- identity: name the technical reader who should care;
- numeric anchor: use sourced counts, scores, files, or timings.

Avoid giving the whole answer away in the hook. The first post should make the
reader want the mechanism, not merely nod at the conclusion.

## 3. Plain-Language Concept Gate

Every high-level concept must be reducible to plain technical language.

Bad shape:

- "This changes the future of agents."
- "A new paradigm for agent evolution."

Better shape:

- "The skill document becomes the state being trained; the model weights stay
  fixed."
- "Rejected edits become negative feedback instead of hidden prompt drift."

When a draft uses words like `paradigm`, `future`, `revolutionary`,
`framework`, `ecosystem`, `agentic`, or `self-evolving`, force one concrete
mechanism next to it.

## 4. Anti-Smoothness Gate

AI-looking copy is often too even: every paragraph closes neatly, every claim is
balanced, and no sentence admits uncertainty. Technical X copy can be clean
without being plastic.

Before publish:

- keep one real caveat or unresolved edge;
- do not repeat the same "not X, but Y" turn more than once unless each turn
  adds a distinct mechanism;
- cut ritual transitions such as "值得注意的是", "更重要的是", "总之",
  "in conclusion", and "it is important to note";
- prefer one sharp sentence and one concrete example over three polished
  summary sentences;
- use the user's language consistently; English should carry exact technical
  names, not filler.

## 5. X-Specific Shape

X is a text-first thinking surface. Links and images help, but they cannot carry
the post.

- Put the link after the reader already knows why it matters.
- If the first post has a link, make the thesis strong enough that the URL does
  not become the only reason to click.
- Do not make every post a feature list. Sequence should be thesis -> mechanism
  -> example -> caveat -> link or implication.
- A short post is acceptable only when it adds a new thought. Short filler is
  worse than no post.
