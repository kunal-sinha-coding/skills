---
name: update-documentation
description: Audit every README.md in a repository against the current code, configuration, scripts, and repository layout, then update factual information that is outdated. Use for documentation refreshes and README maintenance.
---

# Update Documentation

Keep repository README files factually aligned with the implementation.

## Audit

1. Find every tracked or repository-local `README.md`, including nested README files, while excluding dependency, build, and generated directories when they are clearly outside the project's source.
2. Read each README completely enough to understand its claims, commands, paths, configuration, setup steps, examples, and status statements.
3. Inspect the corresponding source files, scripts, configuration, tests, package metadata, and repository layout. Treat executable behavior and configuration as the source of truth.
4. Identify only information that is stale, incorrect, missing for a documented workflow, or contradicted by the code. Preserve accurate wording and the repository's existing style.

## Update and verify

1. Make the smallest edits that bring each README up to date. Do not invent features, credentials, results, or supported environments.
2. Check every command and path mentioned in the changed sections against the repository. Run lightweight documentation-relevant validation when practical.
3. Review the diff for accidental scope expansion, broken Markdown, and claims unsupported by the code.
4. Report each README changed, the factual issue corrected, and any uncertainty or follow-up documentation that could not be verified.
