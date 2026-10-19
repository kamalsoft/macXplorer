---
name: macxplorer-approval-first-changes
description: Plan and implement macXplorer changes with source-grounded requirements, explicit approval before edits, token-efficient context use, focused tests, and production-quality verification. Use for feature requests, fixes, or refactors in this project.
---

# macXplorer approval-first changes

This project requires a plan and affirmative user approval before implementation. A request to explore, review, explain, or plan is not permission to edit.

## Before approval

1. Identify the exact behavior requested and inspect only the relevant source, tests, and documentation. Use symbol searches and bounded reads; avoid broad file dumps and repeated searches.
2. Trace existing behavior and related UI/plugin/test surfaces. State what is verified from code separately from assumptions, unknowns, and options.
3. If behavior, scope, or compatibility has more than one reasonable interpretation, ask one focused question with `ask_user`; do not silently choose.
4. Propose a short, concrete plan naming files/surfaces to change, expected behavior, and targeted validation. Make no file changes until the user explicitly approves that plan.

## After approval

1. Make the smallest complete change consistent with existing patterns. Preserve unrelated work and avoid speculative features, unnecessary abstractions, and dependency changes.
2. Update directly related documentation and tests when behavior changes. Keep UI, core, plugin, settings, and packaging surfaces consistent where relevant.
3. Surface errors using repository conventions; do not conceal failures with broad catches, silent fallbacks, or success-shaped results.
4. Run the narrowest meaningful tests/build/type or syntax checks available. Report exact commands and outcomes; do not imply native macOS or release validation from offscreen tests.
5. Summarize changed files, verified behavior, validation results, and any remaining assumptions or limitations with absolute-path Markdown links.

## Context efficiency

- Follow the user's requested level of detail; default to a concise answer with evidence and next steps.
- Reuse verified facts from the current task, but re-check source when a claim is consequential or may have changed.
- Do not create planning documents unless explicitly requested. Keep the plan in the conversation and implementation in the approved files.
- Do not claim production readiness without tests and platform/release evidence appropriate to the change.
