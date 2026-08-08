---
name: publish-blog-post
description: Publish a user-specified Markdown draft from the personal-website repository as a blog post. Use when the user asks to publish a draft, add a post to the website, or turn a draft file into a live blog entry.
---

# Publish Blog Post

## Overview

Turn one specified draft in `/workspace/personal-website/draft` into a published Markdown and HTML post. Update the homepage, validate the result, then commit and push the website changes on `main`.

## Workflow

1. Confirm the user specified the draft file. If no draft is specified, ask which draft to publish.
2. Inspect the draft and the existing published post at `blog/intro_rl.md` and `blog/intro_rl.html` before editing.
3. Choose a lowercase snake case slug that is unique under `blog/`.
4. Move or copy the draft content into `blog/<slug>.md`. Preserve the draft under `draft/` unless the user explicitly asks to remove it.
5. Copy the existing published HTML shell to `blog/<slug>.html`. Update the page title, metadata, visible heading, date, and Markdown fetch path. Keep the existing renderer, styling, MathJax support, and Mermaid support.
6. Add one card to the Blog Posts section in `index.html`. Include the new HTML path, publication date, title, and a concise summary.
7. Check that the HTML fetch path matches the new Markdown filename and that the homepage link matches the new HTML filename.
8. Review the diff for accidental changes. Run `git diff --check` and any repository-appropriate validation available.
9. Commit only the intended website files directly on `main` with a clear message, then push `main` to the personal-website remote.

## Publishing rules

- Do not publish a draft unless the user explicitly requests publication.
- Do not delete a draft as part of publication unless the user explicitly requests deletion.
- Preserve the author’s content and structure. Make only the edits required for the published page and homepage card.
- Follow the repository’s `AGENTS.md`, especially its writing style and synchronization rules.
- Keep the publication date consistent between the HTML page and the homepage card.
- If unrelated work is present, leave it untouched and exclude it from the commit.
