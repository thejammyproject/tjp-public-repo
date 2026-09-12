# Linux `cut`, `sort`, `uniq`, and `tr` Guide

These small tools become powerful when combined in pipelines.

```text
cut   = select fields or character ranges
sort  = order lines
uniq  = collapse adjacent duplicate lines
tr    = translate or delete characters
```

---

# `cut`

Select delimited fields:

```bash
cut -d ':' -f 1 /etc/passwd
cut -d ',' -f 1,3 servers.csv
cut -d ':' -f 1,3-5 /etc/passwd
```

Select character positions:

```bash
cut -c 1-10 file.txt
cut -c 1,5,10- file.txt
```

Useful options:

```text
-d CHAR      field delimiter
-f LIST      fields to print
-c LIST      characters to print
--complement print everything except the selection
-s           omit lines without the delimiter
```

`cut` accepts a single-character delimiter and does not understand quoted CSV. Use a CSV-aware tool for data such as `"London, UK",prod`.

---

# `sort`

```bash
sort names.txt
sort -r names.txt
sort -n numbers.txt
sort -h sizes.txt
sort -u names.txt
```

Useful options:

```text
-n          numeric sort
-h          human-readable numeric sort: 2K, 10M, 1G
-r          reverse
-u          unique output
-f          ignore case
-t CHAR     field delimiter
-k KEY      sort key
-V          version-aware sort
```

Sort `/etc/passwd` numerically by UID:

```bash
sort -t ':' -k 3,3n /etc/passwd
```

Sort `du` output by size:

```bash
du -h --max-depth=1 /var | sort -h
```

`sort` uses the current locale. For stable byte-wise ordering in scripts:

```bash
LC_ALL=C sort file.txt
```

For very large inputs, `sort` may use temporary disk space. GNU options such as `-S` and `-T` control memory and the temporary directory.

---

# `uniq`

`uniq` only detects adjacent duplicates, so input usually needs sorting first.

```bash
sort names.txt | uniq
sort names.txt | uniq -c
sort names.txt | uniq -d
sort names.txt | uniq -u
```

```text
-c = prefix occurrence count
-d = print repeated lines
-u = print lines that occur once
-i = ignore case
```

Count and rank values:

```bash
sort values.txt | uniq -c | sort -nr
```

`sort -u` is a shorter way to sort and deduplicate when counts are not needed.

---

# `tr`

Translate characters:

```bash
printf '%s\n' 'hello' | tr '[:lower:]' '[:upper:]'
printf '%s\n' 'a,b,c' | tr ',' ':'
```

Delete characters:

```bash
printf '%s\n' '123-456-789' | tr -d '-'
```

Squeeze repeated characters:

```bash
printf '%s\n' 'too    many    spaces' | tr -s ' '
```

Convert spaces to newlines:

```bash
printf '%s\n' 'one two three' | tr ' ' '\n'
```

`tr` operates on characters, not words or regular expressions.

---

# Practical Pipelines

Most frequent client IP addresses in an access log:

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head
```

Most frequently used login shells:

```bash
cut -d ':' -f 7 /etc/passwd | sort | uniq -c | sort -nr
```

Unique listening TCP ports:

```bash
ss -lntH | awk '{print $4}' | awk -F: '{print $NF}' | sort -nu
```

Rank HTTP status codes:

```bash
awk '{print $9}' access.log | sort | uniq -c | sort -nr
```

Normalise a whitespace-separated list:

```bash
tr -s '[:space:]' '\n' < input.txt | sed '/^$/d' | sort -u
```

Top disk consumers in the current directory:

```bash
du -sh -- * | sort -h | tail
```

---

# Choosing the Right Tool

```text
Simple delimiter and fixed fields     cut
Whitespace or conditional fields      awk
Ordering lines                         sort
Counting repeated complete lines       sort | uniq -c
Character substitution or deletion     tr
Structured CSV with quoting            CSV-aware parser
```

---

# Quick Reference

```bash
cut -d ':' -f 1 /etc/passwd
sort -t ':' -k 3,3n /etc/passwd
sort file | uniq -c | sort -nr
tr '[:lower:]' '[:upper:]'
tr -d '\r' < windows.txt
tr -s ' ' < file.txt
```
