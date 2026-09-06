# Website editing guide

This is a static website served by Nginx. It has no application backend, database or server-side language, so there is no backend to convert to Python.

## Main pages

- `index.html` — homepage content, Experience list and Contact form.
- `repository.html` — public GitHub repository browser page.
- `archive.html` — previous homelab projects.
- `styles.css` — shared styling for the whole website.
- `main.js` — shared navigation and Experience modal behaviour.

## Experience modals

Each modal's editable content is stored separately in `modals/`:

- `modals/creovai.html`
- `modals/bcn-group.html`
- `modals/cloud53.html`
- `modals/ukfast.html`
- `modals/secure-information-assurance.html`

Edit the heading, dates, paragraph or list items in the relevant file. The homepage loads that file when its job title is selected. The Creovai file contains all three roles because the CV groups their responsibilities together as one continuous progression.

## Repository browser files

The repository feature is separated by responsibility rather than being ten versions of the same page:

- `repository.html` — page structure.
- `repository.css` — repository-only layout and code-view styling.
- `repository.js` — live GitHub API requests and screen rendering.
- `repository-core.js` — small reusable path, URL and file-tree helpers.
- `repository-config.json` — GitHub owner, repository, branch and display settings.
- `repository.test.mjs` — automated tests; it is not loaded by visitors.

The repository page also uses the shared `styles.css` and `main.js`. Keeping structure, styling, behaviour and configuration separate prevents a single large file from becoming difficult to maintain.

## Hosting and deployment

- `Dockerfile` packages the static files into Nginx.
- `nginx.conf` configures the web server.
- `deploy/k8s/thejammyproject/current-site.yaml` defines the Kubernetes workload.
- `deploy/argocd/thejammyproject.yaml` registers that workload with Argo CD.

These deployment files are not additional repository-page code and are not downloaded by visitors.
