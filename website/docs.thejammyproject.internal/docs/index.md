# The Jammy Project Docs

Practical notes for Linux, cloud, and infrastructure work.

This site is a lightweight knowledge base: each topic is stored as Markdown in
Git, built into its own searchable page, and deployed independently from the
main The Jammy Project website.

## Linux CLI guides

The first collection covers the commands and concepts used most often while
operating and troubleshooting Linux infrastructure.

- Start with [pipes and redirection](linux/cli/pipes-redirection.md) to
  understand how commands connect.
- Use [grep](linux/cli/grep.md), [sed](linux/cli/sed.md), and
  [awk](linux/cli/awk.md) to search and process text.
- Follow the [logs and troubleshooting](linux/cli/logs-troubleshooting.md)
  workflow during incidents.
- Use the sidebar or search box to open any guide.

## How the site works

- Markdown remains the source of truth.
- Git history records every documentation change.
- MkDocs creates one static page per Markdown file.
- The generated site requires no database or server-side application.
- Nginx serves the site inside its own Kubernetes deployment.
