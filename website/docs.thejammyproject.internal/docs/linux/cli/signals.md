# Linux Signals Guide

Signals are notifications sent to processes. They request actions such as stopping, reloading, continuing, or terminating.

---

# Signals Worth Knowing

```text
1    SIGHUP     terminal closed; commonly used to request reload
2    SIGINT     interrupt, normally Ctrl+C
9    SIGKILL    immediate kernel termination; cannot be caught
15   SIGTERM    polite termination request; default for kill
18   SIGCONT    continue a stopped process
19   SIGSTOP    stop immediately; cannot be caught
20   SIGTSTP    terminal stop, normally Ctrl+Z
```

Names are clearer than numbers:

```bash
kill -TERM 1234
kill -HUP 1234
kill -KILL 1234
```

List signals:

```bash
kill -l
```

Signal numbers can vary across architectures, so scripts should prefer names.

---

# `kill`

Despite its name, `kill` sends a signal.

```bash
kill 1234              # SIGTERM
kill -TERM 1234
kill -0 1234           # check existence/permission; send no signal
```

Signal several known PIDs:

```bash
kill -TERM 1234 1235 1236
```

A negative process-group ID targets a process group:

```bash
kill -TERM -- -4321
```

Confirm the group first with `ps -o pid,pgid,sid,args`.

---

# `pkill` and `killall`

`pkill` selects processes using rules similar to `pgrep`:

```bash
pgrep -a nginx
pkill -TERM nginx
pkill -HUP -x nginx
pkill -TERM -u alice worker
```

Use `-x` for an exact process-name match. Use `pgrep` with the same selection first to preview targets.

`killall` sends a signal to processes by name:

```bash
killall -TERM nginx
```

Its behaviour differs between operating systems. For portable automation, prefer known PIDs or carefully constrained `pkill`.

---

# Graceful Termination

Start with `SIGTERM`:

```bash
kill -TERM "$pid"
```

This allows a well-written application to:

- Stop accepting work.
- Finish or cancel requests.
- Flush buffers.
- Remove temporary files.
- Close database connections.

Wait and escalate only if necessary:

```bash
kill -TERM "$pid"
for _ in {1..10}; do
    kill -0 "$pid" 2>/dev/null || break
    sleep 1
done
kill -0 "$pid" 2>/dev/null && kill -KILL "$pid"
```

PID reuse is possible in longer scripts. Service managers and pidfds avoid some PID-race problems.

---

# Why `kill -9` Is Not the First Choice

`SIGKILL` is handled by the kernel and cannot be caught, blocked, or ignored. The process cannot clean up.

Possible consequences:

- Incomplete writes or transactions
- Stale lock files
- Lost buffered logs
- Interrupted child processes
- Harder diagnosis because shutdown handlers never run

Use it when graceful termination failed or immediate containment is necessary.

Even `SIGKILL` cannot immediately remove a process stuck in uninterruptible `D` state; the kernel wait must resolve.

---

# Reloading Services

Some daemons interpret `SIGHUP` as a configuration reload:

```bash
kill -HUP "$pid"
```

This is application-specific. Prefer the service's supported interface:

```bash
sudo systemctl reload nginx
nginx -t && sudo systemctl reload nginx
```

---

# Shell Traps

A shell script can handle signals:

```bash
cleanup() {
    rm -f -- "$tmpfile"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
```

`EXIT` is a shell pseudo-signal used for cleanup when the shell exits.

---

# Safe Workflow

```bash
pgrep -af exact-pattern
ps -p PID -o pid,ppid,user,stat,lstart,args
kill -TERM PID
ps -p PID
kill -KILL PID       # only if still required
```

For managed services, use `systemctl stop` so the service manager applies its configured shutdown behaviour and tracks the result.
