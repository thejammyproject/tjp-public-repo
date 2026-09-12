# Linux Networking Guide

Use a layered approach: interface, address, route, name resolution, transport connection, then application protocol.

---

# Interfaces and Addresses

```bash
ip link
ip -br link
ip addr
ip -br addr
ip -s link show eth0
```

Bring an interface up or down:

```bash
sudo ip link set dev eth0 up
sudo ip link set dev eth0 down
```

`ip` changes are usually temporary. Use the distribution's network configuration system for persistent changes.

---

# Routes

```bash
ip route
ip -6 route
ip route get 1.1.1.1
ip route get 10.0.0.20 from 10.0.0.10
```

A typical default route:

```text
default via 192.0.2.1 dev eth0
```

`ip route get` shows the route, source address, and interface the kernel would select without sending traffic.

---

# Listening Sockets and Connections

```bash
ss -lntp
ss -lnup
ss -tan
ss -s
```

```text
-l   listening
-n   numeric addresses and ports
-t   TCP
-u   UDP
-p   process information
-a   all sockets
```

Filter examples:

```bash
ss -lntp 'sport = :443'
ss -tan state established
sudo lsof -iTCP:8080 -sTCP:LISTEN
```

`127.0.0.1:8080` only accepts local IPv4 connections. `0.0.0.0:8080` listens on all local IPv4 addresses. Firewall and routing rules still apply.

---

# Reachability

```bash
ping -c 4 192.0.2.10
ping -c 4 example.com
tracepath example.com
traceroute example.com
```

Failed ping does not prove a host is down; ICMP may be filtered. Successful ping proves basic IP reachability, not that an application is healthy.

Test a TCP port:

```bash
nc -vz example.com 443
timeout 3 bash -c '</dev/tcp/example.com/443'
```

Test the application protocol:

```bash
curl -v https://example.com/health
openssl s_client -connect example.com:443 -servername example.com
```

---

# DNS

```bash
getent ahosts example.com
dig example.com
resolvectl query example.com
cat /etc/resolv.conf
```

`getent` follows the system's configured name-service path and often best represents what an application sees. `dig` directly queries DNS and is ideal for DNS-specific diagnosis.

---

# Network Configuration and Neighbours

```bash
ip neigh
ip rule
resolvectl status
networkctl status
nmcli device status
```

The available network manager varies by distribution: NetworkManager, `systemd-networkd`, Netplan, ifupdown, or cloud tooling.

---

# Packet Capture

```bash
sudo tcpdump -ni any port 443
sudo tcpdump -ni eth0 host 192.0.2.10
sudo tcpdump -ni any -w incident.pcap 'host 192.0.2.10 and port 443'
```

Captures may contain credentials, personal data, and payloads. Limit the filter, duration, storage, and access.

---

# “Server Reachable but Application Is Not”

Work from the server outward:

```bash
systemctl status app.service
ss -lntp 'sport = :8080'
curl -v http://127.0.0.1:8080/health
curl -v http://SERVER_IP:8080/health
ip addr
ip route
sudo nft list ruleset
journalctl -u app.service -b
```

Then test from the client:

```bash
getent ahosts app.example.com
ip route get SERVER_IP
nc -vz SERVER_IP 8080
curl -v http://app.example.com:8080/health
```

Common causes include wrong bind address, wrong port, host or cloud firewall, missing route, DNS mismatch, reverse-proxy configuration, TLS name/certificate problems, or an unhealthy application.

---

# Quick Troubleshooting Flow

```text
1. ip -br link                  interface up?
2. ip -br addr                  expected address?
3. ip route get DESTINATION     valid route and source?
4. getent ahosts NAME           expected resolution?
5. ss -lntp                     service listening correctly?
6. nc/curl                      transport and application response?
7. firewall rules               traffic allowed?
8. tcpdump                      packets arriving and leaving?
```
