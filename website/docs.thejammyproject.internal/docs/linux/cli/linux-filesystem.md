# Linux Filesystem Guide

The Filesystem Hierarchy Standard gives major directories conventional purposes, although distributions and applications vary.

---

# Main Directories

```text
/       root of the entire filesystem tree
/etc    host-specific system configuration
/var    variable data: logs, caches, queues, databases, state
/usr    installed userland programs, libraries, and shared data
/opt    optional/add-on application packages
/home   normal users' home directories
/root   root user's home directory
/tmp    temporary files, commonly cleaned automatically
/run    volatile runtime state since boot
/proc   virtual process and kernel interface
/sys    virtual device and kernel object interface
/dev    device nodes and pseudo-devices
/boot   bootloader and kernel files
/mnt    temporary administrator mounts
/media  removable-media mounts
/srv    data served by this system
```

---

# `/bin`, `/sbin`, and `/usr`

Historically:

```text
/bin       essential user commands
/sbin      essential system-administration commands
/usr/bin   most user commands
/usr/sbin  most administration commands
```

Many modern systems use a merged `/usr`, where `/bin` and `/sbin` are symbolic links into `/usr`. Scripts should use commands through a suitable `PATH` or known portable paths rather than assuming every distribution has the same layout.

`/usr/local` is for software installed by the local administrator and is kept separate from distribution-managed `/usr` content:

```text
/usr/local/bin
/usr/local/sbin
/usr/local/lib
```

---

# Configuration and Application Data

```text
/etc/app/             system-wide configuration
/var/lib/app/         persistent application state
/var/log/app/         logs
/var/cache/app/       regenerable cache
/run/app/             runtime PID files, sockets, transient state
/opt/app/             self-contained third-party application
/srv/app/             service data exposed by the host
```

Do not put persistent data in `/run` or assume `/tmp` survives reboot. Do not put frequently changing state in `/etc`.

---

# Virtual Filesystems

`/proc`, `/sys`, and much of `/dev` are kernel-backed interfaces, not ordinary data stored on disk.

```bash
findmnt /proc /sys /dev
mount | grep -E ' on /(proc|sys|dev) '
```

Reading these files can expose live kernel state. Writing some of them changes live system behaviour, so understand the specific interface first.

---

# Paths and Links

```bash
pwd
realpath path
readlink link
readlink -f link
ln source hard-link
ln -s target symbolic-link
```

A hard link is another directory entry for the same inode and normally cannot cross filesystems. A symbolic link stores a target path and can be broken.

Inspect every path component and permission:

```bash
namei -l /var/lib/app/data/file
```

---

# Find Filesystem and Mount Information

```bash
df -hT
findmnt
lsblk -f
stat file
stat -f filesystem-path
```

Filesystem boundaries matter for capacity, permissions, snapshots, backups, rename operations, and `find -xdev`.

---

# What Belongs Where?

```text
Administrator script           /usr/local/bin
Administrator system command   /usr/local/sbin
Packaged service config         /etc/service
Service's persistent state      /var/lib/service
Service logs                    /var/log/service or journal
Short-lived runtime socket      /run/service
Temporary scratch data          /tmp or /var/tmp
Self-contained vendor app       /opt/vendor/app
User-specific config            ~/.config/app
User-specific state             ~/.local/state/app
```

`/var/tmp` is generally intended to survive longer than `/tmp`, but cleanup policy is system-specific.

---

# Troubleshooting Questions

- Is the path on the expected filesystem?
- Is the mount present and writable?
- Does every parent directory allow traversal?
- Is a symlink changing the effective destination?
- Is the data persistent or stored on a volatile filesystem?
- Is a package manager or application supposed to own the file?
- Could a container mount namespace show a different tree?
