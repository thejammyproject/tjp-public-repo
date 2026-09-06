# tjp-public-repo

Public examples of what I am learning and the infrastructure, automation, and software work I can share with employers.

## Portfolio repository browser

The CV site in `website/thejammyproject` includes a dedicated, read-only repository browser at `repository.html`. It presents a static snapshot of this repository with directory navigation, bookmarkable `?path=` URLs, breadcrumbs, line-numbered syntax-highlighted source, sanitized Markdown previews, responsive layouts, and links back to GitHub.

The browser never executes repository content and does not use a GitHub token. Binary files and text files larger than the configured limit are listed but not embedded. Traversal paths are rejected in the browser, and only files present in the generated manifest can be requested.

### Configuration

Repository owner, name, branch, display text, technology labels, ignored paths, and the 512 KiB preview limit are centralized in:

```text
website/thejammyproject/repository-config.json
```

No environment variables are required. The default ignored paths exclude Git internals, dependency/build outputs, the encrypted-secrets directory, old web logs, and generated snapshot output.

### Generate and test locally

Node.js 20 or newer is sufficient; there are no npm package dependencies. From the site directory:

```bash
cd website/thejammyproject
npm test
npm run generate:repository
python3 -m http.server 8080
```

Open `http://localhost:8080/repository.html`. Do not open the HTML directly from disk because browsers do not allow its JSON fetches from `file://` URLs.

The generator reads the current local checkout, writes `repository-data/manifest.json`, and writes each previewable file to a separate content-addressed JSON file. File bodies are therefore loaded only when selected. Regenerate the snapshot whenever repository content changes and before building the image.

### Deployment and caching

Build the existing Nginx image from the site directory after generating the snapshot:

```bash
docker build -t jammyuk/thejammyproject-website:<tag> website/thejammyproject
```

The included Nginx configuration caches repository metadata and file snapshots for 10 minutes. Update the pinned image in `deploy/k8s/thejammyproject/current-site.yaml`; Argo CD continues to deploy the site in the existing way.

Syntax highlighting uses highlight.js 11.12.0, Markdown parsing uses Marked 18.0.7, and rendered Markdown is sanitized with DOMPurify 3.4.14. These pinned browser libraries are loaded from their public CDNs; raw Markdown is shown safely if they are unavailable.
