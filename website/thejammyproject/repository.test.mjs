import test from 'node:test';
import assert from 'node:assert/strict';
import { buildBreadcrumbs, entriesForDirectory, githubUrl, isMarkdown, normaliseRepositoryPath } from './repository-core.mjs';

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
