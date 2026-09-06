import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdir, readFile, readdir, rm, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { languageForPath } from '../repository-core.mjs';

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const siteDirectory = path.resolve(scriptDirectory, '..');
const repositoryRoot = path.resolve(siteDirectory, '..', '..');
const outputDirectory = path.join(siteDirectory, 'repository-data');
const config = JSON.parse(await readFile(path.join(siteDirectory, 'repository-config.json'), 'utf8'));
const ignored = config.ignoredPaths.map(item => item.replaceAll('\\', '/').replace(/^\/+|\/+$/g, ''));
const entries = [];
const seenDirectories = new Set(['']);

function isIgnored(relativePath) {
  const parts = relativePath.split('/');
  return ignored.some(item => relativePath === item || relativePath.startsWith(`${item}/`) || (!item.includes('/') && parts.includes(item)));
}

function looksBinary(buffer) {
  const sample = buffer.subarray(0, Math.min(buffer.length, 8000));
  return sample.includes(0);
}

async function walk(directory) {
  const children = await readdir(path.join(repositoryRoot, directory), { withFileTypes: true });
  for (const child of children) {
    const relativePath = path.posix.join(directory, child.name);
    if (isIgnored(relativePath)) continue;
    if (child.isDirectory()) {
      seenDirectories.add(relativePath);
      entries.push({ path: relativePath, parent: directory, name: child.name, type: 'directory' });
      await walk(relativePath);
      continue;
    }
    if (!child.isFile()) continue;

    const fileStats = await stat(path.join(repositoryRoot, relativePath));
    const entry = {
      path: relativePath,
      parent: directory,
      name: child.name,
      type: 'file',
      size: fileStats.size,
      language: languageForPath(relativePath),
      viewable: false
    };
    if (fileStats.size > config.maxFileSize) {
      entry.unavailableReason = 'This file is too large to preview safely.';
    } else {
      const content = await readFile(path.join(repositoryRoot, relativePath));
      if (looksBinary(content)) {
        entry.unavailableReason = 'Preview unavailable for this binary file.';
      } else {
        const id = createHash('sha256').update(relativePath).digest('hex').slice(0, 20);
        entry.dataFile = `repository-data/files/${id}.json`;
        entry.viewable = true;
        await writeFile(path.join(outputDirectory, 'files', `${id}.json`), `${JSON.stringify({ content: content.toString('utf8') })}\n`);
      }
    }
    entries.push(entry);
  }
}

await rm(outputDirectory, { recursive: true, force: true });
await mkdir(path.join(outputDirectory, 'files'), { recursive: true });
await walk('');

let commit = { message: 'Static repository snapshot', date: new Date().toISOString(), shortSha: '' };
try {
  const raw = execFileSync('git', ['log', '-1', '--format=%h%x00%cI%x00%s'], { cwd: repositoryRoot, encoding: 'utf8' }).trim();
  const [shortSha, date, message] = raw.split('\0');
  commit = { shortSha, date, message };
} catch {
  // The browser remains useful when the source tree is built outside Git.
}

const manifest = {
  generatedAt: new Date().toISOString(),
  config: Object.fromEntries(Object.entries(config).filter(([key]) => key !== 'ignoredPaths' && key !== 'maxFileSize')),
  commit,
  counts: {
    files: entries.filter(entry => entry.type === 'file').length,
    directories: seenDirectories.size - 1
  },
  entries
};

await writeFile(path.join(outputDirectory, 'manifest.json'), `${JSON.stringify(manifest)}\n`);
console.log(`Generated ${manifest.counts.files} files and ${manifest.counts.directories} directories.`);
