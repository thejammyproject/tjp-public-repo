# Linux Users and Groups Guide

Linux associates processes and files with numeric user IDs (`UIDs`) and group IDs (`GIDs`). Names are mappings provided by local files or identity services.

---

# Inspect Identity

```bash
whoami
id
id alice
groups
groups alice
```

`id` shows real group membership for the selected account. A running session may not see newly added supplementary groups until the user logs in again.

---

# Use `getent`

`getent` queries the system's configured name services, including local files, LDAP, and SSSD.

```bash
getent passwd alice
getent group developers
getent passwd
getent group
```

Prefer it over reading `/etc/passwd` directly when central identity may be in use.

Password database fields:

```text
name:password-placeholder:UID:GID:comment:home:shell
```

Password hashes are normally stored in `/etc/shadow`, which is restricted.

---

# Create and Modify Users

Distribution defaults differ. Typical commands are:

```bash
sudo useradd -m -s /bin/bash alice
sudo passwd alice
sudo usermod -aG sudo,docker alice
sudo usermod -s /bin/bash alice
sudo usermod -L alice
sudo usermod -U alice
```

The `-a` in `usermod -aG` is essential when adding supplementary groups. Without it, `-G` replaces the existing list.

On Debian/Ubuntu, the friendlier wrapper is often:

```bash
sudo adduser alice
sudo adduser alice developers
```

---

# Create and Modify Groups

```bash
sudo groupadd developers
sudo groupmod -n platform developers
sudo gpasswd -a alice developers
sudo gpasswd -d alice developers
```

Use `newgrp developers` to start a shell with a different effective group, or log out and back in to refresh memberships.

---

# Service Accounts

A service account commonly has:

- A system UID
- No interactive password
- A non-login shell
- A narrowly owned working directory

```bash
sudo useradd --system --home /var/lib/example --create-home \
    --shell /usr/sbin/nologin example
```

Do not assume all system accounts use the same UID range; distribution policy controls it.

---

# `sudo` Basics

Run one command as root:

```bash
sudo command
```

Run as another user:

```bash
sudo -u app command
sudo -iu app
```

Inspect privileges:

```bash
sudo -l
sudo -l -U alice
```

Edit sudo policy with `visudo`, which checks syntax:

```bash
sudo visudo
sudo visudo -f /etc/sudoers.d/platform
```

Example:

```sudoers
%operators ALL=(root) /usr/bin/systemctl restart example.service
```

Use absolute command paths and grant the narrowest required capability. `NOPASSWD` changes authentication, not authorisation, and should be justified.

---

# Logged-In Users

```bash
who
w
last
lastlog
loginctl list-sessions
```

These answer different questions: current sessions, current activity, historical logins, and `systemd-logind` sessions.

---

# Remove Accounts Safely

Before removal, inspect processes, scheduled jobs, files, keys, and service ownership:

```bash
pgrep -u alice -a
sudo crontab -u alice -l
sudo find / -xdev -user alice -print
```

Then use the distribution's account-management command. Removing a home directory or user-owned data is destructive and should be a separate deliberate decision.

---

# Troubleshooting

```bash
id alice
getent passwd alice
getent group developers
sudo -l -U alice
namei -l /path/alice/cannot/access
```

Check numeric IDs with `ls -ln` if name-service mappings are broken. Authentication, account lookup, sudo policy, filesystem permission, and application authorisation are separate layers.
