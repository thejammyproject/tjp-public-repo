# Linux Processes Guide

A process is a running instance of a program. Linux identifies each process with a process ID (`PID`).

---

# Core Concepts

```text
PID     process ID
PPID    parent process ID
UID     user that owns the process
TTY     controlling terminal
STAT    process state and flags
CMD     command
```

Processes form a parent-child tree. Inspect it with:

```bash
pstree -p
ps -ef --forest
```

PID 1 is the first userspace process and adopts orphaned processes. On most modern distributions it is `systemd`.

---

# Inspect Processes with `ps`

Common views:

```bash
ps
ps -ef
ps aux
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,cmd
```

The BSD-style `aux` and Unix-style `-ef` formats differ, but both show all processes.

Sort by CPU or memory:

```bash
ps -eo pid,user,%cpu,%mem,cmd --sort=-%cpu | head
ps -eo pid,user,rss,vsz,cmd --sort=-rss | head
```

Inspect one process:

```bash
ps -p 1234 -o pid,ppid,user,stat,lstart,etime,args
```

---

# Find Processes

```bash
pgrep nginx
pgrep -a nginx
pgrep -u www-data -a
pgrep -P 1234 -a
pidof nginx
```

`pgrep` matches process names and can include arguments with `-f`:

```bash
pgrep -af 'python.*worker'
```

Be careful with `-f`; broad patterns can match unexpected commands.

---

# Live Monitoring

```bash
top
top -p 1234
htop
```

Useful `top` keys:

```text
P    sort by CPU
M    sort by memory
1    show individual CPUs
H    show threads
k    send a signal
q    quit
```

Other useful tools:

```bash
watch -n 2 'ps -eo pid,%cpu,%mem,cmd --sort=-%cpu | head'
pidstat -p 1234 1
```

---

# Foreground and Background Jobs

Start a job in the background:

```bash
long-command &
```

Manage jobs created by the current shell:

```bash
jobs -l
fg %1
bg %1
```

Press `Ctrl+Z` to suspend a foreground job, then use `bg` or `fg`. This sends `SIGTSTP`; it does not terminate the process.

Keep a process after logout:

```bash
nohup long-command > command.log 2>&1 &
disown
```

For real services, prefer a service manager such as `systemd` over `nohup`.

---

# Process States

Common first letters in `ps` state output:

```text
R    running or runnable
S    interruptible sleep
D    uninterruptible sleep, often waiting on I/O
T    stopped or traced
Z    zombie
I    idle kernel thread
```

A zombie has exited, but its parent has not collected its exit status. It consumes a PID entry, not normal process memory. Fix the parent rather than trying to kill the zombie.

An orphan is a live process whose parent exited. PID 1 or another subreaper adopts it.

Processes stuck in `D` state often cannot respond to signals until the kernel operation completes. Investigate storage, NFS, devices, or kernel logs.

---

# Threads and Open Resources

```bash
ps -L -p 1234
top -H -p 1234
ls -l /proc/1234/fd
lsof -p 1234
lsof -iTCP:8080 -sTCP:LISTEN
```

View the executable, working directory, and command line:

```bash
readlink -f /proc/1234/exe
readlink -f /proc/1234/cwd
tr '\0' ' ' < /proc/1234/cmdline
```

Permissions may restrict what one user can inspect about another user's process.

---

# Why Stopping a Service May Not Stop Everything

Possible causes include:

- A child process detached or double-forked.
- The unit's `KillMode` does not cover every process.
- Another supervisor, timer, cron job, or container restarts it.
- The process was launched manually and is outside the service cgroup.
- The unit reports stopped while an unrelated process uses the same binary.

Investigate with:

```bash
systemctl status app.service
systemctl show app.service -p MainPID -p ControlGroup -p KillMode
systemd-cgls
ps -eo pid,ppid,lstart,args --forest
journalctl -u app.service
```

---

# Quick Troubleshooting Flow

```bash
pgrep -af process-name
ps -p PID -o pid,ppid,user,stat,%cpu,%mem,etime,args
pstree -aps PID
lsof -p PID
cat /proc/PID/status
journalctl _PID=PID
```

Confirm identity and ownership before signalling or terminating anything.
