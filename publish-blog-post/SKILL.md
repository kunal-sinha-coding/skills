---
name: publish-blog-post
description: Publish a user-specified Markdown draft from the personal-website repository as a blog post. Use when the user asks to publish a draft, add a post to the website, or turn a draft file into a live blog entry.
---

# Publish Blog Post

## Overview

Turn one specified Markdown post in `/workspace/personal-website/blog` into a published website entry. Use the blog manifest to control homepage visibility, validate the result, then commit and push the website changes on `main`.

## Workflow

1. Confirm the user specified the post file. If no post is specified, ask which post to publish.
2. Inspect the specified post and the existing published post at `blog/intro_rl.md` and `blog/intro_rl.html` before editing.
3. Choose a lowercase snake case slug that is unique under `blog/`.
4. Keep the Markdown content at `blog/<slug>.md`. Do not create a separate draft directory.
5. Copy the existing published HTML shell to `blog/<slug>.html`. Update the page title, metadata, visible heading, date, and Markdown fetch path. Keep the existing renderer, styling, MathJax support, and Mermaid support.
6. Add or update the matching entry in `blog/posts.json`. Set `published` to `true` to display the post on the homepage or `false` to keep it hidden.
7. Do not add individual post cards directly to `index.html`. The homepage reads `blog/posts.json` and filters entries by `published`.
8. Check that the HTML fetch path matches the new Markdown filename and that the manifest slug matches the new HTML filename.
9. Review the diff for accidental changes. Run `git diff --check` and any repository-appropriate validation available.
10. Commit only the intended website files directly on `main` with a clear message, then push `main` to the personal-website remote.

## Publishing rules

- Do not change a post's `published` value unless the user explicitly requests a visibility change.
- A post can remain in `blog/` with `published` set to `false` while it is being revised.
- Preserve the author’s content and structure. Make only the edits required for the published page and manifest entry.
- Follow the repository’s `AGENTS.md`, especially its writing style and synchronization rules.
- Keep the publication date consistent between the HTML page and the manifest entry.
- If unrelated work is present, leave it untouched and exclude it from the commit.
