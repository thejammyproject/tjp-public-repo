# Linux `sed` Guide

`sed` stands for **Stream Editor**.

It is used to read text line-by-line, modify it, filter it, or transform it.

Common uses include:

- Finding and replacing text
- Deleting lines
- Printing specific lines
- Editing configuration files
- Removing or replacing patterns
- Adding text before or after lines
- Processing command output
- Automating text changes in scripts

---

# Basic Syntax

```bash
sed [OPTIONS] 'COMMAND' FILE
```

Example:

```bash
sed 's/hello/world/' file.txt
```

This replaces the **first occurrence** of `hello` with `world` on each line.

Important:

By default, `sed` **does not modify the original file**.

It prints the modified result to standard output.

---

# Example File

Many examples below assume we have:

```text
alice server01 active
bob server02 inactive
charlie server03 active
david server04 inactive
```

Stored in:

```bash
users.txt
```

---

# Substitute Text - `s`

The most common `sed` command is:

```bash
s
```

It means **substitute**.

Syntax:

```bash
sed 's/OLD/NEW/' file
```

Example:

```bash
sed 's/inactive/disabled/' users.txt
```

Output:

```text
alice server01 active
bob server02 disabled
charlie server03 active
david server04 disabled
```

---

# Replace All Occurrences on Each Line - `g`

By default, `sed` only replaces the **first matching occurrence on each line**.

Example:

```bash
echo "linux linux linux" | sed 's/linux/ubuntu/'
```

Output:

```text
ubuntu linux linux
```

Use the `g` flag to replace every occurrence:

```bash
echo "linux linux linux" | sed 's/linux/ubuntu/g'
```

Output:

```text
ubuntu ubuntu ubuntu
```

`g` means:

```text
global
```

---

# Case-Insensitive Replacement - `I`

GNU `sed` supports the `I` flag for case-insensitive matching.

```bash
echo "Linux linux LINUX" | sed 's/linux/ubuntu/gI'
```

Output:

```text
ubuntu ubuntu ubuntu
```

---

# Replace Only a Specific Occurrence

You can specify which match on a line should be replaced.

Example:

```bash
echo "linux linux linux" | sed 's/linux/ubuntu/2'
```

Output:

```text
linux ubuntu linux
```

This replaces only the **second occurrence**.

---

# Use Different Delimiters

The `/` character is normally used as the separator:

```bash
sed 's/old/new/'
```

But another character can be used.

This is especially useful with paths.

Instead of:

```bash
sed 's/\/var\/www\/html/\/srv\/website/'
```

Use:

```bash
sed 's#/var/www/html#/srv/website#'
```

Or:

```bash
sed 's|/var/www/html|/srv/website|'
```

This makes commands involving paths much easier to read.

---

# Modify a File In Place - `-i`

Normally:

```bash
sed 's/old/new/g' file.txt
```

does not change `file.txt`.

To modify the actual file:

```bash
sed -i 's/old/new/g' file.txt
```

## Important

Be careful with:

```bash
-i
```

because it changes the file directly.

---

# Create a Backup Before Editing

You can make `sed` create a backup:

```bash
sed -i.bak 's/old/new/g' file.txt
```

You will then have:

```text
file.txt
file.txt.bak
```

This is useful when modifying configuration files.

---

# Print Lines - `p`

The `p` command means:

```text
print
```

Example:

```bash
sed -n '3p' users.txt
```

Prints only line 3.

Output:

```text
charlie server03 active
```

The `-n` option stops `sed` from automatically printing every line.

Without `-n`:

```bash
sed '3p' users.txt
```

line 3 would appear twice because:

1. `sed` automatically prints the line
2. `p` prints it again

---

# Print a Range of Lines

Print lines 2 through 4:

```bash
sed -n '2,4p' file.txt
```

---

# Print the First Line

```bash
sed -n '1p' file.txt
```

---

# Print the Last Line

```bash
sed -n '$p' file.txt
```

`$` means:

```text
last line
```

---

# Print Lines Matching a Pattern

```bash
sed -n '/active/p' users.txt
```

This prints lines containing `active`.

Be careful here because:

```text
inactive
```

also contains the text:

```text
active
```

A more specific pattern may therefore be required.

For example:

```bash
sed -n '/ active$/p' users.txt
```

`$` means the pattern must occur at the **end of the line**.

---

# Delete Lines - `d`

The `d` command means:

```text
delete
```

Delete line 2:

```bash
sed '2d' file.txt
```

---

# Delete a Range of Lines

```bash
sed '2,4d' file.txt
```

Deletes lines 2 through 4.

---

# Delete the First Line

```bash
sed '1d' file.txt
```

---

# Delete the Last Line

```bash
sed '$d' file.txt
```

---

# Delete Lines Matching Text

```bash
sed '/inactive/d' users.txt
```

Deletes every line containing:

```text
inactive
```

---

# Delete Blank Lines

```bash
sed '/^$/d' file.txt
```

Where:

```text
^ = beginning of line
$ = end of line
```

Therefore:

```regex
^$
```

means there is nothing between the beginning and end of the line.

---

# Delete Blank Lines Including Whitespace

A line might look empty but contain spaces or tabs.

Use:

```bash
sed '/^[[:space:]]*$/d' file.txt
```

---

# Replace Text Only on a Specific Line

Replace `inactive` with `disabled` only on line 2:

```bash
sed '2s/inactive/disabled/' users.txt
```

---

# Replace Text Within a Range of Lines

```bash
sed '2,4s/inactive/disabled/g' users.txt
```

Only lines 2 through 4 are affected.

---

# Replace Text Only on Matching Lines

Example:

```bash
sed '/bob/s/inactive/disabled/' users.txt
```

Meaning:

> On lines containing `bob`, replace `inactive` with `disabled`.

---

# Append Text After a Line - `a`

The `a` command means:

```text
append
```

Example:

```bash
sed '2a New line added here' file.txt
```

This adds text **after line 2**.

---

# Append Text After Matching Text

```bash
sed '/server02/a This server requires maintenance' users.txt
```

The new line appears immediately after the matching line.

---

# Insert Text Before a Line - `i`

The `i` command means:

```text
insert
```

Example:

```bash
sed '2i New line before line 2' file.txt
```

---

# Insert Text Before Matching Text

```bash
sed '/server02/i WARNING:' users.txt
```

---

# Replace an Entire Line - `c`

The `c` command means:

```text
change
```

Example:

```bash
sed '2c bob server02 maintenance' users.txt
```

This replaces the entire second line.

---

# Replace an Entire Matching Line

```bash
sed '/server02/c bob server02 maintenance' users.txt
```

---

# Show Line Numbers - `=`

```bash
sed '=' file.txt
```

Example output:

```text
1
alice server01 active
2
bob server02 inactive
3
charlie server03 active
```

A more convenient way to display numbered lines is often:

```bash
nl -ba file.txt
```

---

# Multiple `sed` Commands

You can use `-e` to execute multiple commands.

```bash
sed \
  -e 's/inactive/disabled/g' \
  -e 's/server/machine/g' \
  users.txt
```

---

# Separate Commands With `;`

Small commands can also be combined:

```bash
sed 's/inactive/disabled/g; s/server/machine/g' users.txt
```

---

# Use a sed Script File - `-f`

For lots of commands, create a file such as:

```text
changes.sed
```

Containing:

```sed
s/inactive/disabled/g
s/server/machine/g
```

Then run:

```bash
sed -f changes.sed users.txt
```

---

# Regular Expressions

`sed` becomes much more powerful when combined with regular expressions.

Some common regex characters are:

| Pattern | Meaning |
|---|---|
| `^` | Beginning of line |
| `$` | End of line |
| `.` | Any single character |
| `*` | Zero or more of previous pattern |
| `[abc]` | One of the characters a, b or c |
| `[^abc]` | Anything except a, b or c |
| `[0-9]` | Any digit |
| `[a-z]` | Lowercase letters |
| `[A-Z]` | Uppercase letters |
| `[[:space:]]` | Whitespace |
| `[[:digit:]]` | Digit |
| `[[:alpha:]]` | Letter |
| `[[:alnum:]]` | Letter or number |

---

# Beginning of a Line - `^`

Example file:

```text
server01
test-server
server02
```

Command:

```bash
sed -n '/^server/p' file.txt
```

Matches lines beginning with:

```text
server
```

---

# End of a Line - `$`

```bash
sed -n '/active$/p' users.txt
```

Matches lines ending with:

```text
active
```

---

# Remove Leading Spaces

```bash
sed 's/^[[:space:]]*//' file.txt
```

---

# Remove Trailing Spaces

```bash
sed 's/[[:space:]]*$//' file.txt
```

---

# Remove Leading and Trailing Spaces

```bash
sed 's/^[[:space:]]*//;s/[[:space:]]*$//' file.txt
```

---

# Extended Regular Expressions - `-E`

Use:

```bash
sed -E
```

to enable extended regular expressions.

Example:

```bash
echo "server123" | sed -E 's/[0-9]+/NUMBER/'
```

Output:

```text
serverNUMBER
```

`+` means:

```text
one or more
```

---

# Capture Groups

Capture groups allow part of a pattern to be remembered and reused.

Example:

```bash
echo "Jammy Shaw" | sed -E 's/(Jammy) (Shaw)/\2, \1/'
```

Output:

```text
Shaw, Jammy
```

Where:

```text
\1 = first capture group
\2 = second capture group
```

---

# Use `&` to Reference the Entire Match

`&` represents whatever text was matched.

Example:

```bash
echo "server01" | sed 's/server01/[&]/'
```

Output:

```text
[server01]
```

Another example:

```bash
echo "ERROR connection failed" | sed 's/ERROR/[&]/'
```

Output:

```text
[ERROR] connection failed
```

---

# Remove Comments

For a file containing:

```text
server=web01
# this is a comment
port=443
# another comment
```

Remove comment lines:

```bash
sed '/^#/d' file.txt
```

---

# Remove Comments and Blank Lines

```bash
sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d' file.txt
```

Useful when reading configuration files.

---

# Remove Everything After a Character

Example:

```text
server01 # production web server
```

Remove everything from `#` onwards:

```bash
sed 's/#.*//' file.txt
```

Result:

```text
server01
```

---

# Replace Configuration Values

Suppose:

```text
PORT=8080
```

Replace it with:

```text
PORT=443
```

Using:

```bash
sed 's/^PORT=.*/PORT=443/' config.env
```

To edit the file:

```bash
sed -i 's/^PORT=.*/PORT=443/' config.env
```

This pattern is useful in automation.

---

# Change an nginx Configuration Value

Example:

```nginx
listen 80;
```

Change it to:

```nginx
listen 8080;
```

Using:

```bash
sed -i 's/listen 80;/listen 8080;/' nginx.conf
```

A more precise version:

```bash
sed -i 's/^[[:space:]]*listen 80;/    listen 8080;/' nginx.conf
```

---

# Use sed With Pipes

`sed` does not require a file.

It can process output from another command.

Example:

```bash
ip addr | sed -n '/inet /p'
```

Or:

```bash
systemctl list-units | sed -n '/nginx/p'
```

Or:

```bash
ps aux | sed -n '/nginx/p'
```

Although for searching output, `grep` is usually simpler:

```bash
ps aux | grep nginx
```

---

# Use Shell Variables With sed

Single quotes prevent shell variables from expanding.

For example:

```bash
name="Jammy"

echo "USER_NAME" | sed "s/USER_NAME/$name/"
```

Output:

```text
Jammy
```

Notice that `" "` double quotes are being used.

This:

```bash
sed 's/USER_NAME/$name/'
```

would literally insert:

```text
$name
```

rather than the value of the variable.

---

# Quit Early - `q`

`q` tells `sed` to stop processing.

Print the first 10 lines:

```bash
sed '10q' file.txt
```

This is similar to:

```bash
head -n 10 file.txt
```

---

# `q` vs `Q`

GNU `sed` supports both:

```text
q
Q
```

`q` quits after normal processing of the current line.

`Q` quits immediately without printing the current pattern space.

`Q` is mainly useful in more advanced `sed` scripts.

---

# Transliterate Characters - `y`

The `y` command replaces characters individually.

Example:

```bash
echo "hello" | sed 'y/abcdefghijklmnopqrstuvwxyz/ABCDEFGHIJKLMNOPQRSTUVWXYZ/'
```

Output:

```text
HELLO
```

For simply changing case, commands such as:

```bash
tr
```

are often easier.

Example:

```bash
echo "hello" | tr '[:lower:]' '[:upper:]'
```

---

# Reading Another File - `r`

The `r` command reads another file and inserts its contents.

Example:

```bash
sed '2r additional.txt' file.txt
```

The contents of:

```text
additional.txt
```

are inserted after line 2.

---

# Write Matching Lines to Another File - `w`

```bash
sed -n '/ERROR/w errors.txt' application.log
```

Matching lines are written to:

```text
errors.txt
```

---

# Next Line - `n`

`n` moves to the next input line.

Example:

```bash
sed -n 'n;p' file.txt
```

This can be used to print every second line.

`n` is more commonly encountered in advanced `sed` scripts.

---

# Pattern Space and Hold Space

Understanding these is useful when learning advanced `sed`.

## Pattern Space

The **pattern space** is `sed`'s main working area.

For each line:

```text
file
  ↓
sed reads line
  ↓
pattern space
  ↓
sed command runs
  ↓
output
```

Most normal commands such as:

```text
s
d
p
```

operate on the pattern space.

## Hold Space

`sed` also has another temporary storage area called the:

```text
hold space
```

It allows text to be saved and reused later.

This is mostly required for complex multi-line processing.

---

# Hold Space Commands

| Command | Meaning |
|---|---|
| `h` | Copy pattern space into hold space |
| `H` | Append pattern space to hold space |
| `g` | Copy hold space into pattern space |
| `G` | Append hold space to pattern space |
| `x` | Exchange pattern space and hold space |

These are advanced commands and aren't required for most normal administration tasks.

---

# Multi-Line Commands

`sed` normally processes one line at a time.

There are commands that allow multiple lines to be processed.

| Command | Meaning |
|---|---|
| `n` | Read next line |
| `N` | Append next line to pattern space |
| `p` | Print pattern space |
| `P` | Print up to first newline |
| `d` | Delete pattern space |
| `D` | Delete up to first newline and restart |

Example:

```bash
sed 'N;s/\n/ /' file.txt
```

This joins pairs of lines together.

---

# Branching

Advanced `sed` scripts can use branches.

## `b`

Unconditional branch.

## `t`

Branch if a previous substitution succeeded.

## `T`

Branch if a previous substitution failed.

Example:

```bash
sed ':again; s/  / /g; t again' file.txt
```

This repeatedly replaces double spaces with single spaces until none remain.

---

# Labels - `:`

Labels are used with branching.

Example:

```sed
:start
```

A branch can jump to it:

```sed
b start
```

This is generally only needed in advanced `sed` scripts.

---

# Useful sed Options

| Option | Meaning |
|---|---|
| `-n` | Disable automatic output |
| `-i` | Modify file in place |
| `-i.bak` | Modify file and create backup |
| `-E` | Use extended regular expressions |
| `-e` | Supply another sed command |
| `-f` | Read sed commands from a file |
| `-z` | Treat NUL instead of newline as line separator |
| `--debug` | Show how GNU sed processes the script |

---

# Important sed Commands

| Command | Meaning |
|---|---|
| `s` | Substitute text |
| `p` | Print |
| `d` | Delete |
| `a` | Append text |
| `i` | Insert text |
| `c` | Change entire line |
| `q` | Quit |
| `Q` | Quit immediately |
| `=` | Print line number |
| `y` | Transliterate characters |
| `r` | Read another file |
| `w` | Write to another file |
| `n` | Read next line |
| `N` | Append next line |
| `P` | Print first part of pattern space |
| `D` | Delete first part of pattern space |
| `h` | Copy pattern space to hold space |
| `H` | Append pattern space to hold space |
| `g` | Copy hold space to pattern space |
| `G` | Append hold space to pattern space |
| `x` | Exchange pattern and hold spaces |
| `b` | Branch |
| `t` | Branch after successful substitution |
| `T` | Branch after failed substitution |

---

# Addressing

A command can be restricted to particular lines.

## Specific line

```bash
sed '5d' file.txt
```

Delete line 5.

## Range

```bash
sed '5,10d' file.txt
```

Delete lines 5 through 10.

## Last line

```bash
sed '$d' file.txt
```

Delete the last line.

## Pattern

```bash
sed '/ERROR/d' file.txt
```

Delete lines containing `ERROR`.

## Between Two Patterns

```bash
sed '/START/,/END/d' file.txt
```

Deletes everything beginning with the first line matching:

```text
START
```

through the line matching:

```text
END
```

---

# Negating an Address - `!`

`!` means:

> run the command on lines that DO NOT match.

Example:

```bash
sed '/ERROR/!d' logfile
```

Delete every line that does **not** contain `ERROR`.

Effectively, only ERROR lines remain.

Equivalent to something like:

```bash
grep ERROR logfile
```

---

# Practical Linux Administration Examples

## Change SSH port

```bash
sudo sed -i 's/^#Port 22/Port 2222/' /etc/ssh/sshd_config
```

Always inspect configuration files before doing this because the exact existing line may differ.

---

## Change a hostname in a config

```bash
sed -i 's/old-server/new-server/g' config.conf
```

---

## Find only ERROR log entries

```bash
sed -n '/ERROR/p' application.log
```

---

## Remove DEBUG log entries

```bash
sed '/DEBUG/d' application.log
```

---

## Remove comments from a config file

```bash
sed '/^[[:space:]]*#/d' config.conf
```

---

## Remove comments and blank lines

```bash
sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d' config.conf
```

This is useful for viewing the actual active configuration:

```bash
sed '/^[[:space:]]*#/d; /^[[:space:]]*$/d' /etc/ssh/sshd_config
```

---

# sed vs grep

A useful way to remember them:

## grep

Mainly used to:

```text
SEARCH
```

Example:

```bash
grep "ERROR" application.log
```

## sed

Mainly used to:

```text
SEARCH + MODIFY
```

Example:

```bash
sed 's/ERROR/WARNING/g' application.log
```

---

# sed vs awk

A rough rule:

```text
grep = find lines
sed  = modify lines
awk  = process fields/columns
```

Example data:

```text
jammy 192.168.1.10 active
bob   192.168.1.11 inactive
```

`grep`:

```bash
grep active users.txt
```

Find matching lines.

`sed`:

```bash
sed 's/inactive/disabled/' users.txt
```

Modify text.

`awk`:

```bash
awk '{print $1, $2}' users.txt
```

Process columns.

These tools often overlap and can be combined.

---

# Useful sed Cheat Sheet

```bash
# Replace first occurrence on each line
sed 's/old/new/' file

# Replace every occurrence
sed 's/old/new/g' file

# Case-insensitive replacement
sed 's/old/new/gI' file

# Modify file
sed -i 's/old/new/g' file

# Modify file and create backup
sed -i.bak 's/old/new/g' file

# Print line 5
sed -n '5p' file

# Print lines 5-10
sed -n '5,10p' file

# Print last line
sed -n '$p' file

# Print matching lines
sed -n '/ERROR/p' file

# Delete line 5
sed '5d' file

# Delete lines 5-10
sed '5,10d' file

# Delete matching lines
sed '/ERROR/d' file

# Delete blank lines
sed '/^$/d' file

# Delete whitespace-only lines
sed '/^[[:space:]]*$/d' file

# Insert before line 3
sed '3i New text' file

# Append after line 3
sed '3a New text' file

# Replace entire line 3
sed '3c Replacement line' file

# Replace only on line 3
sed '3s/old/new/' file

# Replace only on matching lines
sed '/server01/s/old/new/' file

# Remove leading whitespace
sed 's/^[[:space:]]*//' file

# Remove trailing whitespace
sed 's/[[:space:]]*$//' file

# Remove comments
sed '/^[[:space:]]*#/d' file

# Remove comments and blank lines
sed '/^[[:space:]]*#/d;/^[[:space:]]*$/d' file

# Use extended regex
sed -E 's/[0-9]+/NUMBER/g' file

# Multiple commands
sed -e 's/foo/bar/g' -e 's/test/prod/g' file
```

---

# Safe Way to Learn sed

Create a test file:

```bash
cat > sed-test.txt <<'EOF'
server01 active
server02 inactive
server03 active
server04 inactive
EOF
```

Then practise without `-i`:

```bash
sed 's/inactive/disabled/g' sed-test.txt
```

Because `-i` was not used, the original file remains unchanged.

Check:

```bash
cat sed-test.txt
```

Once the command produces the result you expect, you can use:

```bash
sed -i.bak 's/inactive/disabled/g' sed-test.txt
```

This changes the file while keeping a backup.

---

# Useful Learning Rule

When learning `sed`, start with these five concepts:

```text
s = substitute
p = print
d = delete
i = insert
a = append
```

Then learn addressing:

```text
2        = line 2
2,5      = lines 2 through 5
$        = last line
/pattern/ = matching line
```

Then combine them.

Examples:

```bash
sed '2d' file
```

> Delete line 2.

```bash
sed '/ERROR/d' file
```

> Delete lines containing ERROR.

```bash
sed '3s/foo/bar/' file
```

> Replace foo with bar on line 3.

```bash
sed '/server01/s/active/maintenance/' file
```

> Find the line containing server01 and change active to maintenance.

This combination of **address + command** is one of the most important concepts to understand in `sed`.