# Linux `journalctl` Guide

`journalctl` reads logs collected by `systemd-journald`.

---

# Basic Commands

```bash
journalctl
journalctl -r
journalctl -n 100
journalctl -f
journalctl -e
```

```text
-r       newest entries first
-n NUM   last NUM entries
-f       follow new entries
-e       jump to the end
--no-pager print directly instead of opening a pager
```

---

# Logs for a Unit

```bash
journalctl -u nginx.service
journalctl -u nginx.service -f
journalctl -u nginx.service -n 100
journalctl -u nginx.service -b
```

Several units:

```bash
journalctl -u nginx.service -u php8.3-fpm.service
```

`systemctl status` only shows a small recent excerpt; use `journalctl -u` for the full unit log.

---

# Time Filters

```bash
journalctl --since '2026-09-12 09:00:00'
journalctl --until '2026-09-12 10:00:00'
journalctl --since '1 hour ago'
journalctl --since today
journalctl -u nginx --since yesterday --until today
```

Use explicit timestamps when recording incident evidence so the time range is reproducible.

---

# Boots

Current boot:

```bash
journalctl -b
```

Previous boot:

```bash
journalctl -b -1
```

List known boots:

```bash
journalctl --list-boots
```

Previous-boot logs require persistent journal storage. If `/var/log/journal` is not configured, old logs may be unavailable after reboot.

---

# Priorities

```text
0 emerg
1 alert
2 crit
3 err
4 warning
5 notice
6 info
7 debug
```

Errors and more severe messages:

```bash
journalctl -p err
journalctl -p 0..3
journalctl -u nginx -p warning..alert
```

Priority is metadata supplied by the logging source and may not perfectly classify every problem.

---

# Kernel Logs

```bash
journalctl -k
journalctl -k -b
journalctl -k -p warning
```

Useful searches:

```bash
journalctl -k -b | grep -iE 'oom|out of memory|i/o error|segfault'
```

`dmesg` also reads kernel messages, but access can be restricted and older entries may have rotated.

---

# Filter by Journal Fields

```bash
journalctl _PID=1234
journalctl _UID=1000
journalctl _COMM=sshd
journalctl _EXE=/usr/sbin/sshd
journalctl SYSLOG_IDENTIFIER=app
```

Combine different fields as AND conditions:

```bash
journalctl _SYSTEMD_UNIT=nginx.service _PID=1234
```

Repeated values for one field act as alternatives:

```bash
journalctl _SYSTEMD_UNIT=nginx.service + _SYSTEMD_UNIT=php8.3-fpm.service
```

Show fields attached to entries:

```bash
journalctl -u nginx -n 1 -o verbose
```

---

# Output Formats

```bash
journalctl -o short-iso
journalctl -o short-iso-precise
journalctl -o cat
journalctl -o json
journalctl -o json-pretty
```

Process JSON output:

```bash
journalctl -u nginx --since today -o json |
    jq -r '[.__REALTIME_TIMESTAMP, .MESSAGE] | @tsv'
```

---

# Disk Usage and Retention

```bash
journalctl --disk-usage
sudo journalctl --vacuum-time=14d
sudo journalctl --vacuum-size=1G
```

Vacuuming deletes archived journal data. Configure retention in `journald.conf` rather than relying only on manual cleanup.

Check journal integrity:

```bash
journalctl --verify
```

---

# Troubleshooting Patterns

A service failed during the current boot:

```bash
systemctl status app.service
journalctl -u app.service -b -p warning
journalctl -u app.service -b --no-pager
```

System errors around an incident:

```bash
journalctl --since '2026-09-12 10:10' --until '2026-09-12 10:20' -p warning
```

Follow and filter a busy service:

```bash
journalctl -fu app.service | grep --line-buffered -iE 'error|timeout'
```

---

# Quick Reference

```bash
journalctl -u UNIT -b
journalctl -u UNIT -f
journalctl -b -1
journalctl --since '1 hour ago'
journalctl -p err
journalctl -k -b
journalctl _PID=PID
journalctl --disk-usage
```
