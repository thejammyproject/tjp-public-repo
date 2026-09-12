# Linux Memory Guide

Linux uses otherwise idle RAM for caches. High memory usage is not automatically a problem; available memory, swap activity, and workload behaviour matter more than the “free” number alone.

---

# Start with `free`

```bash
free -h
free -h -w
```

Important columns:

```text
total       installed usable memory
used        memory not counted as free, buffers, or cache
free        completely unused memory
buff/cache  kernel buffers and filesystem cache
available   estimate available to new applications without swapping
```

Focus on `available`, not just `free`.

---

# RSS and VSZ

```bash
ps -eo pid,user,rss,vsz,%mem,comm --sort=-rss | head
```

```text
RSS   resident set size: pages currently resident in RAM
VSZ   virtual address space: mappings, reserved space, libraries, files
```

VSZ is not the amount of physical RAM consumed. RSS can double-count shared pages across processes.

For a process:

```bash
grep -E 'VmPeak|VmSize|VmRSS|VmSwap|Threads' /proc/1234/status
pmap -x 1234 | tail -n 1
```

For proportional accounting, use `smem` if installed; PSS divides shared memory among processes.

---

# `/proc/meminfo`

```bash
cat /proc/meminfo
grep -E 'MemTotal|MemAvailable|Cached|SwapTotal|SwapFree|Dirty|Slab' /proc/meminfo
```

Useful fields include:

```text
MemAvailable  estimated memory available without swapping
Cached        filesystem page cache
Buffers       block-device metadata buffers
Slab          kernel object caches
Dirty         memory waiting to be written to storage
SwapCached    swapped pages also still present in RAM
```

---

# Swap

```bash
swapon --show
free -h
vmstat 1
```

In `vmstat`, sustained non-zero `si` and `so` mean active swap-in and swap-out. Some swap usage by itself does not prove current memory pressure.

Inspect per-process swap:

```bash
for status in /proc/[0-9]*/status; do
    awk '/^(Name|Pid|VmSwap):/ {printf "%s ", $2} END {print ""}' "$status" 2>/dev/null
done | sort -k3 -nr | head
```

---

# Page Cache

The kernel caches recently accessed files in RAM and reclaims those pages when applications need memory. This improves performance.

Do not routinely clear caches on production systems. Commands that write to `/proc/sys/vm/drop_caches` can create severe I/O spikes and usually hide rather than solve a problem.

---

# OOM Killer

When the kernel cannot satisfy memory allocations, it may invoke the out-of-memory killer.

```bash
journalctl -k -b | grep -iE 'out of memory|oom-kill|killed process'
dmesg -T | grep -iE 'out of memory|oom-kill|killed process'
```

Inspect a process's score:

```bash
cat /proc/1234/oom_score
cat /proc/1234/oom_score_adj
```

In containers and `systemd` units, a cgroup memory limit can cause an OOM kill even when the host has available RAM:

```bash
systemctl show app.service -p MemoryCurrent -p MemoryMax
systemctl status app.service
```

---

# Troubleshooting Flow

```bash
free -h
vmstat 1 10
ps -eo pid,user,rss,vsz,%mem,etime,cmd --sort=-rss | head -20
swapon --show
journalctl -k -b | grep -iE 'oom|memory|swap'
```

Ask:

- Is `MemAvailable` consistently low?
- Is the system actively swapping?
- Is one process growing over time?
- Is page cache being mistaken for application use?
- Is a cgroup or container limit involved?
- Did the kernel kill anything?

Repeated snapshots or metrics are more useful than a single reading.
