# Linux CPU and Load Guide

CPU utilisation and load average describe different things.

```text
CPU utilisation = time CPUs spend doing categories of work
load average     = runnable tasks plus tasks in uninterruptible sleep
```

---

# CPU Utilisation

```bash
top
mpstat -P ALL 1
pidstat 1
```

Common CPU categories:

```text
us   user-space work
sy   kernel work
id   idle
wa   waiting for I/O
st   time taken by the hypervisor from a virtual machine
hi   hardware interrupt handling
si   software interrupt handling
```

High `wa` points toward storage or network-filesystem waits. High `st` can indicate host contention in a VM.

---

# Load Average

```bash
uptime
cat /proc/loadavg
```

The three values are exponentially damped averages over roughly 1, 5, and 15 minutes.

Interpret load relative to logical CPUs:

```bash
nproc
lscpu
```

On an 8-CPU host, load near 8 means roughly one runnable or uninterruptibly waiting task per CPU on average. It does not mean 8% or 800% CPU usage.

Load can be high while CPUs are partly idle when many tasks are blocked in uninterruptible I/O sleep.

---

# Find CPU-Heavy Processes

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,cmd --sort=-%cpu | head
top -o %CPU
pidstat -u 1
```

In `ps`, `%CPU` is commonly averaged over process lifetime. In `top`, it represents a recent interval. Values can exceed 100% for multithreaded processes depending on display mode.

Inspect threads:

```bash
top -H -p 1234
ps -L -p 1234 -o pid,tid,psr,stat,%cpu,comm
```

---

# Find I/O Wait and Blocked Tasks

```bash
vmstat 1
iostat -xz 1
ps -eo state,pid,ppid,wchan:32,cmd | awk '$1 ~ /^D/'
journalctl -k -b
```

`vmstat` fields worth watching:

```text
r    runnable processes
b    processes blocked on uninterruptible I/O
us   user CPU
sy   system CPU
id   idle CPU
wa   I/O wait
```

One brief spike is normal. Look for sustained patterns and correlate them with workload and latency.

---

# CPU Capacity and Affinity

```bash
lscpu
nproc
taskset -pc 1234
```

Containers may see host CPU information while being limited by cgroups. For a `systemd` service:

```bash
systemctl show app.service -p CPUQuotaPerSecUSec -p AllowedCPUs
```

For cgroup v2, inspect `cpu.max`, `cpu.stat`, and `cpuset.cpus.effective` under the process's cgroup.

---

# Troubleshooting Flow

```bash
uptime
nproc
top
vmstat 1 10
mpstat -P ALL 1 5
pidstat -u -d -w 1 5
ps -eo pid,ppid,stat,%cpu,%mem,etime,cmd --sort=-%cpu | head -20
```

Ask:

- Is work CPU-bound or blocked on I/O?
- Is one core saturated while others are idle?
- Is the pressure host-wide or inside a container limit?
- Is virtual-machine steal time high?
- Did the issue spike briefly or persist?

Do not react to load average alone; correlate it with CPU states, blocked tasks, latency, and I/O.
