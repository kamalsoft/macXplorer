---
name: macxplorer-repository-guide
description: Explain macXplorer's structure, startup, PyQt UI, feature flows, plugin boundaries, tests, dependencies, and risks with token-efficient, verified repository evidence. Use when onboarding, tracing code, or answering repository questions.
---

# macXplorer repository guide

Use this skill for codebase explanations and onboarding, not implementation.

1. Start with the user's requested component and the repository map in `docs/architecture.md`. Read the current source files/functions needed to verify the answer; documentation is a map, not proof that source has not changed.
2. Keep exploration bounded: locate exact symbols, read focused ranges, and follow only the calls/signals needed for the question. Avoid dumping unrelated files or repeating information already verified in the current task.
3. Ground every behavior statement in actual files and functions. In responses, link workspace files using absolute-path Markdown links. Separate verified behavior from assumptions and unverified risks; say when the repository does not establish an answer.
4. Explain one component at a time when requested. Include only relevant call paths, signals/slots, state, tests, and dependencies. Use a small Mermaid diagram only when it makes a real relationship easier to understand.
5. Prefer concise, structured answers. Do not invent modules, APIs, supported behavior, dependency versions, test results, or platform guarantees.
6. If the question implies a code or documentation change, stop at explanation and request or follow the user's approval-gated implementation workflow; do not edit from this skill alone.

For a verified file/function inventory and learning sequence, consult `docs/architecture.md`. For setup and test commands, consult `docs/development.md`.
