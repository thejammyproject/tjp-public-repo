import { buildBreadcrumbs, entriesForDirectory, entriesFromGitTree, githubUrl, isMarkdown, normaliseRepositoryPath, rawGithubUrl } from './repository-core.js';

const elements = {
  title: document.getElementById('repository-title'),
  description: document.getElementById('repository-description'),
  meta: document.getElementById('repository-meta'),
  technologies: document.getElementById('repository-technologies'),
  repositoryLink: document.getElementById('repository-github-link'),
  currentLink: document.getElementById('current-github-link'),
  breadcrumbs: document.getElementById('breadcrumbs'),
  parent: document.getElementById('parent-link'),
  directoryStatus: document.getElementById('directory-status'),
  directoryList: document.getElementById('directory-list'),
  filePanel: document.getElementById('file-panel')
};

let repository;
let currentPath = '';

function setUrl(path) {
  const url = new URL(window.location.href);
  path ? url.searchParams.set('path', path) : url.searchParams.delete('path');
  history.pushState({ path }, '', url);
}

function navigate(path, replace = false) {
  try {
    currentPath = normaliseRepositoryPath(path);
  } catch {
    renderError('That repository path is not valid.');
    return;
  }
  if (!replace) setUrl(currentPath);
  renderLocation();
}

function createPathButton(label, path, className = '') {
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = label;
  button.className = className;
  button.addEventListener('click', () => navigate(path));
  return button;
}

function renderBreadcrumbs(entry) {
  elements.breadcrumbs.replaceChildren();
  for (const [index, crumb] of buildBreadcrumbs(currentPath).entries()) {
    if (index) elements.breadcrumbs.append(document.createTextNode(' / '));
    if (crumb.path === currentPath) {
      const current = document.createElement('span');
      current.textContent = crumb.label;
      current.setAttribute('aria-current', 'page');
      elements.breadcrumbs.append(current);
    } else {
      elements.breadcrumbs.append(createPathButton(crumb.label, crumb.path));
    }
  }
  elements.currentLink.href = githubUrl(repository.config, currentPath, entry?.type || 'directory');
}

function renderDirectory(directory) {
  const children = entriesForDirectory(repository.entries, directory);
  elements.directoryList.replaceChildren();
  elements.directoryStatus.hidden = true;
  if (!children.length) {
    elements.directoryStatus.textContent = 'This directory is empty.';
    elements.directoryStatus.hidden = false;
  }

  for (const entry of children) {
    const item = document.createElement('li');
    const button = createPathButton(entry.name, entry.path, 'directory-entry');
    const icon = document.createElement('span');
    icon.className = `entry-icon ${entry.type}`;
    icon.textContent = entry.type === 'directory' ? '▸' : '·';
    icon.setAttribute('aria-hidden', 'true');
    const label = document.createElement('span');
    label.textContent = entry.name;
    const detail = document.createElement('span');
    detail.className = 'entry-detail';
    detail.textContent = entry.type === 'directory' ? 'Folder' : formatBytes(entry.size);
    button.replaceChildren(icon, label, detail);
    button.setAttribute('aria-label', `${entry.type === 'directory' ? 'Open folder' : 'Open file'} ${entry.name}`);
    item.append(button);
    elements.directoryList.append(item);
  }

  const parentPath = directory.split('/').slice(0, -1).join('/');
  elements.parent.hidden = !directory;
  elements.parent.onclick = () => navigate(parentPath);
}

function formatBytes(bytes = 0) {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(bytes < 10240 ? 1 : 0)} KB`;
}

function renderEmptyPanel(title = 'Select a file', message = 'Choose a file from the repository to inspect its contents.') {
  const wrapper = document.createElement('div');
  wrapper.className = 'empty-state';
  const heading = document.createElement('h2');
  heading.textContent = title;
  const copy = document.createElement('p');
  copy.textContent = message;
  wrapper.append(heading, copy);
  elements.filePanel.replaceChildren(wrapper);
}

async function renderFile(entry, { landing = false } = {}) {
  if (!entry.viewable) {
    renderEmptyPanel('Preview unavailable', entry.unavailableReason || 'This file cannot be displayed safely. Use the GitHub link to view the original.');
    return;
  }
  elements.filePanel.innerHTML = '<div class="file-loading" role="status"><span class="spinner"></span>Loading file…</div>';
  try {
    const response = await fetch(rawGithubUrl(repository.config, entry.path), { cache: 'default' });
    if (!response.ok) throw new Error('GitHub file unavailable');
    const bytes = new Uint8Array(await response.arrayBuffer());
    if (bytes.subarray(0, Math.min(bytes.length, 8000)).includes(0)) {
      renderEmptyPanel('Preview unavailable', 'This appears to be a binary file. Use the GitHub link to view the original.');
      return;
    }
    const content = new TextDecoder('utf-8', { fatal: false }).decode(bytes);
    const header = document.createElement('header');
    header.className = 'file-header';
    const heading = document.createElement('h2');
    heading.textContent = landing ? 'README' : entry.path;
    const info = document.createElement('span');
    info.textContent = `${formatBytes(entry.size)} · ${entry.language}`;
    header.append(heading, info);
    const body = isMarkdown(entry.path) ? renderMarkdown(content) : renderCode(content, entry.language);
    elements.filePanel.replaceChildren(header, body);
  } catch {
    renderEmptyPanel('Unable to load this file', 'GitHub may be unavailable or rate-limiting requests. Please try again or use the GitHub link.');
  }
}

function renderCode(content, language) {
  const scroller = document.createElement('div');
  scroller.className = 'code-scroller';
  const table = document.createElement('table');
  table.className = 'code-table';
  const tbody = document.createElement('tbody');
  const highlighted = window.hljs
    ? (window.hljs.getLanguage(language)
        ? window.hljs.highlight(content, { language, ignoreIllegals: true }).value
        : window.hljs.highlightAuto(content).value).split('\n')
    : null;
  content.split('\n').forEach((line, index) => {
    const row = document.createElement('tr');
    const number = document.createElement('td');
    number.className = 'line-number';
    number.textContent = String(index + 1);
    const code = document.createElement('td');
    code.className = 'line-code hljs';
    if (highlighted) code.innerHTML = highlighted[index] || '';
    else code.textContent = line || ' ';
    row.append(number, code);
    tbody.append(row);
  });
  table.append(tbody);
  scroller.append(table);
  return scroller;
}

function renderMarkdown(content) {
  const article = document.createElement('div');
  article.className = 'markdown-body';
  if (window.marked && window.DOMPurify) {
    const raw = window.marked.parse(content, { gfm: true, breaks: false });
    article.innerHTML = window.DOMPurify.sanitize(raw, { USE_PROFILES: { html: true } });
    article.querySelectorAll('a').forEach(link => {
      link.rel = 'noreferrer';
      if (/^https?:/i.test(link.href)) link.target = '_blank';
    });
  } else {
    const pre = document.createElement('pre');
    pre.textContent = content;
    article.append(pre);
  }
  return article;
}

function renderLocation() {
  const entry = repository.entries.find(item => item.path === currentPath);
  if (currentPath && !entry) {
    renderError('That file or directory was not found in this repository.');
    return;
  }
  renderBreadcrumbs(entry);
  if (entry?.type === 'file') {
    renderDirectory(entry.parent);
    renderFile(entry);
    return;
  }
  const directory = entry?.path || '';
  renderDirectory(directory);
  const readme = repository.entries.find(item => item.parent === directory && item.type === 'file' && /^readme\.md$/i.test(item.name));
  readme ? renderFile(readme, { landing: true }) : renderEmptyPanel();
}

function renderError(message) {
  elements.directoryList.replaceChildren();
  elements.directoryStatus.hidden = false;
  elements.directoryStatus.textContent = message;
  renderEmptyPanel('Repository unavailable', 'Please refresh the page or view the original repository on GitHub.');
}

async function initialise() {
  try {
    const configResponse = await fetch('repository-config.json', { cache: 'default' });
    if (!configResponse.ok) throw new Error('Configuration unavailable');
    const config = await configResponse.json();
    const apiBase = `https://api.github.com/repos/${encodeURIComponent(config.owner)}/${encodeURIComponent(config.repo)}`;
    const apiOptions = {
      cache: 'default',
      headers: { Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' }
    };
    const [metadataResponse, treeResponse, commitsResponse] = await Promise.all([
      fetch(apiBase, apiOptions),
      fetch(`${apiBase}/git/trees/${encodeURIComponent(config.branch)}?recursive=1`, apiOptions),
      fetch(`${apiBase}/commits?sha=${encodeURIComponent(config.branch)}&per_page=1`, apiOptions)
    ]);
    if (![metadataResponse, treeResponse, commitsResponse].every(response => response.ok)) {
      throw new Error('GitHub API unavailable');
    }
    const [metadata, treeData, commits] = await Promise.all([
      metadataResponse.json(), treeResponse.json(), commitsResponse.json()
    ]);
    if (treeData.truncated) throw new Error('GitHub returned a truncated repository tree');
    repository = { config, entries: entriesFromGitTree(treeData.tree, config.maxFileSize) };
    const commit = commits[0];
    const files = repository.entries.filter(entry => entry.type === 'file').length;
    elements.title.textContent = config.title;
    elements.description.textContent = metadata.description || config.description;
    elements.repositoryLink.href = githubUrl(config);
    elements.technologies.replaceChildren(...config.technologies.map(value => {
      const chip = document.createElement('span');
      chip.className = 'chip';
      chip.textContent = value;
      return chip;
    }));
    const updated = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(commit.commit.author.date));
    elements.meta.textContent = `${config.owner}/${config.repo} · ${config.branch} · ${files} files · Updated ${updated} · ${commit.sha.slice(0, 7)} — ${commit.commit.message.split('\n')[0]}`;
    let initialPath = '';
    try { initialPath = normaliseRepositoryPath(new URLSearchParams(location.search).get('path') || ''); }
    catch { renderError('That repository path is not valid.'); return; }
    navigate(initialPath, true);
  } catch {
    renderError('GitHub is unavailable or has rate-limited this connection. Please try again shortly.');
  }
}

window.addEventListener('popstate', () => {
  if (repository) navigate(new URLSearchParams(location.search).get('path') || '', true);
});

initialise();
