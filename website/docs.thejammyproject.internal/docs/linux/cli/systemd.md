# Linux `systemd` Guide

`systemd` is the service and system manager used by many Linux distributions. It manages units, dependencies, cgroups, startup ordering, and service supervision.

---

# Services and Processes

A process is a running program. A service unit is a definition describing how `systemd` should manage one or more processes.

```bash
systemctl status nginx.service
systemctl show nginx.service -p MainPID -p SubState -p ControlGroup
```

`systemd` tracks services with Linux control groups, so it can supervise more than a single PID.

---

# Everyday Commands

```bash
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx
sudo systemctl reload-or-restart nginx
systemctl status nginx
systemctl is-active nginx
systemctl is-enabled nginx
```

```text
start      run now
stop       stop now
restart    stop and start
reload     ask the running service to reload configuration
enable     arrange startup at boot
disable    remove startup links
mask       make all starts impossible until unmasked
```

Enabling does not normally start a service:

```bash
sudo systemctl enable --now nginx
sudo systemctl disable --now nginx
```

---

# Inspect Units

```bash
systemctl list-units --type=service
systemctl list-units --type=service --state=failed
systemctl list-unit-files --type=service
systemctl cat nginx.service
systemctl show nginx.service
systemctl list-dependencies nginx.service
```

Find the unit file and drop-ins:

```bash
systemctl show nginx.service -p FragmentPath -p DropInPaths
```

Common locations:

```text
/usr/lib/systemd/system/   package-provided units
/lib/systemd/system/       package-provided units on some distributions
/etc/systemd/system/       administrator units and overrides
/run/systemd/system/       runtime units
```

Do not directly edit vendor unit files. Create an override:

```bash
sudo systemctl edit nginx.service
```

---

# Unit File Structure

```ini
[Unit]
Description=Example API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=app
Group=app
WorkingDirectory=/opt/example
ExecStart=/opt/example/bin/server
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Important rules:

- `ExecStart` is not run through a shell unless you explicitly invoke one.
- Use absolute executable paths.
- Shell operators such as `>`, `|`, and `&&` are not interpreted automatically.
- Environment expansion follows `systemd` rules, not interactive shell rules.

Validate a unit:

```bash
systemd-analyze verify /etc/systemd/system/example.service
```

After unit-file changes:

```bash
sudo systemctl daemon-reload
sudo systemctl restart example.service
```

`daemon-reload` reloads manager configuration; it does not restart the service.

---

# Service Types

```text
simple       ExecStart process is the main process
exec         like simple, but startup waits until exec succeeds
forking      daemon forks and parent exits; often uses PIDFile
oneshot      command runs to completion
notify       service reports readiness with sd_notify
idle         delays execution until jobs settle
```

Modern applications should usually run in the foreground with `Type=simple`, `exec`, or `notify`.

---

# Restart Policies

```ini
Restart=no
Restart=on-failure
Restart=always
RestartSec=5s
StartLimitIntervalSec=60s
StartLimitBurst=5
```

Clear a start-rate-limit failure after fixing the cause:

```bash
sudo systemctl reset-failed example.service
sudo systemctl start example.service
```

Do not use automatic restart to hide repeated crashes. Inspect the journal and exit status.

---

# Dependencies and Ordering

```text
Wants=       weak requirement
Requires=    stronger requirement
After=       ordering only: start this unit later
Before=      ordering only: start this unit earlier
Conflicts=   units should not be active together
```

`After=network.target` does not guarantee usable networking. Services needing configured networking commonly use both:

```ini
Wants=network-online.target
After=network-online.target
```

---

# Targets

Targets group units and represent system states.

```bash
systemctl get-default
systemctl set-default multi-user.target
systemctl isolate rescue.target
systemctl list-dependencies multi-user.target
```

Common targets include `multi-user.target`, `graphical.target`, `rescue.target`, and `network-online.target`.

`isolate` stops units not required by the selected target and is disruptive.

---

# Troubleshooting

```bash
systemctl status example.service
journalctl -u example.service -b
systemctl show example.service -p Result -p ExecMainCode -p ExecMainStatus
systemctl cat example.service
systemd-analyze critical-chain example.service
```

If a stopped service's process remains or returns:

```bash
systemctl show example.service -p MainPID -p ControlGroup -p KillMode -p Restart
systemd-cgls
pgrep -af example
systemctl list-timers --all
```

Check for another unit, timer, cron job, container orchestrator, or manual process. A matching executable is not necessarily part of the stopped service.

---

# Quick Reference

```bash
systemctl status UNIT
systemctl is-active UNIT
systemctl is-enabled UNIT
sudo systemctl enable --now UNIT
sudo systemctl restart UNIT
sudo systemctl reload UNIT
systemctl cat UNIT
journalctl -u UNIT -b
sudo systemctl daemon-reload
```
