# docs.thejammyproject.internal

An independent, static documentation site built with MkDocs Material.

## Local development

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r website/docs.thejammyproject.internal/requirements.txt
mkdocs serve -f website/docs.thejammyproject.internal/mkdocs.yml
```

Open `http://127.0.0.1:8000`.

## Build

```bash
mkdocs build --strict -f website/docs.thejammyproject.internal/mkdocs.yml
docker build -f website/docs.thejammyproject.internal/Dockerfile \
  -t thejammyproject-docs:local .
```

Add documentation beneath `docs/` and register deliberate navigation ordering
in `mkdocs.yml`. Every Markdown file builds to its own page.
