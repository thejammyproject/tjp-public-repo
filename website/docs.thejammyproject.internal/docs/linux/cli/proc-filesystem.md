# Linux `/proc` Filesystem Guide

`/proc` is a virtual filesystem exposing live process and kernel information. Most files are generated on access and do not occupy ordinary disk space.

---

# Process Directories

Each process has `/proc/PID`:

```bash
ls /proc/1234
cat /proc/1234/status
tr '\0' ' ' < /proc/1234/cmdline
readlink -f /proc/1234/exe
readlink -f /proc/1234/cwd
ls -l /proc/1234/fd
```

Useful entries:

```text
cmdline      NUL-separated command arguments
environ      NUL-separated environment
status       readable identity, state, memory, and capability summary
stat         machine-oriented process statistics
maps         virtual memory mappings
fd/          open file descriptors
exe          executable symlink
cwd          working-directory symlink
root         process root-directory symlink
cgroup       cgroup membership
limits       resource limits
mountinfo    mounts visible in the process namespace
```

Permissions and kernel security settings restrict access to other users' process information.

---

# Safe Display of NUL-Separated Data

```bash
tr '\0' ' ' < /proc/1234/cmdline
tr '\0' '\n' < /proc/1234/environ
```

Environment variables may contain credentials. Do not collect or publish them casually.

Process entries can disappear between listing and reading because processes exit; scripts must tolerate this race.

---

# CPU and Load

```bash
cat /proc/cpuinfo
cat /proc/loadavg
cat /proc/uptime
cat /proc/stat
```

`/proc/cpuinfo` can be verbose and virtualised environments may expose host-like details. Prefer `lscpu` and `nproc` for convenient summaries.

`/proc/loadavg` contains 1/5/15-minute load, runnable/total tasks, and the latest PID.

---

# Memory

```bash
cat /proc/meminfo
grep -E 'MemTotal|MemAvailable|SwapTotal|SwapFree' /proc/meminfo
cat /proc/1234/smaps_rollup
```

Tools such as `free`, `ps`, and `pmap` derive much of their information from `/proc`.

---

# Networking

```bash
ls /proc/net
cat /proc/net/dev
cat /proc/net/route
```

Prefer `ip`, `ss`, and `nstat` for decoded output. `/proc/net` is namespace-aware and may be a link to `/proc/self/net`.

---

# Kernel Settings

Runtime tunables appear under `/proc/sys` and can be managed with `sysctl`:

```bash
sysctl net.ipv4.ip_forward
sysctl vm.swappiness
sudo sysctl -w net.ipv4.ip_forward=1
```

Persistent settings belong in a suitable file under `/etc/sysctl.d/` and are loaded with the system's sysctl service.

Writing incorrect values can disrupt or weaken a system. Check documentation and current state before changing tunables.

---

# Special Links

```text
/proc/self       current process
/proc/thread-self current thread
/proc/$$         current shell in Bash
```

Examples:

```bash
cat /proc/self/status
ls -l /proc/$$/fd
```

---

# Infrastructure Examples

Find a process's parent and namespace IDs:

```bash
grep -E '^(Name|Pid|PPid|Uid|Gid|NSpid):' /proc/1234/status
```

Find its cgroup:

```bash
cat /proc/1234/cgroup
```

Inspect resource limits:

```bash
cat /proc/1234/limits
```

See deleted open files:

```bash
ls -l /proc/1234/fd | grep ' (deleted)$'
```

Use normal tools first for readability; use `/proc` when you need the underlying kernel view or are working in a minimal environment.
