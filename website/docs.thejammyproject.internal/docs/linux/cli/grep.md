# Linux `grep` Guide

`grep` searches text and prints lines that match a pattern.

```text
grep = find lines
sed  = modify lines
awk  = process fields and columns
```

---

# Basic Syntax

```bash
grep [OPTIONS] PATTERN [FILE...]
```

```bash
grep "error" application.log
```

Patterns are case-sensitive by default.

---

# Options Worth Memorising

```text
-i          ignore case
-v          invert the match
-n          show line numbers
-r          search directories recursively
-l          print only matching filenames
-c          count matching lines
-w          match a whole word
-x          match a whole line
-E          use extended regular expressions
-F          treat the pattern as literal text
-A NUM      show lines after a match
-B NUM      show lines before a match
-C NUM      show context on both sides
-m NUM      stop after NUM matches per file
-q          quiet; communicate through the exit status
```

Examples:

```bash
grep -in "failed" /var/log/application.log
grep -v '^#' /etc/ssh/sshd_config
grep -RIl "old.example.com" /etc
grep -C 3 "Out of memory" /var/log/syslog
```

Use `-I` or `--binary-files=without-match` when recursively searching trees that may contain binaries.

---

# Regular Expression Basics

Basic `grep` expressions:

```text
^       start of line
$       end of line
.       any one character
[abc]   one character from the set
[^abc]  one character not in the set
[0-9]   one digit
*       zero or more of the previous item
```

```bash
grep '^ERROR' application.log
grep 'timeout$' application.log
grep 'server[0-9]' inventory.txt
grep '^[[:space:]]*#' config.ini
grep '^$' file.txt
```

With `-E`, alternation, grouping, `+`, and `?` are easier to use:

```bash
grep -E 'ERROR|WARN' application.log
grep -E 'https?://' endpoints.txt
grep -E '^server(01|02)$' hosts.txt
```

Shell quoting matters. Single quotes normally protect the expression from shell expansion:

```bash
grep '$5' file        # searches for the end-of-line expression followed by 5: usually wrong
grep '\$5' file       # searches for the literal text $5
grep -F '$5' file     # simplest literal search
```

---

# Searching Logs and Configuration

```bash
grep -RIn --include='*.conf' 'listen' /etc/nginx
grep -RIn --exclude-dir='.git' 'api_key' .
journalctl -u nginx | grep -iE 'error|failed|timeout'
tail -F application.log | grep --line-buffered 'ERROR'
```

Patterns beginning with `-` must follow `--`:

```bash
grep -- '-Xmx' service.conf
```

Multiple patterns:

```bash
grep -e 'ERROR' -e 'WARN' application.log
grep -Ff known-errors.txt application.log
```

---

# Exit Status

```text
0 = at least one match
1 = no match
2 = an error occurred
```

This makes quiet mode useful in scripts:

```bash
if grep -q '^enabled=true$' app.conf; then
    echo "Feature enabled"
fi
```

Do not confuse “no match” with a command failure.

---

# Common Infrastructure Examples

Find listening web ports:

```bash
ss -lntp | grep -E ':(80|443)[[:space:]]'
```

Find failed SSH logins:

```bash
grep 'Failed password' /var/log/auth.log
```

Ignore comments and blank lines:

```bash
grep -Ev '^[[:space:]]*(#|$)' service.conf
```

Count HTTP 500 response lines:

```bash
grep -c ' 500 ' access.log
```

Search safely when filenames may contain spaces:

```bash
find /etc -type f -name '*.conf' -print0 |
    xargs -0 grep -nH 'example.com'
```

---

# `grep` vs `sed` vs `awk`

Use `grep` when the main question is:

```text
Which lines match?
```

Use `sed` when the main question is:

```text
How should each line be changed?
```

Use `awk` when the main question is:

```text
Which fields should be tested, calculated, or printed?
```

```bash
grep 'ERROR' app.log
sed 's/old-host/new-host/g' config
awk '$9 >= 500 {print $1, $7, $9}' access.log
```

Avoid unnecessary `grep` before `awk` because `awk` can filter by itself:

```bash
awk '/ERROR/ {print $1, $5}' application.log
```

---

# Safety and Gotchas

- Quote patterns so the shell does not expand them.
- Use `-F` for literal strings, especially generated input.
- Recursive searches can be expensive; limit the path and file types.
- `grep -c` counts matching lines, not total matches.
- `grep -o` prints each matched portion and can be combined with `wc -l`.
- `zgrep` searches gzip-compressed text without manual extraction.

---

# Quick Reference

```bash
grep 'text' file
grep -i 'text' file
grep -v 'text' file
grep -n 'text' file
grep -E 'one|two' file
grep -F 'literal.*text' file
grep -C 2 'text' file
grep -RIn --include='*.log' 'ERROR' /var/log/app
```
