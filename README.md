# Website

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Installation

```bash
yarn
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Automated Blog Generation Workflow

This repo includes an issue-driven workflow to auto-generate SparkOS release blog posts.

### How it works

1. Create a new issue using **Blog Release Post** template.
2. Add/keep the `blog-post` label (template adds it automatically).
3. GitHub Actions runs `.github/workflows/generate-blog-post.yml`.
4. The workflow reads issue fields and `BLOG_FORMATTING_GUIDELINES.md`.
5. It generates one `.mdx` file in `blog/` and opens a PR.

### Required repository settings

- Add repository secret: `OPENAI_API_KEY`
- Optional repository variable: `OPENAI_MODEL` (default fallback is used if unset)

### Files involved

- Issue template: `.github/ISSUE_TEMPLATE/blog_release_post.yml`
- Workflow: `.github/workflows/generate-blog-post.yml`
- Generator script: `.github/scripts/generate_blog_post.py`
- Formatting contract: `BLOG_FORMATTING_GUIDELINES.md`

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
