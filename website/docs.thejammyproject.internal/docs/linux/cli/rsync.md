# Linux `rsync` Guide

`rsync` efficiently copies and synchronises files locally or over SSH.

---

# Basic Syntax

```bash
rsync [OPTIONS] SOURCE DESTINATION
```

Local copy:

```bash
rsync -av source/ destination/
```

Remote copy:

```bash
rsync -av source/ user@server:/srv/data/
rsync -av user@server:/var/log/app/ ./app-logs/
```

---

# Options Worth Knowing

```text
-a              archive mode
-v              verbose
-h              human-readable numbers
-z              compress transfer data
-n, --dry-run   preview
--progress      per-file progress
--info=progress2 overall progress
--delete        delete destination entries absent from source
--exclude       omit matching paths
-e ssh          use SSH transport
```

Archive mode roughly preserves recursion, symlinks, permissions, timestamps, groups, owners, and devices. Some preservation requires privileges; ACLs and extended attributes need `-A` and `-X`.

---

# The Trailing-Slash Rule

```bash
rsync -a source/ destination/
```

copies the contents of `source` into `destination`.

```bash
rsync -a source destination/
```

creates or updates `destination/source`.

This is one of the most important `rsync` details. Use a dry run whenever the layout matters.

---

# Safe Synchronisation

Preview first:

```bash
rsync -avhn --delete source/ destination/
```

Then remove `-n` after checking every source, destination, exclusion, and deletion.

`--delete` makes the destination mirror the source and can remove large amounts of data. Useful variants include:

```text
--delete-before
--delete-during
--delete-after
--max-delete=NUM
```

Use `--max-delete` as an additional guardrail, not as a substitute for a dry run.

---

# Exclusions

```bash
rsync -av --exclude='cache/' --exclude='*.log' app/ server:/srv/app/
rsync -av --exclude-from='.rsync-exclude' source/ destination/
```

Patterns are relative to the transfer root and have their own matching rules. Confirm them with `--dry-run` and `--itemize-changes`.

---

# SSH Options

```bash
rsync -av -e 'ssh -p 2222' source/ user@server:/srv/data/
```

For automation, configure host, port, user, and identity in `~/.ssh/config`:

```bash
rsync -av source/ app-prod:/srv/data/
```

---

# Partial Transfers and Bandwidth

```bash
rsync -av --partial --info=progress2 large-file server:/backup/
rsync -av --bwlimit=20m source/ server:/backup/
```

`--partial-dir=.rsync-partial` keeps partial data separate. Consider its storage and cleanup implications.

---

# Useful Infrastructure Patterns

Deploy files but keep runtime data:

```bash
rsync -avhn --delete \
    --exclude='.env' --exclude='uploads/' --exclude='cache/' \
    ./ app-prod:/srv/app/
```

Backup while preserving hard links, ACLs, and xattrs:

```bash
sudo rsync -aHAX --numeric-ids /srv/data/ /backup/data/
```

Show exactly what changes:

```bash
rsync -avni --itemize-changes source/ destination/
```

---

# Gotchas

- `rsync` is a synchronisation tool, not inherently a versioned backup.
- A bad source plus `--delete` can propagate loss.
- Open databases may not produce transactionally consistent copies.
- `-z` can waste CPU on fast networks or already compressed data.
- UID/GID name mapping can differ across hosts; understand `--numeric-ids`.
- Root privileges on the sending side do not grant root privileges remotely.

Always verify restore procedures, not only copy completion.
