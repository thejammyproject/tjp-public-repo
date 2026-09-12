# Linux `xargs` Guide

`xargs` reads items from standard input and turns them into arguments for another command.

```text
standard input -> xargs -> command arguments
```

---

# Basic Syntax

```bash
printf '%s\n' file1 file2 file3 | xargs ls -l
```

This runs approximately:

```bash
ls -l file1 file2 file3
```

Many commands do not read filenames from standard input. `xargs` bridges that gap.

---

# Options Worth Knowing

```text
-0          input is NUL-delimited
-n NUM      use at most NUM items per command
-P NUM      run up to NUM commands in parallel
-I TOKEN    replace TOKEN in the command
-r          do not run if input is empty (GNU)
-t          print commands before running them
-p          ask before each command
```

Examples:

```bash
printf '%s\n' one two three four | xargs -n 2 echo
printf '%s\n' server01 server02 | xargs -n 1 -P 2 ping -c 1
printf '%s\n' alice bob | xargs -I USER echo 'Hello USER'
```

---

# Safe Filename Handling

This is unsafe because filenames may contain whitespace or quotes:

```bash
find . -type f -name '*.log' | xargs gzip
```

Use a NUL-delimited stream:

```bash
find . -type f -name '*.log' -print0 | xargs -0 -r gzip
```

Other commands that can emit NUL delimiters include:

```bash
printf '%s\0' ...
rg -l --null PATTERN
```

---

# Batching and Parallelism

Limit arguments per invocation:

```bash
find . -type f -print0 | xargs -0 -n 20 sha256sum
```

Run four workers:

```bash
find backups -type f -name '*.gz' -print0 |
    xargs -0 -r -n 1 -P 4 gzip -t
```

Parallel commands may print interleaved output. Do not use `-P` when commands modify shared state unless concurrency is safe.

`-P 0` means “as many processes as possible” on GNU systems and can overload a host. Prefer an explicit limit.

---

# Placing the Argument

By default, `xargs` appends arguments to the command. Use `-I` when the item belongs elsewhere:

```bash
printf '%s\n' server01 server02 |
    xargs -I HOST ssh HOST 'uptime'
```

`-I` normally implies one input line per command and is less efficient than batching.

For shell syntax, invoke a shell deliberately and pass the item as an argument:

```bash
find . -type f -name '*.conf' -print0 |
    xargs -0 -r -n 1 sh -c 'cp -- "$1" "$1.bak"' sh
```

The first `sh` after the script becomes `$0`; each pathname becomes `$1`.

---

# `xargs` vs `find -exec`

Prefer `find -exec ... {} +` when:

- You only need to append paths.
- You want straightforward safe filename handling.
- You do not need parallel execution.

```bash
find . -type f -name '*.log' -exec gzip -- {} +
```

Prefer `xargs` when:

- Input comes from something other than `find`.
- You need `-P` parallelism.
- You need controlled batch sizes.
- Arguments must appear in a custom position.

---

# Infrastructure Examples

Check several URLs concurrently:

```bash
printf '%s\n' https://app1.example.com https://app2.example.com |
    xargs -r -n 1 -P 4 curl -fsS -o /dev/null
```

Search files selected by `find`:

```bash
find /etc/nginx -type f -name '*.conf' -print0 |
    xargs -0 -r grep -nH 'proxy_pass'
```

Restart a controlled list of services one at a time:

```bash
printf '%s\n' app-worker app-scheduler |
    xargs -r -n 1 sudo systemctl restart
```

Preview generated commands:

```bash
printf '%s\n' *.log | xargs -r -n 1 -t gzip
```

---

# Gotchas

- Use `-0` with filenames from `find -print0`.
- GNU `xargs` can run the command once even with empty input; use `-r`.
- Input is data, not shell syntax, unless you explicitly invoke a shell.
- `-I` changes batching behaviour.
- Check command length and concurrency on production systems.
- Avoid using untrusted input inside a shell script string.

---

# Quick Reference

```bash
producer | xargs -r command
producer | xargs -r -n 1 command
producer | xargs -r -n 1 -P 4 command
producer0 | xargs -0 -r command
producer | xargs -I ITEM command ITEM
```
