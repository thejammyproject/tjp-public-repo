# Linux Permissions Guide

Linux permissions control read, write, and execute access for the owning user, owning group, and everyone else.

---

# Read Permission Strings

```bash
ls -l file
```

```text
-rwxr-xr-- 1 alice developers 1234 Sep 12 10:00 deploy.sh
│└─┬┘└─┬┘└─┬┘
│  │   │   └ other permissions
│  │   └ group permissions
│  └ owner permissions
└ file type
```

```text
r = read
w = write
x = execute, or traverse/search for directories
```

Directory permissions differ:

```text
r = list names
w = create, rename, and remove directory entries
x = access entries and traverse the directory
```

Deleting a file depends mainly on the parent directory's permissions, not the file's write bit.

---

# Numeric Modes

```text
r = 4
w = 2
x = 1
```

Add each class:

```text
7 = rwx
6 = rw-
5 = r-x
4 = r--
0 = ---
```

Common examples:

```bash
chmod 644 file.txt       # rw-r--r--
chmod 600 secret.key     # rw-------
chmod 755 script.sh      # rwxr-xr-x
chmod 750 private-dir    # rwxr-x---
```

Avoid reflexive `chmod 777`; it grants all users write access and rarely fixes the underlying ownership or deployment problem.

---

# Symbolic Modes

```bash
chmod u+x script.sh
chmod g+w shared-dir
chmod o-r secret.txt
chmod a+r public.txt
chmod u=rw,g=r,o= file.txt
```

```text
u = user/owner
g = group
o = other
a = all
```

Recursive changes can affect directories and files incorrectly. Use `find` for different modes:

```bash
find /srv/site -type d -exec chmod 755 {} +
find /srv/site -type f -exec chmod 644 {} +
```

---

# Ownership

```bash
sudo chown alice file.txt
sudo chown alice:developers file.txt
sudo chgrp developers file.txt
sudo chown -R app:app /srv/app
```

Before a recursive change, confirm the exact path and inspect current ownership. Symlink handling varies by command and option; read the command's documentation for security-sensitive trees.

---

# `umask`

`umask` removes permission bits from an application's requested mode.

```bash
umask
umask 027
```

Typical calculation:

```text
files:       666 requested, minus umask
directories: 777 requested, minus umask

umask 022 -> files 644, directories 755
umask 027 -> files 640, directories 750
umask 077 -> files 600, directories 700
```

Applications can request more restrictive modes themselves.

---

# Special Bits

```text
SUID    executable runs with file owner's effective identity
SGID    executable uses file group; directory inherits group ownership
sticky  only entry owner, directory owner, or privileged user can delete
```

```bash
chmod u+s executable
chmod g+s shared-dir
chmod +t shared-dir
```

Numeric forms:

```bash
chmod 4755 executable
chmod 2775 shared-dir
chmod 1777 shared-temp
```

Find special-permission files:

```bash
find /usr -xdev -type f -perm /6000 -ls
```

---

# ACLs

Access control lists grant permissions beyond the basic owner/group/other model.

```bash
getfacl file.txt
setfacl -m u:bob:r file.txt
setfacl -m g:developers:rw shared-dir
setfacl -d -m g:developers:rwx shared-dir
setfacl -b file.txt
```

A `+` after the mode in `ls -l` often indicates an ACL. Default directory ACLs affect newly created entries.

---

# Troubleshooting “Permission Denied”

```bash
id
namei -l /full/path/to/file
ls -ld /full /full/path /full/path/to /full/path/to/file
getfacl /full/path/to/file
```

Also check:

- Read-only mounts
- SELinux or AppArmor policy
- Service sandboxing in `systemd`
- NFS root squashing or server-side permissions
- The actual runtime user and group

`sudo` can bypass many discretionary checks, but it is not a diagnosis.
