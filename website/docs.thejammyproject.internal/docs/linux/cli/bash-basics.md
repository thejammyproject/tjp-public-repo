# Bash Basics Guide

Bash is both an interactive shell and a scripting language. Quoting and exit-status handling matter as much as command syntax.

---

# Variables and Quoting

```bash
name='server01'
printf 'Host: %s\n' "$name"
```

```text
'single quotes'   everything is literal
"double quotes"   expand variables and command substitutions
unquoted text     subject to word splitting and pathname expansion
```

Usually quote expansions:

```bash
cp -- "$source" "$destination"
```

Use arrays for lists of arguments:

```bash
files=("one file" "two file")
rm -- "${files[@]}"
```

---

# Environment Variables

Shell variables are not inherited by child processes until exported:

```bash
environment=production
export environment
export LOG_LEVEL=info
LOG_LEVEL=debug command
```

Inspect:

```bash
printenv
printf '%s\n' "$PATH"
```

Do not store or print secrets casually; environments can be exposed through diagnostics and process interfaces.

---

# Exit Status and Conditions

`$?` is the previous command's exit status. Zero means success; non-zero means failure.

```bash
command
status=$?
printf 'status=%d\n' "$status"
```

Prefer testing the command directly:

```bash
if systemctl is-active --quiet nginx; then
    echo 'running'
else
    echo 'not running'
fi
```

Conditional execution:

```bash
command1 && command2   # command2 only after success
command1 || command2   # command2 only after failure
```

---

# Tests

```bash
[[ -f $file ]]
[[ -d $directory ]]
[[ -n $value ]]
[[ $environment == production ]]
(( count > 10 ))
```

Inside `[[ ... ]]`, unquoted variables are safer than in `[ ... ]`, but quote ordinary command arguments and expansions consistently.

---

# Loops

```bash
for host in server01 server02; do
    ssh "$host" uptime
done
```

Read lines safely:

```bash
while IFS= read -r line; do
    printf '%s\n' "$line"
done < file.txt
```

Arithmetic loop:

```bash
for ((i = 0; i < 3; i++)); do
    printf '%d\n' "$i"
done
```

---

# Functions and Arguments

```bash
log() {
    printf '%s %s\n' "$(date --iso-8601=seconds)" "$*" >&2
}

log 'deployment started'
```

Script/function parameters:

```text
$0       script name
$1..$9   positional parameters
$#       number of parameters
"$@"     every parameter, preserving boundaries
shift    discard $1 and move the rest left
```

```bash
for argument in "$@"; do
    printf '%s\n' "$argument"
done
```

---

# Safer Script Structure

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

main() {
    local config=${1:?usage: script CONFIG}
    [[ -f $config ]] || {
        printf 'not a file: %s\n' "$config" >&2
        return 1
    }
}

main "$@"
```

```text
-e          exit on many unhandled failures
-u          error on unset variables
-o pipefail fail a pipeline if any component fails
-E          inherit ERR traps in functions/subshell contexts
```

These options have edge cases; they do not replace explicit error handling. Validate scripts with:

```bash
bash -n script.sh
shellcheck script.sh
```

---

# Temporary Files and Cleanup

```bash
tmpdir=$(mktemp -d)
cleanup() { rm -rf -- "$tmpdir"; }
trap cleanup EXIT
```

Never invent predictable temporary filenames. Validate destructive targets and do not operate recursively on empty or unresolved variables.

---

# Common Gotchas

- `for item in $(command)` destroys whitespace boundaries; use arrays or `read`.
- `cmd | while read ...` may run the loop in a subshell.
- `source file` executes that file in the current shell.
- Globs that match nothing may remain literal unless shell options change.
- Bash syntax is not portable `/bin/sh` syntax.
- Prefer `printf` over `echo` when exact output matters.
