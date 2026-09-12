# Linux Cron and `systemd` Timers Guide

Cron and `systemd` timers run commands on a schedule.

---

# Cron Syntax

User crontabs use five time fields followed by a command:

```text
minute hour day-of-month month day-of-week command
```

```text
┌──────── minute (0-59)
│ ┌────── hour (0-23)
│ │ ┌──── day of month (1-31)
│ │ │ ┌── month (1-12)
│ │ │ │ ┌ day of week (0-7; Sunday is 0 or 7)
│ │ │ │ │
* * * * * command
```

Examples:

```cron
*/5 * * * * /usr/local/bin/health-check
0 2 * * * /usr/local/bin/backup
30 6 * * 1-5 /usr/local/bin/report
0 0 1 * * /usr/local/bin/monthly-task
```

Common shortcuts:

```text
@reboot @hourly @daily @weekly @monthly @yearly
```

---

# Manage Crontabs

```bash
crontab -l
crontab -e
sudo crontab -u app -l
sudo crontab -u app -e
```

`crontab -r` removes a crontab; use it cautiously.

System schedules may also exist in:

```text
/etc/crontab
/etc/cron.d/
/etc/cron.hourly/
/etc/cron.daily/
/etc/cron.weekly/
/etc/cron.monthly/
```

`/etc/crontab` and files under `/etc/cron.d` include a username field:

```cron
0 2 * * * root /usr/local/sbin/backup
```

---

# Cron Environment Gotchas

Cron has a small, non-interactive environment. Commands that work in a terminal may fail because of:

- A different `PATH`
- No working directory assumption
- Missing environment variables
- No interactive shell setup
- Different permissions
- `%` being treated specially by some cron implementations

Use absolute paths and redirect output:

```cron
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAILTO=ops@example.com

0 2 * * * cd /opt/app && /opt/app/bin/backup >> /var/log/app-backup.log 2>&1
```

Test as the scheduled user with a minimal environment:

```bash
sudo -u app env -i PATH=/usr/bin:/bin /opt/app/bin/job
```

Use a lock to prevent overlapping runs:

```cron
*/5 * * * * /usr/bin/flock -n /run/health-check.lock /usr/local/bin/health-check
```

---

# `systemd` Timers

A timer activates another unit, usually a service.

`backup.service`:

```ini
[Unit]
Description=Create application backup

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup
```

`backup.timer`:

```ini
[Unit]
Description=Run application backup nightly

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true
RandomizedDelaySec=5m

[Install]
WantedBy=timers.target
```

Install and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now backup.timer
```

---

# Timer Expressions

```ini
OnCalendar=hourly
OnCalendar=daily
OnCalendar=Mon..Fri 06:30
OnCalendar=*-*-01 00:00:00
```

Validate calendar expressions:

```bash
systemd-analyze calendar 'Mon..Fri 06:30'
```

Monotonic timers schedule relative to events:

```ini
OnBootSec=5min
OnUnitActiveSec=1h
```

Important timer settings:

```text
Persistent=true          catch up missed calendar runs after downtime
RandomizedDelaySec=      spread load across machines
AccuracySec=             permitted scheduling coalescence
Unit=                    unit to activate if not same basename
```

---

# Inspect and Troubleshoot Timers

```bash
systemctl list-timers --all
systemctl status backup.timer
systemctl status backup.service
journalctl -u backup.timer -u backup.service
systemctl show backup.timer -p NextElapseUSecRealtime -p LastTriggerUSec
```

The timer schedules work; the associated service contains the command and its result.

---

# Find What Keeps Restarting a Process

Check all likely schedulers and supervisors:

```bash
systemctl list-timers --all
systemctl list-units --type=service --state=running
crontab -l
sudo crontab -l
sudo find /etc/cron.d /etc/cron.* -type f -maxdepth 2 -print
atq
```

Also inspect containers, configuration-management agents, process supervisors, cloud-init, and CI runners.

Use timestamps and parent PIDs to correlate starts:

```bash
ps -eo pid,ppid,lstart,args --forest
journalctl --since '15 minutes ago'
```

---

# Cron vs Timers

```text
Cron                         systemd timers
simple and widely available integrated logging through journal
compact schedule syntax      rich calendar and monotonic schedules
limited environment          explicit service environment
manual overlap handling      service state prevents same-unit overlap
missed runs usually missed   Persistent=true can catch up
```

Use cron for small portable schedules. Use timers when service supervision, dependencies, structured logs, catch-up behaviour, or resource controls matter.
