# Linux Disk and Storage Guide

Linux storage troubleshooting involves filesystems, block devices, mounts, space, inodes, and I/O.

---

# Filesystem Usage with `df`

```bash
df -h
df -hT
df -i
df -h /var/lib/app
```

```text
-h   human-readable sizes
-T   filesystem type
-i   inode usage instead of byte usage
```

A filesystem can have free bytes but no free inodes, usually because it contains huge numbers of small files.

`df` reports filesystem allocation. It does not show which directory owns the space.

---

# Directory Usage with `du`

```bash
du -sh /var/log
du -h --max-depth=1 /var | sort -h
du -xah /var | sort -h | tail
```

```text
-s   summary
-h   human-readable
-a   include files
-x   stay on one filesystem
```

Use `--` before paths beginning with `-`.

If `df` shows much more usage than `du`, look for deleted files that are still open:

```bash
sudo lsof +L1
```

Space is released when the process closes the file or restarts. Truncating file descriptors blindly can corrupt applications.

---

# Block Devices

```bash
lsblk
lsblk -f
lsblk -o NAME,SIZE,TYPE,FSTYPE,FSVER,LABEL,UUID,MOUNTPOINTS
sudo blkid
```

`lsblk` shows the device hierarchy, including disks, partitions, LVM volumes, encryption layers, and mount points. `blkid` reports filesystem signatures and UUIDs.

---

# Mounts

```bash
findmnt
findmnt /var
mount | column -t
```

Temporary mount:

```bash
sudo mount /dev/sdb1 /mnt/data
sudo umount /mnt/data
```

If unmounting reports “target is busy”:

```bash
findmnt /mnt/data
sudo fuser -vm /mnt/data
sudo lsof +D /mnt/data
```

Avoid forced or lazy unmounts until you understand the active users and consequences.

---

# `/etc/fstab`

An entry contains:

```text
device  mount-point  filesystem-type  options  dump  fsck-order
```

Example:

```fstab
UUID=1234-ABCD /srv/data ext4 defaults,nofail 0 2
```

Prefer UUIDs or stable identifiers over `/dev/sdX` names. Test changes before reboot:

```bash
sudo findmnt --verify --verbose
sudo mount -a
```

Keep an existing recovery session open when changing remote-server mounts.

---

# Find Space Consumers

Largest top-level directories:

```bash
sudo du -xhd1 / | sort -h
```

Large files on one filesystem:

```bash
sudo find / -xdev -type f -size +1G -printf '%s %p\n' | sort -nr
```

Journal usage:

```bash
journalctl --disk-usage
```

Container usage:

```bash
docker system df
```

Do not delete files merely because they are large. Identify ownership, retention requirements, backups, and the correct application cleanup mechanism.

---

# I/O and Health

```bash
iostat -xz 1
vmstat 1
cat /proc/diskstats
sudo smartctl -a /dev/sda
journalctl -k -b | grep -iE 'i/o error|nvme|ata|ext4|xfs'
```

Device names, SMART support, and interpretation differ for physical disks, virtual disks, RAID, SAN, and cloud volumes.

---

# Troubleshooting Flow

```bash
df -hT
df -i
findmnt
lsblk -f
sudo du -xhd1 /affected/mount | sort -h
sudo lsof +L1
journalctl -k -b -p warning
```

Distinguish:

- Filesystem full by bytes
- Inode exhaustion
- Deleted-but-open files
- Read-only remount after errors
- Block-device capacity exhaustion
- I/O latency or hardware errors
- An unavailable remote mount
