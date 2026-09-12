# Linux Pipes and Redirection Guide

Pipes and redirection control where commands read input and send output.

Every process normally begins with three standard streams:

```text
0 = stdin   standard input
1 = stdout  standard output
2 = stderr  standard error
```

---

# Pipes - `|`

A pipe sends one command's standard output to the next command's standard input.

```bash
producer | consumer
```

```bash
journalctl -u nginx | grep -i error
ps aux | sort -k 4 -nr | head
```

Only standard output enters the pipe by default. Standard error still goes to the terminal.

Pipe both output streams in Bash:

```bash
command 2>&1 | less
command |& less
```

---

# Redirect Standard Output

Overwrite a file:

```bash
command > output.txt
```

Append to a file:

```bash
command >> output.txt
```

The shell opens the destination before running the command. This is unsafe:

```bash
sort file.txt > file.txt
```

The shell truncates `file.txt` before `sort` reads it. Write to a separate file or use a tool's in-place facility where appropriate.

Prevent accidental overwrites in an interactive Bash session:

```bash
set -o noclobber
```

---

# Redirect Standard Error

```bash
command 2> errors.log
command 2>> errors.log
```

Send stdout and stderr to separate files:

```bash
command > output.log 2> error.log
```

Send both to one file:

```bash
command > combined.log 2>&1
```

Order matters:

```bash
command > combined.log 2>&1
```

means “send stdout to the file, then make stderr follow stdout”.

```bash
command 2>&1 > output.log
```

means “make stderr follow the current stdout, then redirect stdout”. Stderr usually remains on the terminal.

Bash shorthand:

```bash
command &> combined.log
command &>> combined.log
```

---

# Redirect Standard Input

```bash
command < input.txt
```

```bash
sort < unsorted.txt
mysql database_name < schema.sql
```

A here-document supplies several lines:

```bash
ssh server01 <<'REMOTE'
hostname
uptime
df -h
REMOTE
```

Quoting the delimiter prevents local expansion of `$variables` and command substitutions.

A here-string supplies one string in Bash:

```bash
grep -q root <<< "$line"
```

---

# `/dev/null`

`/dev/null` discards anything written to it and produces immediate end-of-file when read.

```bash
command > /dev/null
command 2> /dev/null
command > /dev/null 2>&1
```

Do not discard errors during troubleshooting unless they are genuinely expected.

---

# `tee`

`tee` copies standard input to both standard output and one or more files.

```bash
command | tee output.log
command | tee -a output.log
```

`sudo` applies to a command, not to shell redirection. This may fail:

```bash
sudo echo 'setting=value' > /etc/app.conf
```

Use:

```bash
printf '%s\n' 'setting=value' | sudo tee /etc/app.conf > /dev/null
```

Capture stderr too:

```bash
command 2>&1 | tee combined.log
```

---

# Command Substitution - `$(...)`

Command substitution captures standard output as text:

```bash
kernel=$(uname -r)
printf 'Kernel: %s\n' "$kernel"
```

Quote substitutions unless you deliberately need word splitting:

```bash
files=$(find . -type f)       # fragile for filenames
printf '%s\n' "$files"      # preserves embedded whitespace in the value
```

Trailing newlines are removed. Binary data and NUL bytes cannot be stored safely in shell variables.

---

# File Descriptors

You can open additional descriptors in Bash:

```bash
exec 3> audit.log
printf '%s\n' 'deployment started' >&3
exec 3>&-
```

Duplicate and restore stderr:

```bash
exec 3>&2
command 2> errors.log
printf '%s\n' 'still goes to original stderr' >&3
exec 3>&-
```

---

# Exit Status and Pipelines

By default, a Bash pipeline returns the exit status of its final command:

```bash
false | true
echo "$?"       # 0
```

For scripts, consider:

```bash
set -o pipefail
```

Then the pipeline fails if any component fails. `${PIPESTATUS[@]}` contains the statuses of all commands in the most recent Bash pipeline.

---

# Useful Patterns

Save and inspect API output:

```bash
curl -fsS https://api.example.com/health | tee health.json | jq .
```

Log a script with errors included:

```bash
./deploy.sh > deploy.log 2>&1
```

Append a timestamped status:

```bash
printf '%s %s\n' "$(date --iso-8601=seconds)" "healthy" >> health.log
```

Read a file line by line without losing backslashes:

```bash
while IFS= read -r line; do
    printf '%s\n' "$line"
done < input.txt
```

---

# Quick Reference

```bash
a | b                    # stdout from a becomes stdin for b
cmd > file               # overwrite stdout destination
cmd >> file              # append stdout
cmd 2> file              # redirect stderr
cmd > file 2>&1          # combine stdout and stderr
cmd < file               # read stdin from file
cmd | tee file           # display and save
cmd > /dev/null 2>&1     # discard both streams
value=$(command)          # capture stdout
```
