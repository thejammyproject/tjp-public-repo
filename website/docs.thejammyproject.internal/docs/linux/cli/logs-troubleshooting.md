# Linux Logs and Troubleshooting Guide

Good troubleshooting builds a timeline, tests one layer at a time, and preserves evidence before changing the system.

---

# Where Logs Live

Common sources:

```text
systemd journal        journalctl
traditional logs      /var/log
application logs      application-specific directory or stdout/stderr
kernel messages       journalctl -k, dmesg
container logs        runtime or orchestrator interface
audit logs            audit framework or security platform
cloud logs            provider logging service
```

Examples under `/var/log` vary by distribution:

```text
syslog or messages
auth.log or secure
kern.log
nginx/
apache2/ or httpd/
```

Do not assume a file exists; inspect logging configuration and the service definition.

---

# Inspect Large Files

```bash
less application.log
tail -n 100 application.log
tail -F application.log
head -n 50 application.log
grep -nC 3 'ERROR' application.log
```

Useful `less` commands:

```text
/pattern   search forward
?pattern   search backward
n / N      next / previous match
G / g      end / beginning
F          follow mode
Ctrl+C     leave follow mode
q          quit
```

Use `tail -F` for rotating log files; it follows by name and can reopen a replacement file.

---

# Time Windows and Correlation

```bash
journalctl --since '2026-09-12 10:00' --until '2026-09-12 10:15'
sed -n '/2026-09-12T10:00/,/2026-09-12T10:15/p' application.log
```

Record:

- Timezone and clock accuracy
- Incident start and end
- Request, trace, job, host, container, and user identifiers
- Deployment and configuration-change times
- Symptoms observed by clients and servers

Do not grep only for `error`; relevant events may be warnings, timeouts, retries, restarts, kernel events, or ordinary state changes.

---

# Systematic Workflow

```text
1. Define the symptom and impact.
2. Establish when it started and what changed.
3. Reproduce safely or obtain a concrete failing example.
4. Check health from the client and server perspectives.
5. Follow dependencies: DNS, network, proxy, app, database, storage.
6. Correlate logs and metrics in the same time window.
7. Form a testable hypothesis.
8. Make the smallest safe change.
9. Verify recovery and watch for recurrence.
10. Record cause, evidence, fix, and prevention.
```

---

# Service Investigation

```bash
systemctl status app.service
journalctl -u app.service -b
systemctl show app.service -p Result -p ExecMainStatus -p NRestarts
ps -eo pid,ppid,stat,%cpu,%mem,etime,args --forest
ss -lntp
```

Check the service itself before downstream symptoms. A listening socket does not guarantee a healthy application, and an active unit does not guarantee successful requests.

---

# Host Investigation

```bash
uptime
free -h
vmstat 1 5
df -hT
df -i
ip -br addr
ip route
journalctl -k -b -p warning
```

Capture the current state before restarting a service; restarts can destroy the best evidence and temporarily mask the cause.

---

# Log Rotation and Deleted Files

```bash
ls -lh /var/log/app/
logrotate -d /etc/logrotate.conf
sudo lsof +L1
```

`logrotate -d` debugs without rotating. Use `-f` carefully because it performs rotation.

A process can keep writing to a deleted file, consuming disk space invisibly to directory listings. Restart or correctly signal the owner so it reopens logs.

---

# Security and Evidence

Logs can contain credentials, tokens, IP addresses, personal data, request bodies, and customer content.

- Redact before sharing.
- Preserve original timestamps and files when evidence matters.
- Record commands and changes.
- Avoid modifying production data during diagnosis.
- Check retention and access-control requirements.

The aim is not merely to restore service, but to explain why the failure occurred and how recovery was verified.
