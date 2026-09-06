const LANGUAGE_BY_EXTENSION = {
  '.css': 'css', '.html': 'xml', '.htm': 'xml', '.ini': 'ini', '.conf': 'ini',
  '.js': 'javascript', '.jsx': 'javascript', '.json': 'json', '.md': 'markdown',
  '.py': 'python', '.sh': 'bash', '.bash': 'bash', '.tf': 'terraform',
  '.ts': 'typescript', '.tsx': 'typescript', '.yaml': 'yaml', '.yml': 'yaml',
  '.txt': 'plaintext', '.xml': 'xml'
};

export function normaliseRepositoryPath(value = '') {
  let decoded;
  try {
    decoded = decodeURIComponent(String(value));
  } catch {
    throw new Error('Invalid repository path.');
  }
  const path = decoded.replaceAll('\\', '/').replace(/^\/+|\/+$/g, '');
  if (path.includes('\0') || path.split('/').some(part => part === '..' || part === '.')) {
    throw new Error('Invalid repository path.');
  }
  return path;
}

export function languageForPath(path) {
  const name = path.split('/').pop().toLowerCase();
  if (name === 'dockerfile' || name.startsWith('dockerfile.')) return 'dockerfile';
  const dot = name.lastIndexOf('.');
  return LANGUAGE_BY_EXTENSION[name.slice(dot)] || 'plaintext';
}

export function isMarkdown(path) {
  return /(?:^|\/)readme(?:\.[^/]*)?\.md$/i.test(path) || /\.md$/i.test(path);
}

export function buildBreadcrumbs(path) {
  const safePath = normaliseRepositoryPath(path);
  const parts = safePath ? safePath.split('/') : [];
  return [{ label: 'repository', path: '' }, ...parts.map((label, index) => ({
    label,
    path: parts.slice(0, index + 1).join('/')
  }))];
}

export function entriesForDirectory(entries, directory = '') {
  const safeDirectory = normaliseRepositoryPath(directory);
  return entries
    .filter(entry => entry.parent === safeDirectory)
    .sort((a, b) => Number(b.type === 'directory') - Number(a.type === 'directory') || a.name.localeCompare(b.name));
}

export function githubUrl(config, path = '', type = 'directory') {
  const safePath = normaliseRepositoryPath(path);
  const base = `https://github.com/${encodeURIComponent(config.owner)}/${encodeURIComponent(config.repo)}`;
  if (!safePath) return base;
  const encodedPath = safePath.split('/').map(encodeURIComponent).join('/');
  return `${base}/${type === 'file' ? 'blob' : 'tree'}/${encodeURIComponent(config.branch)}/${encodedPath}`;
}
