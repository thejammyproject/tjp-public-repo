import test from 'node:test';
import assert from 'node:assert/strict';
import { buildBreadcrumbs, entriesForDirectory, entriesFromGitTree, githubUrl, isMarkdown, normaliseRepositoryPath, rawGithubUrl, relativeTime } from './repository-core.js';

test('normalises valid paths and rejects traversal', () => {
  assert.equal(normaliseRepositoryPath('/deploy/k8s/'), 'deploy/k8s');
  assert.throws(() => normaliseRepositoryPath('../../etc/passwd'), /Invalid/);
  assert.throws(() => normaliseRepositoryPath('%2e%2e/secrets'), /Invalid/);
});

test('builds clickable breadcrumb paths', () => {
  assert.deepEqual(buildBreadcrumbs('deploy/k8s/app.yaml').map(item => item.path), ['', 'deploy', 'deploy/k8s', 'deploy/k8s/app.yaml']);
});

test('lists directories before files', () => {
  const entries = [
    { parent: '', name: 'README.md', type: 'file' },
    { parent: '', name: 'deploy', type: 'directory' }
  ];
  assert.deepEqual(entriesForDirectory(entries).map(item => item.name), ['deploy', 'README.md']);
});

test('recognises Markdown and creates fixed-repository GitHub links', () => {
  assert.equal(isMarkdown('docs/README.md'), true);
  assert.equal(githubUrl({ owner: 'owner', repo: 'repo', branch: 'main' }, 'a b.tf', 'file'), 'https://github.com/owner/repo/blob/main/a%20b.tf');
});

test('converts GitHub tree data and enforces the preview limit', () => {
  const entries = entriesFromGitTree([
    { path: 'deploy', type: 'tree' },
    { path: 'deploy/app.yaml', type: 'blob', size: 200 },
    { path: 'archive.zip', type: 'blob', size: 600000 },
    { path: 'submodule', type: 'commit' }
  ], 524288);
  assert.deepEqual(entries.map(entry => entry.path), ['deploy', 'deploy/app.yaml', 'archive.zip']);
  assert.equal(entries[1].language, 'yaml');
  assert.equal(entries[1].viewable, true);
  assert.equal(entries[2].viewable, false);
});

test('creates raw-content URLs only for the configured repository', () => {
  assert.equal(
    rawGithubUrl({ owner: 'owner', repo: 'repo', branch: 'main' }, 'a b/file.yml'),
    'https://raw.githubusercontent.com/owner/repo/main/a%20b/file.yml'
  );
});

test('formats GitHub-style relative timestamps', () => {
  const now = Date.parse('2026-09-06T12:00:00Z');
  assert.equal(relativeTime('2026-09-06T09:00:00Z', now), '3 hours ago');
  assert.equal(relativeTime('2026-09-05T12:00:00Z', now), 'yesterday');
});
