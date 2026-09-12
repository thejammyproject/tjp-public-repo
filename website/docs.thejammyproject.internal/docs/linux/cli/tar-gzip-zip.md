# Linux Archive and Compression Guide

`tar` combines files into an archive. `gzip`, `bzip2`, and `xz` compress streams. ZIP combines archiving and compression in one format.

---

# `tar` Basics

Create an archive:

```bash
tar -cf archive.tar directory/
```

List contents:

```bash
tar -tf archive.tar
```

Extract:

```bash
tar -xf archive.tar
tar -xf archive.tar -C /destination
```

```text
-c   create
-x   extract
-t   list
-f   archive filename follows
-v   verbose
-C   change directory
```

---

# Compressed Tar Archives

```bash
tar -czf archive.tar.gz directory/
tar -cjf archive.tar.bz2 directory/
tar -cJf archive.tar.xz directory/
```

Extract:

```bash
tar -xzf archive.tar.gz
tar -xjf archive.tar.bz2
tar -xJf archive.tar.xz
```

GNU `tar` often detects compression during extraction, so `tar -xf archive.tar.gz` also works.

```text
-z   gzip: fast and common
-j   bzip2: older, generally slower
-J   xz: often smaller, more CPU and memory
```

---

# Select and Exclude Paths

```bash
tar -czf app.tar.gz app/ --exclude='app/cache' --exclude='*.log'
tar -xzf app.tar.gz app/config.yml
tar -tf app.tar.gz | less
```

Archive from a parent directory to avoid unwanted leading paths:

```bash
tar -C /srv -czf app.tar.gz app/
```

---

# Standalone Compression

```bash
gzip file.log
gzip -k file.log
gunzip file.log.gz
gzip -cd file.log.gz | less
```

Equivalent tools:

```bash
bzip2 file
bunzip2 file.bz2
xz file
unxz file.xz
```

Test compressed data:

```bash
gzip -t archive.tar.gz
xz -t archive.tar.xz
```

---

# ZIP

```bash
zip archive.zip file1 file2
zip -r archive.zip directory/
unzip -l archive.zip
unzip archive.zip
unzip archive.zip -d destination/
```

ZIP is convenient for cross-platform exchange. Tar better preserves common Unix metadata and is conventional for Linux trees.

---

# Safety

Inspect an unfamiliar archive before extraction:

```bash
tar -tf archive.tar.gz | less
unzip -l archive.zip | less
```

Extract as an unprivileged user into a new empty directory. Malicious archives may contain absolute paths, `..` traversal, symlinks, device nodes, or paths intended to overwrite existing files.

Avoid extracting untrusted archives directly into `/`, `/etc`, a home directory, or an application directory.

---

# Infrastructure Examples

Archive configuration while preserving permissions:

```bash
sudo tar -C / -czf etc-nginx.tar.gz etc/nginx
```

Stream an archive over SSH without an intermediate file:

```bash
tar -C /srv -czf - app/ | ssh backup 'cat > app.tar.gz'
```

View a compressed log:

```bash
zless application.log.gz
zgrep -i error application.log.gz
```

An archive copy is not automatically a complete, consistent backup. Databases and active applications may require snapshots or application-aware backup procedures.
