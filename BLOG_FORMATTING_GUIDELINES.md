# SparkOS Blog Formatting Guidelines (LLM Workflow)

This guide is the canonical format contract for auto-generated SparkOS blog posts.

Use it when a GitHub Issue triggers an Action that asks an LLM to generate a Docusaurus post and open a PR.

---

## 1) Goal

Generate **consistent, release-grade Docusaurus blog posts** from issue content, with:

- valid Docusaurus frontmatter
- valid SparkOS author/tag values
- predictable file naming
- stable post structure for readers and maintainers

---

## 2) Output location and filename

Create posts in:

- `blog/`

Filename format (required):

- `YYYY-MM-DD-short-kebab-slug.mdx`

Examples:

- `2026-04-09-sparkos-16-0-release-announcement.mdx`
- `2026-04-09-sparkos-16-0-hotfix-2.mdx`

Rules:

- Date must be UTC date of post creation.
- Slug must be lowercase kebab-case.
- Use `.mdx` extension.

---

## 3) Allowed frontmatter schema

Every post MUST start with frontmatter exactly in this style:

```md
---
slug: <kebab-slug-without-date>
title: <human-readable-title>
authors: [sparkteam] | [releasebot] | [sparkteam, releasebot]
tags: [<one-or-more-allowed-tags>]
---
```

### Allowed authors

From `blog/authors.yml`:

- `sparkteam`
- `releasebot`

### Allowed tags

From `blog/tags.yml`:

- `release`
- `changelog`
- `security`
- `hotfix`
- `maintenance`
- `misc`

Hard constraints:

- Do **not** invent authors.
- Do **not** invent tags.
- Use at least 1 tag and at most 3 tags.

---

## 4) Mandatory body structure

All posts must follow this section order.

1. **Opening summary paragraph** (2-4 lines)
2. `/* truncate */` marker
3. `## Highlights`
4. `## Detailed Changelog`
5. `## Known Issues`
6. `## Support / Reporting`

### Required section behavior

- If a section has no data, write `- None.` (do not remove the section).
- Use concise bullet lists.
- Keep tone neutral and release-focused.
- Avoid marketing fluff.

---

## 5) Writing style

- Use clear release engineering language.
- Prefer factual statements and actionable guidance.
- No emoji in headings.
- Avoid speculative claims.
- Use short paragraphs and bullets.
- Refer to build artifacts exactly as provided.

---

## 6) Mapping from issue fields to post content

The workflow should parse issue body fields and map them as follows:

- `Release Type` -> tags/title wording
- `Version` -> title + highlights
- `Highlights` -> `## Highlights`
- `Detailed Changelog` -> `## Detailed Changelog`
- `Known Issues` -> `## Known Issues`
- `Security Notes` -> include `security` tag and mention under Highlights/Known Issues
- `Support Links` -> `## Support / Reporting`

If a required issue field is missing:

- insert `TBD` in that specific bullet
- still generate valid post
- include a PR note requesting maintainer completion

---

## 7) Tag selection rules

Use these rules deterministically:

- Full monthly/major source release announcement: `release`, `changelog`
- Patch between releases: `hotfix`, `changelog`
- Security-focused patch: include `security`
- Infra/tooling-only post: `maintenance`
- Anything else: `misc`

---

## 8) Canonical title templates

Use one of these:

- `SparkOS <version> - Official Release Announcement`
- `SparkOS <version> Hotfix <n>`
- `SparkOS <month year> Maintenance Update`
- `SparkOS Security Update - <month year>`

Examples:

- `SparkOS 16.0 - Official Release Announcement`
- `SparkOS 16.0 Hotfix 2`

---

## 9) Required MDX template for generation

Use this exact starter template:

```mdx
---
slug: <slug>
title: <title>
authors: [sparkteam]
tags: [release, changelog]
---

<Summary paragraph 1>
<Summary paragraph 2>

{/* truncate */}

## Highlights

- <item>

## Detailed Changelog

- <category>: <change>
- <category>: <change>

## Known Issues

- <item or "None.">

## Support / Reporting

- Community: https://t.me/SparkOSCommunity
- Channel: https://t.me/SparkOSChannel
- GitHub: https://github.com/Spark-Rom
```

---

## 10) PR requirements for the Action

The generated PR must:

- modify only files under `blog/` (unless explicitly requested)
- include exactly one new post file per release issue
- include PR body with:
  - source issue link
  - generated slug
  - selected tags
  - checklist of missing/TBD fields

Suggested PR title format:

- `blog: add <slug> release post`

---

## 11) Validation checklist (must pass before PR)

- [ ] file path matches `blog/YYYY-MM-DD-*.mdx`
- [ ] frontmatter present and valid
- [ ] authors are from allowed list
- [ ] tags are from allowed list
- [ ] `/* truncate */` exists
- [ ] all mandatory sections exist in correct order
- [ ] no empty section (use `None.` when needed)
- [ ] markdown/MDX syntax valid

---

## 12) Non-goals

- Do not auto-edit Docusaurus config.
- Do not create new tags/authors automatically.
- Do not alter unrelated files.

This keeps automation safe and predictable.
