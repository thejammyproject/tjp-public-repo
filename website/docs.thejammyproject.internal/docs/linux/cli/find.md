# Linux `find` Guide

`find` walks a directory tree and applies tests or actions to each path.

---

# Basic Syntax

```bash
find STARTING_PATH [EXPRESSION]
```

```bash
find /var/log -type f -name '*.log'
```

Always include the starting path explicitly. Use `.` for the current directory.

---

# Find by Name and Type

```bash
find . -name '*.yaml'
find . -iname '*.jpg'
find /etc -type f -name '*.conf'
find /srv -type d -name cache
find /dev -type l
```

Common types:

```text
f = regular file
d = directory
l = symbolic link
b = block device
c = character device
s = socket
p = named pipe
```

Quote wildcard patterns. Without quotes, the shell may expand `*.log` before `find` receives it.

---

# Find by Size

```bash
find /var -type f -size +1G
find . -type f -size +100M -size -1G
find . -type f -empty
```

```text
c = bytes
k = KiB
M = MiB
G = GiB
+ = greater than
- = less than
```

Show large files with human-readable sizes:

```bash
find /var -xdev -type f -size +500M -exec ls -lh {} +
```

---

# Find by Time

```bash
find /var/log -type f -mtime -1
find /tmp -type f -mtime +7
find . -type f -mmin -60
find . -type f -newer reference.file
```

```text
-mtime -1   modified less than one 24-hour period ago
-mtime +7   modified more than seven 24-hour periods ago
-mmin -60   modified within the last 60 minutes
```

For exact boundaries, use GNU `find` with reference timestamps:

```bash
find /var/log -type f -newermt '2026-09-12 09:00' ! -newermt '2026-09-12 10:00'
```

---

# Find by Ownership and Permissions

```bash
find /srv -user www-data
find /srv -group developers
find /srv -nouser -o -nogroup
find . -type f -perm 0644
find . -type f -perm /002
```

`-perm /002` finds files writable by “other”. Keep `-o` expressions grouped when combined with other tests:

```bash
find /srv \( -nouser -o -nogroup \) -print
```

---

# Control the Search

```bash
find . -maxdepth 1 -type f
find . -mindepth 2 -maxdepth 3 -type d
find / -xdev -type f -size +1G
find . -path './.git' -prune -o -type f -name '*.sh' -print
```

`-xdev` stays on one filesystem. It is useful when searching `/` so mounted network filesystems and virtual filesystems are not traversed.

---

# Run Commands with `-exec`

Run once per file:

```bash
find . -type f -name '*.log' -exec gzip -- {} \;
```

Pass many paths per command, which is usually faster:

```bash
find . -type f -name '*.log' -exec gzip -- {} +
```

Interactive confirmation:

```bash
find . -type f -name '*.bak' -ok rm -- {} \;
```

Run from each file's containing directory:

```bash
find . -type f -name '*.sha256' -execdir sha256sum -c -- {} \;
```

---

# Safe Deletion

First print exactly what will match:

```bash
find /tmp/my-app -type f -name '*.tmp' -mtime +7 -print
```

Only then add deletion:

```bash
find /tmp/my-app -type f -name '*.tmp' -mtime +7 -delete
```

Important:

- Put restrictive tests before `-delete`.
- `-delete` implies depth-first traversal.
- Check the starting path carefully.
- Avoid broad commands against `/`, `/home`, or an unresolved variable.
- Prefer a dry run using `-print`.

Delete empty directories:

```bash
find /srv/app/cache -depth -type d -empty -delete
```

---

# Combining Conditions

`find` implicitly joins adjacent tests with AND.

```bash
find . -type f -name '*.log' -size +100M
```

Explicit operators:

```text
-a          AND
-o          OR
!           NOT
\( ... \)   grouping
```

```bash
find . -type f \( -name '*.yaml' -o -name '*.yml' \)
find . -type f ! -user root
```

---

# `find` with `xargs`

Filenames can contain spaces, quotes, and newlines. Use NUL delimiters:

```bash
find . -type f -name '*.log' -print0 | xargs -0 gzip
```

`-exec ... {} +` is often simpler and avoids delimiter problems entirely:

```bash
find . -type f -name '*.log' -exec gzip -- {} +
```

Use `xargs` when you need batching, parallelism, or to place arguments somewhere other than the end.

---

# Infrastructure Examples

Files larger than 1 GiB on the root filesystem:

```bash
sudo find / -xdev -type f -size +1G -exec ls -lh {} +
```

Configuration files changed in the last hour:

```bash
find /etc -type f -mmin -60 -print
```

World-writable files:

```bash
find /srv -xdev -type f -perm /002 -print
```

Broken symbolic links:

```bash
find /srv -xtype l -print
```

Largest files under a directory:

```bash
find /var/log -type f -printf '%s %p\n' | sort -nr | head
```

---

# Quick Reference

```bash
find . -type f -name '*.log'
find . -type f -mmin -60
find . -type f -size +1G
find . -type f -user root
find . -type f -exec command -- {} +
find . -path './vendor' -prune -o -type f -print
```
