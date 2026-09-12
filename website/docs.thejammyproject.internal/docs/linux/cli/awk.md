# Linux `awk` Guide

`awk` is a text-processing tool designed for working with structured text.

It is especially useful for:

- Reading columns or fields
- Filtering lines
- Processing logs
- Extracting information
- Performing calculations
- Reformatting output
- Summarising data
- Working with command output
- Writing small text-processing programs

A useful mental model is:

```text
grep = find lines
sed  = modify lines
awk  = process fields and columns
```

---

# Basic Syntax

```bash
awk 'PATTERN { ACTION }' file
```

Example:

```bash
awk '{print $1}' users.txt
```

This prints the first field from every line.

---

# Example File

Many examples below assume:

```text
alice server01 active 25
bob server02 inactive 32
charlie server03 active 41
david server04 inactive 29
```

Stored in:

```bash
users.txt
```

By default, `awk` treats whitespace as the field separator.

So:

```text
alice server01 active 25
```

is divided into:

```text
$1 = alice
$2 = server01
$3 = active
$4 = 25
```

---

# Records and Fields

This is the most important concept in `awk`.

## Record

A record normally means:

```text
one line
```

## Field

A field normally means:

```text
one column
```

Example:

```text
alice server01 active 25
```

In `awk`:

```text
$1 = alice
$2 = server01
$3 = active
$4 = 25
```

---

# `$0`

`$0` means:

```text
the entire current line
```

Example:

```bash
awk '{print $0}' users.txt
```

Output:

```text
alice server01 active 25
bob server02 inactive 32
charlie server03 active 41
david server04 inactive 29
```

---

# `$1`, `$2`, `$3`, etc.

Print the first field:

```bash
awk '{print $1}' users.txt
```

Output:

```text
alice
bob
charlie
david
```

Print the second field:

```bash
awk '{print $2}' users.txt
```

Output:

```text
server01
server02
server03
server04
```

Print multiple fields:

```bash
awk '{print $1, $3}' users.txt
```

Output:

```text
alice active
bob inactive
charlie active
david inactive
```

---

# `$NF`

`NF` means:

```text
Number of Fields
```

Therefore:

```text
$NF
```

means:

```text
the last field
```

Example:

```bash
awk '{print $NF}' users.txt
```

Output:

```text
25
32
41
29
```

---

# Second-to-Last Field

```bash
awk '{print $(NF-1)}' file.txt
```

This prints the field before the last field.

---

# `NF`

Print how many fields each line contains:

```bash
awk '{print NF}' users.txt
```

Output:

```text
4
4
4
4
```

---

# `NR`

`NR` means:

```text
Number of Records
```

It represents the current line number.

Example:

```bash
awk '{print NR, $0}' users.txt
```

Output:

```text
1 alice server01 active 25
2 bob server02 inactive 32
3 charlie server03 active 41
4 david server04 inactive 29
```

---

# Print a Specific Line

Print line 3:

```bash
awk 'NR == 3 {print}' users.txt
```

Output:

```text
charlie server03 active 41
```

---

# Print a Range of Lines

```bash
awk 'NR >= 2 && NR <= 4 {print}' users.txt
```

Prints lines 2 through 4.

---

# Pattern Matching

Print lines containing:

```text
active
```

```bash
awk '/active/' users.txt
```

This prints the whole matching line.

Be careful because:

```text
inactive
```

also contains:

```text
active
```

So this would match both.

A more precise field comparison is:

```bash
awk '$3 == "active" {print}' users.txt
```

---

# Exact Field Matching

Print users whose third field equals:

```text
active
```

```bash
awk '$3 == "active" {print}' users.txt
```

Output:

```text
alice server01 active 25
charlie server03 active 41
```

---

# Not Equal

```bash
awk '$3 != "active" {print}' users.txt
```

Output:

```text
bob server02 inactive 32
david server04 inactive 29
```

---

# Numeric Comparisons

Print rows where field 4 is greater than 30:

```bash
awk '$4 > 30 {print}' users.txt
```

Output:

```text
bob server02 inactive 32
charlie server03 active 41
```

Other comparison operators include:

```text
==   equal
!=   not equal
>    greater than
<    less than
>=   greater than or equal
<=   less than or equal
```

---

# Logical AND - `&&`

Example:

```bash
awk '$3 == "active" && $4 > 30 {print}' users.txt
```

Meaning:

```text
status must be active
AND
field 4 must be greater than 30
```

Output:

```text
charlie server03 active 41
```

---

# Logical OR - `||`

```bash
awk '$1 == "alice" || $1 == "bob" {print}' users.txt
```

Matches either:

```text
alice
```

or:

```text
bob
```

---

# Logical NOT - `!`

Example:

```bash
awk '$3 != "inactive" {print}' users.txt
```

Another form:

```bash
awk '!/inactive/' users.txt
```

This prints lines that do not contain:

```text
inactive
```

---

# BEGIN Block

`BEGIN` runs before `awk` reads the file.

Example:

```bash
awk 'BEGIN {print "User Server Status Age"} {print}' users.txt
```

Output starts with:

```text
User Server Status Age
```

followed by the file contents.

---

# END Block

`END` runs after the file has been processed.

Example:

```bash
awk 'END {print "Finished"}' users.txt
```

---

# Count Lines

```bash
awk 'END {print NR}' users.txt
```

Output:

```text
4
```

This gives the total number of records processed.

---

# BEGIN, Main Processing and END

A complete `awk` structure can look like:

```bash
awk '
BEGIN {
    print "Starting"
}
{
    print $1
}
END {
    print "Finished"
}
' users.txt
```

---

# Field Separator - `-F`

By default, `awk` uses whitespace.

You can change the field separator.

Example CSV file:

```text
alice,server01,active,25
bob,server02,inactive,32
```

Use:

```bash
awk -F',' '{print $1}' users.csv
```

Output:

```text
alice
bob
```

---

# Colon-Separated Files

A very common Linux example is:

```text
/etc/passwd
```

Its fields are separated by:

```text
:
```

Example:

```bash
awk -F':' '{print $1}' /etc/passwd
```

This prints usernames.

---

# `/etc/passwd` Fields

A typical line looks like:

```text
jammy:x:1000:1000:Jammy:/home/jammy:/bin/bash
```

Using:

```bash
awk -F':' '{print $1, $6, $7}' /etc/passwd
```

prints:

```text
username home-directory shell
```

For example:

```text
jammy /home/jammy /bin/bash
```

---

# `FS`

`FS` means:

```text
Field Separator
```

Instead of:

```bash
awk -F':' '{print $1}' file
```

you can use:

```bash
awk 'BEGIN {FS=":"} {print $1}' file
```

Both do the same thing.

---

# Output Field Separator - `OFS`

`OFS` means:

```text
Output Field Separator
```

Example:

```bash
awk 'BEGIN {OFS=" | "} {print $1, $2, $3}' users.txt
```

Output:

```text
alice | server01 | active
bob | server02 | inactive
```

---

# Record Separator - `RS`

`RS` means:

```text
Record Separator
```

By default:

```text
RS = newline
```

So each line is treated as one record.

It can be changed for more advanced processing.

---

# Output Record Separator - `ORS`

`ORS` means:

```text
Output Record Separator
```

By default:

```text
ORS = newline
```

Example:

```bash
awk 'BEGIN {ORS=" | "} {print $1}' users.txt
```

Output:

```text
alice | bob | charlie | david |
```

---

# Print Formatted Output

`printf` gives more control than `print`.

Example:

```bash
awk '{printf "%-10s %-10s %-10s\n", $1, $2, $3}' users.txt
```

Possible output:

```text
alice      server01   active
bob        server02   inactive
charlie    server03   active
david      server04   inactive
```

---

# `print` vs `printf`

`print` automatically adds a newline:

```bash
awk '{print $1}' file
```

`printf` does not automatically add one:

```bash
awk '{printf "%s\n", $1}' file
```

With `printf`, you control formatting explicitly.

---

# Common printf Format Specifiers

```text
%s   string
%d   integer
%f   decimal number
%.2f decimal number with 2 decimal places
```

Example:

```bash
awk '{printf "%s is %d years old\n", $1, $4}' users.txt
```

---

# Variables

You can create variables inside `awk`.

Example:

```bash
awk '{name=$1; status=$3; print name, status}' users.txt
```

---

# Variables From the Shell - `-v`

Suppose:

```bash
status="active"
```

You can pass it into `awk`:

```bash
awk -v target="$status" '$3 == target {print}' users.txt
```

This is safer and clearer than trying to inject shell variables directly into the awk program.

---

# Arithmetic

`awk` can perform calculations.

Example:

```bash
awk '{print $4 * 2}' users.txt
```

---

# Addition

```bash
awk '{print $4 + 10}' users.txt
```

---

# Sum a Column

```bash
awk '{sum += $4} END {print sum}' users.txt
```

Explanation:

```text
sum += $4
```

means:

```text
sum = sum + $4
```

Output:

```text
127
```

---

# Calculate an Average

```bash
awk '{sum += $4} END {print sum / NR}' users.txt
```

---

# Minimum Value

```bash
awk 'NR == 1 {min=$4} $4 < min {min=$4} END {print min}' users.txt
```

---

# Maximum Value

```bash
awk 'NR == 1 {max=$4} $4 > max {max=$4} END {print max}' users.txt
```

---

# Increment Counters

Example:

```bash
awk '$3 == "active" {count++} END {print count}' users.txt
```

This counts active users.

Output:

```text
2
```

---

# Count Values

You can use an associative array.

Example:

```bash
awk '{count[$3]++} END {for (status in count) print status, count[status]}' users.txt
```

Output may be:

```text
active 2
inactive 2
```

---

# Associative Arrays

Unlike normal indexed arrays, `awk` arrays can use text as keys.

Example:

```awk
count["active"]
count["inactive"]
```

This makes them useful for summarising logs and categories.

---

# Arrays

Example:

```bash
awk '{users[NR]=$1} END {for (i=1; i<=NR; i++) print users[i]}' users.txt
```

---

# `for` Loop

Example:

```bash
awk 'BEGIN {
    for (i=1; i<=5; i++) {
        print i
    }
}'
```

Output:

```text
1
2
3
4
5
```

---

# `while` Loop

```bash
awk 'BEGIN {
    i=1
    while (i<=5) {
        print i
        i++
    }
}'
```

---

# `if` Statements

Example:

```bash
awk '{
    if ($4 >= 30)
        print $1, "is 30 or older"
}' users.txt
```

---

# `if` / `else`

```bash
awk '{
    if ($3 == "active")
        print $1, "OK"
    else
        print $1, "NOT ACTIVE"
}' users.txt
```

---

# Multiple Conditions

```bash
awk '{
    if ($3 == "active" && $4 > 30)
        print $1
}' users.txt
```

---

# String Matching With `~`

The `~` operator means:

```text
matches regular expression
```

Example:

```bash
awk '$1 ~ /^a/ {print}' users.txt
```

This prints names beginning with:

```text
a
```

---

# String Does Not Match - `!~`

```bash
awk '$1 !~ /^a/ {print}' users.txt
```

Prints names that do not begin with:

```text
a
```

---

# Regular Expressions

Common regular-expression patterns include:

```text
^        beginning of line
$        end of line
.        any single character
*        zero or more
+        one or more
?        zero or one
[0-9]    digit
[a-z]    lowercase letter
[A-Z]    uppercase letter
```

Example:

```bash
awk '$2 ~ /^server[0-9]+$/ {print}' users.txt
```

---

# String Functions

`awk` includes useful functions for working with strings.

---

# `length()`

Print the length of a field:

```bash
awk '{print $1, length($1)}' users.txt
```

---

# `tolower()`

Convert text to lowercase:

```bash
awk '{print tolower($1)}' users.txt
```

---

# `toupper()`

Convert text to uppercase:

```bash
awk '{print toupper($1)}' users.txt
```

---

# `substr()`

Extract part of a string.

Syntax:

```text
substr(string, start, length)
```

Example:

```bash
awk '{print substr($1, 1, 3)}' users.txt
```

For:

```text
charlie
```

this would output:

```text
cha
```

---

# `index()`

Find the position of text inside another string.

```bash
awk '{print index($2, "server")}' users.txt
```

---

# `split()`

Split a string into an array.

Example:

```bash
awk 'BEGIN {
    text="linux,aws,docker"
    split(text, arr, ",")
    print arr[1]
    print arr[2]
    print arr[3]
}'
```

Output:

```text
linux
aws
docker
```

---

# `sub()`

Replace the first match.

Example:

```bash
awk '{
    sub(/inactive/, "disabled")
    print
}' users.txt
```

---

# `gsub()`

Replace all matches.

Example:

```bash
awk '{
    gsub(/server/, "host")
    print
}' users.txt
```

---

# `sub()` vs `gsub()`

```text
sub()  = replace first match
gsub() = replace all matches
```

This is similar to `sed`.

---

# Modify a Specific Field

Example:

```bash
awk '$3 == "inactive" {$3="disabled"} {print}' users.txt
```

Output:

```text
alice server01 active 25
bob server02 disabled 32
charlie server03 active 41
david server04 disabled 29
```

Important:

This changes only awk's output.

It does not modify the original file.

---

# Writing Output to Another File

Shell redirection can be used:

```bash
awk '$3 == "active" {print}' users.txt > active-users.txt
```

---

# Append Output to Another File

```bash
awk '$3 == "active" {print}' users.txt >> active-users.txt
```

---

# awk Does Not Edit Files In Place

Unlike:

```bash
sed -i
```

standard `awk` does not normally edit a file directly.

Use:

```bash
awk '$3 == "inactive" {$3="disabled"} {print}' users.txt > users.tmp
mv users.tmp users.txt
```

For important files, create a backup first.

---

# Skip the First Line

Useful with files containing headings.

Example:

```text
NAME SERVER STATUS AGE
alice server01 active 25
bob server02 inactive 32
```

Skip the header:

```bash
awk 'NR > 1 {print}' users.txt
```

---

# Process Only the First Line

```bash
awk 'NR == 1 {print}' users.txt
```

---

# Process the Last Line

One approach:

```bash
awk '{line=$0} END {print line}' users.txt
```

---

# Stop Processing - `exit`

Example:

```bash
awk '$1 == "charlie" {print; exit}' users.txt
```

Once `charlie` is found, awk stops reading the file.

---

# `next`

`next` skips the remaining actions for the current line and moves to the next record.

Example:

```bash
awk '$3 == "inactive" {next} {print}' users.txt
```

Inactive users are skipped.

Equivalent idea:

```text
if inactive:
    skip line
else:
    print line
```

---

# Multiple Actions

```bash
awk '
$3 == "active" {
    count++
    print $1, "is active"
}
END {
    print "Total:", count
}
' users.txt
```

---

# Multiple Input Files

```bash
awk '{print}' file1.txt file2.txt
```

`awk` processes both files.

---

# `FILENAME`

Print the current file name:

```bash
awk '{print FILENAME, $0}' file1.txt file2.txt
```

---

# `FNR`

`FNR` means:

```text
File Number of Records
```

It is the line number within the current file.

Difference:

```text
NR  = line number across all files
FNR = line number within each file
```

Example:

```bash
awk '{print NR, FNR, FILENAME, $0}' file1 file2
```

---

# Common Built-In Variables

```text
$0       entire current line
$1       first field
$2       second field
$NF      last field

NR       current record number
FNR      current record number in current file
NF       number of fields
FS       input field separator
OFS      output field separator
RS       input record separator
ORS      output record separator
FILENAME current file name
```

---

# Practical Linux Administration Examples

## Show Mounted Filesystem Usage

```bash
df -h
```

Extract filesystem and usage percentage:

```bash
df -h | awk '{print $1, $5}'
```

---

# Find Filesystems Above 80%

```bash
df -P | awk 'NR > 1 {
    gsub(/%/, "", $5)
    if ($5 > 80)
        print $1, $5 "%"
}'
```

This is useful for monitoring scripts.

---

# Check Disk Usage Without Header

```bash
df -h | awk 'NR > 1 {print $1, $5, $6}'
```

---

# Show Memory Information

Using:

```bash
free -m
```

You can extract memory values:

```bash
free -m | awk '/Mem:/ {print $2, $3, $4}'
```

Where the fields represent values such as:

```text
total used free
```

depending on the command output.

---

# Calculate Memory Usage Percentage

Example:

```bash
free | awk '/Mem:/ {
    printf "Memory usage: %.2f%%\n", $3/$2 * 100
}'
```

---

# Process `ps` Output

Show PID and command:

```bash
ps aux | awk '{print $2, $11}'
```

---

# Find Processes Using More Than 10% Memory

For typical `ps aux` output:

```bash
ps aux | awk '$4 > 10 {print $2, $4, $11}'
```

Where:

```text
$2  = PID
$4  = memory percentage
$11 = command
```

---

# Find Processes Using More Than 50% CPU

```bash
ps aux | awk '$3 > 50 {print $2, $3, $11}'
```

---

# Show Listening Ports

Example:

```bash
ss -tulpn
```

You can process columns:

```bash
ss -tulpn | awk '{print $1, $5}'
```

The exact field numbers can vary depending on output, so always inspect the command first.

---

# Extract IP Addresses

Example:

```bash
ip addr
```

One approach:

```bash
ip addr | awk '/inet / {print $2}'
```

Example output:

```text
127.0.0.1/8
192.168.1.20/24
```

---

# Extract IP Without CIDR Prefix

```bash
ip addr | awk '/inet / {
    split($2, a, "/")
    print a[1]
}'
```

Output:

```text
127.0.0.1
192.168.1.20
```

---

# Get Your Main IPv4 Address

A common approach:

```bash
ip -4 addr | awk '/inet / && $2 !~ /^127/ {
    split($2, a, "/")
    print a[1]
}'
```

---

# Read `/etc/passwd`

Print usernames:

```bash
awk -F':' '{print $1}' /etc/passwd
```

---

# Show Users With Bash Shell

```bash
awk -F':' '$7 == "/bin/bash" {print $1}' /etc/passwd
```

---

# Show Usernames and Home Directories

```bash
awk -F':' '{print $1, $6}' /etc/passwd
```

---

# Find Users With UID >= 1000

```bash
awk -F':' '$3 >= 1000 {print $1, $3}' /etc/passwd
```

This is often useful when looking for normal user accounts.

Be aware that some systems also use high UIDs for service accounts.

---

# Parse Logs

Suppose a log contains:

```text
2026-09-12 INFO login successful
2026-09-12 ERROR database failed
2026-09-12 INFO logout
2026-09-12 ERROR timeout
```

Print ERROR lines:

```bash
awk '$2 == "ERROR" {print}' app.log
```

---

# Count Errors

```bash
awk '$2 == "ERROR" {count++} END {print count}' app.log
```

---

# Count Log Levels

```bash
awk '{count[$2]++}
END {
    for (level in count)
        print level, count[level]
}' app.log
```

Possible output:

```text
INFO 2
ERROR 2
```

---

# Count HTTP Status Codes

Suppose an access log has status code in field 9:

```bash
awk '{count[$9]++}
END {
    for (code in count)
        print code, count[code]
}' access.log
```

Possible output:

```text
200 2456
404 42
500 6
```

---

# Find HTTP 500 Responses

```bash
awk '$9 == 500 {print}' access.log
```

---

# Find IPs Producing Errors

For a typical web access log:

```bash
awk '$9 >= 400 {print $1}' access.log
```

---

# Count Requests Per IP

```bash
awk '{count[$1]++}
END {
    for (ip in count)
        print ip, count[ip]
}' access.log
```

---

# Sort awk Results

`awk` works extremely well with other Linux commands.

Example:

```bash
awk '{print $1}' access.log | sort
```

---

# Count Unique Values

```bash
awk '{print $1}' access.log | sort | uniq -c
```

---

# Sort by Count

```bash
awk '{print $1}' access.log |
sort |
uniq -c |
sort -nr
```

This is useful for finding the most common IP addresses.

---

# Top 10 IP Addresses

```bash
awk '{print $1}' access.log |
sort |
uniq -c |
sort -nr |
head -10
```

---

# Process CSV Files

Example:

```text
name,server,status,cpu
alice,server01,active,25
bob,server02,inactive,32
```

Print name and CPU:

```bash
awk -F',' '{print $1, $4}' servers.csv
```

---

# Skip CSV Header

```bash
awk -F',' 'NR > 1 {print $1, $4}' servers.csv
```

---

# Filter CSV Data

```bash
awk -F',' 'NR > 1 && $3 == "active" {print $1}' servers.csv
```

---

# Sum CSV Column

```bash
awk -F',' 'NR > 1 {sum += $4} END {print sum}' servers.csv
```

---

# Calculate CSV Average

```bash
awk -F',' '
NR > 1 {
    sum += $4
    count++
}
END {
    print sum / count
}
' servers.csv
```

---

# Useful One-Liners

Print first column:

```bash
awk '{print $1}' file
```

Print first and third columns:

```bash
awk '{print $1, $3}' file
```

Print last column:

```bash
awk '{print $NF}' file
```

Print line numbers:

```bash
awk '{print NR, $0}' file
```

Print line 5:

```bash
awk 'NR == 5' file
```

Print lines 5 through 10:

```bash
awk 'NR >= 5 && NR <= 10' file
```

Print matching lines:

```bash
awk '/ERROR/' logfile
```

Print non-matching lines:

```bash
awk '!/ERROR/' logfile
```

Print field 3 when it equals active:

```bash
awk '$3 == "active" {print $1}' file
```

Count lines:

```bash
awk 'END {print NR}' file
```

Count matching lines:

```bash
awk '/ERROR/ {count++} END {print count}' logfile
```

Sum column 4:

```bash
awk '{sum += $4} END {print sum}' file
```

Average column 4:

```bash
awk '{sum += $4} END {print sum / NR}' file
```

Use comma separator:

```bash
awk -F',' '{print $1}' file.csv
```

Use colon separator:

```bash
awk -F':' '{print $1}' /etc/passwd
```

---

# awk vs grep

Use `grep` mainly when you want to:

```text
find lines
```

Example:

```bash
grep ERROR app.log
```

Use `awk` when you want to:

```text
find lines
AND
process fields
```

Example:

```bash
awk '$2 == "ERROR" {print $1, $3}' app.log
```

---

# awk vs sed

Use `sed` mainly when you want to:

```text
modify text
```

Example:

```bash
sed 's/inactive/disabled/g' users.txt
```

Use `awk` mainly when you want to:

```text
process columns
calculate values
filter structured text
```

Example:

```bash
awk '$3 == "active" {print $1, $4}' users.txt
```

---

# awk + grep + sed

These tools can be combined.

Example:

```bash
grep ERROR app.log |
awk '{print $1, $3}' |
sed 's/server/host/g'
```

But avoid chaining tools unnecessarily.

For example:

```bash
grep ERROR app.log | awk '{print $1}'
```

can often simply be written:

```bash
awk '/ERROR/ {print $1}' app.log
```

---

# Useful Learning Rule

The most important awk structure is:

```text
PATTERN { ACTION }
```

Example:

```bash
awk '$3 == "active" {print $1}' users.txt
```

Break it down:

```text
$3 == "active"
```

means:

```text
find records where field 3 equals active
```

Then:

```text
{print $1}
```

means:

```text
print field 1
```

So the full command means:

```text
Find lines where the third column is "active"
and print the first column.
```

---

# Mental Model

Think of awk processing a file like this:

```text
input line
    ↓
split into fields
    ↓
$1 $2 $3 $4 ...
    ↓
test pattern
    ↓
run action
    ↓
next line
```

Example:

```text
alice server01 active 25
```

becomes:

```text
$1     = alice
$2     = server01
$3     = active
$4     = 25
NF     = 4
NR     = current line number
$0     = entire line
```

---

# The Five Things to Learn First

Start with:

```text
$0    whole line
$1    first field
$2    second field
NF    number of fields
NR    line number
```

Then learn:

```text
PATTERN { ACTION }
```

Then:

```text
-F     input separator
OFS    output separator
```

Then filtering:

```bash
awk '$3 == "active" {print $1}' file
```

Then calculations:

```bash
awk '{sum += $4} END {print sum}' file
```

Once those make sense, most day-to-day Linux `awk` usage becomes much easier.

---

# Quick Cheat Sheet

```bash
# Print complete line
awk '{print $0}' file

# First field
awk '{print $1}' file

# First and third fields
awk '{print $1, $3}' file

# Last field
awk '{print $NF}' file

# Number of fields
awk '{print NF}' file

# Add line numbers
awk '{print NR, $0}' file

# Line 5
awk 'NR == 5' file

# Lines 5-10
awk 'NR >= 5 && NR <= 10' file

# Lines containing ERROR
awk '/ERROR/' file

# Lines not containing ERROR
awk '!/ERROR/' file

# Field 3 equals active
awk '$3 == "active"' file

# Field 4 greater than 30
awk '$4 > 30' file

# Multiple conditions
awk '$3 == "active" && $4 > 30' file

# Print matching field
awk '$3 == "active" {print $1}' file

# CSV
awk -F',' '{print $1}' file.csv

# /etc/passwd usernames
awk -F':' '{print $1}' /etc/passwd

# Count lines
awk 'END {print NR}' file

# Count matching lines
awk '/ERROR/ {count++} END {print count}' file

# Sum column
awk '{sum += $4} END {print sum}' file

# Average column
awk '{sum += $4} END {print sum / NR}' file

# Replace text in output
awk '{gsub(/old/, "new"); print}' file

# Skip first line
awk 'NR > 1' file

# Stop after finding match
awk '/ERROR/ {print; exit}' file

# Uppercase first field
awk '{print toupper($1)}' file

# Lowercase first field
awk '{print tolower($1)}' file
```

---

# Safe Practice File

Create a test file:

```bash
cat > awk-test.txt <<'EOF'
alice server01 active 25
bob server02 inactive 32
charlie server03 active 41
david server04 inactive 29
EOF
```

Try:

```bash
awk '{print $1}' awk-test.txt
```

Then:

```bash
awk '$3 == "active" {print $1}' awk-test.txt
```

Then:

```bash
awk '$4 > 30 {print $1, $4}' awk-test.txt
```

Then:

```bash
awk '{sum += $4} END {print sum}' awk-test.txt
```

Then:

```bash
awk '{
    if ($3 == "active")
        print $1, "is available"
    else
        print $1, "is unavailable"
}' awk-test.txt
```

These examples cover most of the core awk concepts you are likely to use regularly as a Linux, cloud or infrastructure engineer.