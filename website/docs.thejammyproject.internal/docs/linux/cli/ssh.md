# Linux SSH Guide

SSH provides encrypted remote shells, command execution, tunnelling, and file transfer.

---

# Connect and Run Commands

```bash
ssh user@server
ssh -p 2222 user@server
ssh user@server 'hostname && uptime'
```

The quoted remote command is interpreted by the remote shell. Be careful when inserting local variables or untrusted data.

Debug connection setup:

```bash
ssh -v user@server
ssh -vvv user@server
```

Verbose output shows configuration, address selection, key exchange, host-key checking, and authentication attempts.

---

# Keys

Create a modern key:

```bash
ssh-keygen -t ed25519 -a 100
```

Install its public half:

```bash
ssh-copy-id user@server
```

Key files commonly include:

```text
~/.ssh/id_ed25519       private key: never share
~/.ssh/id_ed25519.pub   public key
~/.ssh/authorized_keys  public keys allowed to log in
~/.ssh/known_hosts      remembered server host keys
```

Typical permissions:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

Ownership and parent-directory permissions also matter.

---

# Host-Key Verification

The host key proves the server's identity. Verify new fingerprints through a trusted channel.

Inspect a server's configured public keys locally on that server:

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

A changed host key can be legitimate after rebuild, but can also indicate misrouting or interception. Investigate before removing the old entry.

---

# SSH Configuration

`~/.ssh/config`:

```sshconfig
Host app-prod
    HostName 192.0.2.10
    User deploy
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
```

Then connect with:

```bash
ssh app-prod
```

Show evaluated configuration:

```bash
ssh -G app-prod
```

System-wide client configuration is usually under `/etc/ssh/ssh_config` and `ssh_config.d`.

---

# File Transfer

```bash
scp file.txt user@server:/tmp/
scp user@server:/var/log/app.log .
sftp user@server
rsync -av --progress -e ssh ./data/ user@server:/srv/data/
```

For resumable or repeated directory syncs, `rsync` is usually more capable than `scp`.

---

# Port Forwarding

Local forward: reach a remote-side service locally:

```bash
ssh -N -L 5432:db.internal:5432 bastion
```

Remote forward: expose a local-side service through the remote server:

```bash
ssh -N -R 8080:localhost:3000 server
```

SOCKS proxy:

```bash
ssh -N -D 1080 bastion
```

Useful options:

```text
-N                    do not run a remote command
-T                    do not allocate a terminal
-o ExitOnForwardFailure=yes  fail if the forward cannot be created
```

Forwarding can bypass network boundaries; use only where authorised.

---

# Jump Hosts and Agent Forwarding

```bash
ssh -J bastion user@private-server
```

Prefer `ProxyJump` over logging into a bastion and copying private keys there.

Agent forwarding (`ssh -A`) lets the remote host request signatures from your local agent. A compromised remote host can misuse that access while connected, so enable it only when necessary and trusted.

---

# Troubleshooting

```bash
ssh -vvv user@server
getent ahosts server
nc -vz server 22
ssh -G server | grep -E '^(hostname|user|port|identityfile) '
```

On the server:

```bash
sudo sshd -t
systemctl status ssh
journalctl -u ssh -b
ss -lntp 'sport = :22'
```

Common causes are network/firewall failure, wrong user or key, rejected file permissions, too many keys offered, host-key mismatch, or server policy.
