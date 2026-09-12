# Linux `less`, `head`, `tail`, and `wc` Guide

These commands inspect large files and streams without opening them in an editor.

---

# `less`

```bash
less file.log
command | less
less +G file.log
less +F file.log
```

Useful keys:

```text
Space / b   page forward / backward
j / k       line down / up
g / G       beginning / end
/text       search forward
?text       search backward
n / N       next / previous match
F           follow growing file
Ctrl+C      stop following
q           quit
```

Useful options:

```bash
less -N file          # line numbers
less -S file          # chop long lines instead of wrapping
less -R file          # show ANSI colour escapes
```

`less` reads incrementally, so it works well for very large files. Compressed-file helpers include `zless`, `bzless`, and `xzless`.

---

# `head`

```bash
head file.txt
head -n 20 file.txt
head -n 1 *.csv
head -c 100 file.bin
```

Print everything except the last ten lines on GNU systems:

```bash
head -n -10 file.txt
```

Use `head` to inspect format and headers before processing a large dataset.

---

# `tail`

```bash
tail file.log
tail -n 100 file.log
tail -n +2 data.csv
tail -c 1K file
```

`tail -n +2` starts at line two, which is useful for skipping a header.

Follow a growing file:

```bash
tail -f application.log
tail -F application.log
```

```text
-f   follow the current file descriptor
-F   follow the filename and retry after rotation/replacement
```

Follow several files:

```bash
tail -F /var/log/app/*.log
```

Filter live output with line buffering:

```bash
tail -F application.log | grep --line-buffered -i error
```

---

# `wc`

```bash
wc file.txt
wc -l file.txt
wc -w file.txt
wc -c file.txt
wc -m file.txt
```

```text
-l   newline count
-w   word count
-c   byte count
-m   character count
-L   longest line length
```

`wc -l` counts newline characters. A non-empty final line without a terminating newline is not counted as a line by that definition.

Count output rows:

```bash
find . -type f -print0 | tr -cd '\0' | wc -c
```

For ordinary newline-safe output:

```bash
systemctl list-units --type=service --no-legend | wc -l
```

---

# Practical Examples

Inspect the start and end of a configuration:

```bash
head -n 20 app.conf
tail -n 20 app.conf
```

Skip a CSV header and preview rows:

```bash
tail -n +2 data.csv | head -n 10
```

Count errors:

```bash
grep -i 'error' application.log | wc -l
```

View recent service logs comfortably:

```bash
journalctl -u app.service -n 500 --no-pager | less
```

For logs managed by the journal, prefer `journalctl -f -u UNIT`; it understands journal rotation and metadata.

---

# Quick Reference

```bash
less -N file
head -n NUM file
tail -n NUM file
tail -n +NUM file
tail -F file
wc -l file
wc -c file
```
