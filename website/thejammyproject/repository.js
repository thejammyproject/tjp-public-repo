import { buildBreadcrumbs, entriesForDirectory, entriesFromGitTree, githubUrl, isMarkdown, normaliseRepositoryPath, rawGithubUrl, relativeTime } from './repository-core.js';

const elements = {
  title: document.getElementById('repository-title'),
  description: document.getElementById('repository-description'),
  meta: document.getElementById('repository-meta'),
  repositoryLink: document.getElementById('repository-github-link'),
  currentLink: document.getElementById('current-github-link'),
  syncStatus: document.getElementById('sync-status'),
  breadcrumbs: document.getElementById('breadcrumbs'),
  directoryStatus: document.getElementById('directory-status'),
  repositoryTree: document.getElementById('repository-tree'),
  filePanel: document.getElementById('file-panel')
};

let repository;
let currentPath = '';
let apiBase;
let apiOptions;
let lastSyncedAt = 0;
let refreshInFlight;
const entryTimestampCache = new Map();
const expandedDirectories = new Set(['']);
const AUTO_SYNC_INTERVAL = 300_000;

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

function iconForEntry(entry) {
  const icon = document.createElement('span');
  icon.className = `entry-icon ${entry.type}`;
  icon.setAttribute('aria-hidden', 'true');
  return icon;
}

function renderBreadcrumbs(entry) {
  elements.breadcrumbs.replaceChildren();
  for (const [index, crumb] of buildBreadcrumbs(currentPath).entries()) {
    const label = index === 0 ? repository.config.repo : crumb.label;
    if (index) elements.breadcrumbs.append(document.createTextNode(' / '));
    if (crumb.path === currentPath) {
      const current = document.createElement('span');
      current.textContent = label;
      current.setAttribute('aria-current', 'page');
      elements.breadcrumbs.append(current);
    } else {
      elements.breadcrumbs.append(createPathButton(label, crumb.path));
    }
  }
  elements.currentLink.href = githubUrl(repository.config, currentPath, entry?.type || 'directory');
}

function expandPath(path) {
  const parts = path ? path.split('/') : [];
  expandedDirectories.add('');
  parts.forEach((_, index) => expandedDirectories.add(parts.slice(0, index + 1).join('/')));
}

function renderTree() {
  elements.repositoryTree.replaceChildren();
  elements.directoryStatus.hidden = true;

  function appendEntries(parent, list, depth) {
    for (const entry of entriesForDirectory(repository.entries, parent)) {
      const item = document.createElement('li');
      item.className = 'tree-item';
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'tree-entry';
      button.style.paddingLeft = `${.65 + depth}rem`;
      button.setAttribute('aria-current', entry.path === currentPath ? 'page' : 'false');

      const disclosure = document.createElement('span');
      disclosure.className = 'tree-disclosure';
      if (entry.type === 'directory') {
        const expanded = expandedDirectories.has(entry.path);
        disclosure.textContent = expanded ? '⌄' : '›';
        button.setAttribute('aria-expanded', String(expanded));
      }
      const icon = iconForEntry(entry);
      const label = document.createElement('span');
      label.className = 'tree-label';
      label.textContent = entry.name;
      button.replaceChildren(disclosure, icon, label);
      button.setAttribute('aria-label', `${entry.type === 'directory' ? 'Open folder' : 'Open file'} ${entry.path}`);
      if (entry.type === 'directory') {
        button.addEventListener('click', () => {
          expandedDirectories.has(entry.path) ? expandedDirectories.delete(entry.path) : expandedDirectories.add(entry.path);
          navigate(entry.path);
        });
      } else button.addEventListener('click', () => navigate(entry.path));
      item.append(button);
      list.append(item);

      if (entry.type === 'directory' && expandedDirectories.has(entry.path)) {
        const nested = document.createElement('ul');
        nested.className = 'tree-group';
        item.append(nested);
        appendEntries(entry.path, nested, depth + 1);
      }
    }
  }

  appendEntries('', elements.repositoryTree, 0);
}

function createDirectoryListing(directory) {
  const wrapper = document.createElement('div');
  wrapper.className = 'directory-view';
  const table = document.createElement('div');
  table.className = 'directory-table';
  const tableHeader = document.createElement('div');
  tableHeader.className = 'directory-table-header';
  tableHeader.innerHTML = '<span>Name</span><span>Type</span><span>Size</span><span>Updated</span>';
  table.append(tableHeader);
  const timeTargets = new Map();

  if (directory) {
    const item = document.createElement('div');
    const parentPath = directory.split('/').slice(0, -1).join('/');
    const button = createPathButton('..', parentPath, 'directory-row');
    button.replaceChildren(iconForEntry({ type: 'directory' }), document.createTextNode('..'), document.createElement('span'), document.createElement('span'), document.createElement('span'));
    item.append(button);
    table.append(item);
  }

  const children = entriesForDirectory(repository.entries, directory);
  for (const entry of children) {
    const item = document.createElement('div');
    const button = createPathButton(entry.name, entry.path, 'directory-row');
    const icon = iconForEntry(entry);
    const label = document.createElement('span');
    label.className = 'directory-name';
    label.textContent = entry.name;
    const type = document.createElement('span');
    type.className = 'directory-detail';
    type.textContent = entry.type === 'directory' ? 'Directory' : entry.language;
    const size = document.createElement('span');
    size.className = 'directory-size';
    size.textContent = entry.type === 'directory' ? '—' : formatBytes(entry.size);
    const updated = document.createElement('span');
    updated.className = 'directory-updated';
    updated.textContent = '…';
    button.replaceChildren(icon, label, type, size, updated);
    timeTargets.set(entry.path, updated);
    button.setAttribute('aria-label', `${entry.type === 'directory' ? 'Open folder' : 'Open file'} ${entry.name}`);
    item.append(button);
    table.append(item);
  }

  if (!children.length) {
    const empty = document.createElement('p');
    empty.className = 'directory-empty';
    empty.textContent = 'This directory is empty.';
    table.append(empty);
  }
  wrapper.append(table);
  return { wrapper, children, timeTargets };
}

async function entryTimestamp(path) {
  if (entryTimestampCache.has(path)) return entryTimestampCache.get(path);
  const query = new URLSearchParams({ sha: repository.config.branch, path, per_page: '1' });
  try {
    const response = await fetch(`${apiBase}/commits?${query}`, apiOptions);
    if (!response.ok) throw new Error('Commit history unavailable');
    const commits = await response.json();
    const timestamp = commits[0]?.commit?.author?.date || null;
    entryTimestampCache.set(path, timestamp);
    return timestamp;
  } catch {
    entryTimestampCache.set(path, null);
    return null;
  }
}

async function hydrateDirectoryTimes(children, timeTargets, directory) {
  await Promise.all(children.map(async entry => {
    const timestamp = await entryTimestamp(entry.path);
    if (currentPath !== directory || !timeTargets.get(entry.path)?.isConnected) return;
    const target = timeTargets.get(entry.path);
    target.textContent = timestamp ? relativeTime(timestamp) : '—';
    if (timestamp) target.title = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(timestamp));
  }));
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

async function renderDirectoryPanel(directory) {
  const { wrapper: listing, children, timeTargets } = createDirectoryListing(directory);
  elements.filePanel.replaceChildren(listing);
  hydrateDirectoryTimes(children, timeTargets, directory);
  const readme = repository.entries.find(item => item.parent === directory && item.type === 'file' && /^readme\.md$/i.test(item.name));
  if (!readme?.viewable) return;

  try {
    const response = await fetch(rawGithubUrl(repository.config, readme.path), { cache: 'default' });
    if (!response.ok) return;
    const content = await response.text();
    if (currentPath !== directory) return;
    const readmePanel = document.createElement('section');
    readmePanel.className = 'readme-panel';
    const header = document.createElement('header');
    header.className = 'file-header';
    const heading = document.createElement('h2');
    heading.textContent = 'README.md';
    header.append(heading);
    readmePanel.append(header, renderMarkdown(content));
    listing.append(readmePanel);
  } catch {
    // The directory browser remains usable when a README cannot be fetched.
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
  const treePath = entry?.type === 'file'
    ? entry.parent
    : currentPath.split('/').slice(0, -1).join('/');
  expandPath(treePath);
  renderTree();
  if (entry?.type === 'file') {
    renderFile(entry);
    return;
  }
  const directory = entry?.path || '';
  renderDirectoryPanel(directory);
}

function renderError(message) {
  elements.repositoryTree.replaceChildren();
  elements.directoryStatus.hidden = false;
  elements.directoryStatus.textContent = message;
  renderEmptyPanel('Repository unavailable', 'Please refresh the page or view the original repository on GitHub.');
}

function updateSyncStatus(message) {
  elements.syncStatus.textContent = message || (lastSyncedAt ? `Synced ${relativeTime(lastSyncedAt)} · Auto-sync on` : 'Connecting to GitHub…');
}

async function refreshRepository(config, { initial = false } = {}) {
  if (refreshInFlight) return refreshInFlight;
  refreshInFlight = (async () => {
    updateSyncStatus('Syncing with GitHub…');
    try {
      const requests = [
        fetch(`${apiBase}/git/trees/${encodeURIComponent(config.branch)}?recursive=1`, apiOptions),
        fetch(`${apiBase}/commits?sha=${encodeURIComponent(config.branch)}&per_page=1`, apiOptions)
      ];
      if (initial) requests.unshift(fetch(apiBase, apiOptions));
      const responses = await Promise.all(requests);
      if (!responses.every(response => response.ok)) throw new Error('GitHub API unavailable');
      const payloads = await Promise.all(responses.map(response => response.json()));
      const metadata = initial ? payloads[0] : null;
      const treeData = payloads[initial ? 1 : 0];
      const commits = payloads[initial ? 2 : 1];
      if (treeData.truncated) throw new Error('GitHub returned a truncated repository tree');
      const commit = commits[0];
      const previousSha = repository?.headSha;
      repository = { config, entries: entriesFromGitTree(treeData.tree, config.maxFileSize), headSha: commit.sha };
      if (previousSha && previousSha !== commit.sha) entryTimestampCache.clear();
      const files = repository.entries.filter(entry => entry.type === 'file').length;
      if (initial) {
        elements.title.textContent = config.title;
        elements.description.textContent = metadata.description || config.description;
        elements.repositoryLink.href = githubUrl(config);
      }
      const updated = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(commit.commit.author.date));
      elements.meta.textContent = `${config.owner}/${config.repo} · ${config.branch} · ${files} files · Updated ${updated} · ${commit.sha.slice(0, 7)} — ${commit.commit.message.split('\n')[0]}`;
      lastSyncedAt = Date.now();
      updateSyncStatus();
      renderLocation();
    } catch {
      if (!repository) renderError('GitHub is unavailable or has rate-limited this connection. Please try again shortly.');
      updateSyncStatus(repository ? 'Sync delayed · GitHub unavailable' : 'Unable to connect to GitHub');
    } finally {
      refreshInFlight = null;
    }
  })();
  return refreshInFlight;
}

async function initialise() {
  try {
    const configResponse = await fetch('repository-config.json', { cache: 'default' });
    if (!configResponse.ok) throw new Error('Configuration unavailable');
    const config = await configResponse.json();
    apiBase = `https://api.github.com/repos/${encodeURIComponent(config.owner)}/${encodeURIComponent(config.repo)}`;
    apiOptions = {
      cache: 'default',
      headers: { Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' }
    };
    try { currentPath = normaliseRepositoryPath(new URLSearchParams(location.search).get('path') || ''); }
    catch { renderError('That repository path is not valid.'); return; }
    await refreshRepository(config, { initial: true });
    setInterval(() => refreshRepository(config), AUTO_SYNC_INTERVAL);
    setInterval(() => updateSyncStatus(), 60_000);
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible' && Date.now() - lastSyncedAt >= AUTO_SYNC_INTERVAL) refreshRepository(config);
    });
  } catch {
    renderError('GitHub is unavailable or has rate-limited this connection. Please try again shortly.');
  }
}

window.addEventListener('popstate', () => {
  if (repository) navigate(new URLSearchParams(location.search).get('path') || '', true);
});

initialise();
