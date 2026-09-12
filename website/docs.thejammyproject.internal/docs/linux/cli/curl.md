# Linux `curl` Guide

`curl` transfers data using protocols including HTTP and HTTPS. It is invaluable for API testing and service troubleshooting.

---

# Basic Requests

```bash
curl https://example.com
curl -I https://example.com
curl -i https://example.com
curl -v https://example.com
```

```text
-I   headers only using an HTTP HEAD request
-i   include response headers with the body
-v   verbose connection and protocol diagnostics
-sS  quiet progress but still show errors
```

Follow redirects:

```bash
curl -L https://example.com/old-path
```

---

# Fail Reliably in Scripts

```bash
curl -fsS https://example.com/health
curl --fail-with-body -sS https://example.com/api
```

By default, HTTP 404 or 500 responses do not make `curl` fail. `-f` makes HTTP errors produce a non-zero exit status.

Add timeouts and retries deliberately:

```bash
curl -fsS --connect-timeout 3 --max-time 10 \
    --retry 3 --retry-all-errors https://example.com/health
```

Retries can repeat side effects. Use care with non-idempotent requests.

---

# Methods and Request Bodies

JSON POST:

```bash
curl -fsS https://api.example.com/widgets \
    -H 'Content-Type: application/json' \
    -d '{"name":"server01"}'
```

`-d` implies POST unless `-X` says otherwise. Send a file:

```bash
curl -fsS https://api.example.com/widgets \
    -H 'Content-Type: application/json' \
    --data-binary @payload.json
```

Other methods:

```bash
curl -X PUT -H 'Content-Type: application/json' -d @payload.json URL
curl -X DELETE URL
```

Avoid unnecessary `-X`; options such as `-d`, `-I`, and `-T` select methods naturally.

---

# Headers and Authentication

```bash
curl -H 'Accept: application/json' URL
curl -u 'username:password' URL
curl -H "Authorization: Bearer $API_TOKEN" URL
```

Secrets in command arguments may be exposed in process listings and shell history. Prefer protected config/netrc files, environment-aware tooling, or secret injection appropriate to the platform.

Inspect response headers:

```bash
curl -sS -D headers.txt -o body.json URL
```

---

# Status Codes and Timing

Print only the status code:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' https://example.com
```

Show useful timings:

```bash
curl -sS -o /dev/null \
    -w 'dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} total=%{time_total}\n' \
    https://example.com
```

Separate DNS, TCP, TLS, server, and transfer delays when diagnosing latency.

---

# DNS, IP, and TLS Testing

Connect to a chosen IP while keeping the hostname and TLS SNI:

```bash
curl --resolve example.com:443:192.0.2.10 https://example.com/health
```

Choose an address family:

```bash
curl -4 URL
curl -6 URL
```

Use a client certificate:

```bash
curl --cert client.crt --key client.key https://example.com
```

`-k` disables TLS certificate verification:

```bash
curl -k https://example.com
```

Use it only as a short diagnostic step. It removes identity verification and should not become a production fix.

---

# Downloads and Uploads

```bash
curl -fLO https://example.com/archive.tar.gz
curl -fL -o local-name.tar.gz URL
curl -T file.txt https://example.com/upload/path
curl -F 'file=@report.txt' https://example.com/upload
```

Resume a partial download:

```bash
curl -C - -O URL
```

---

# API Pipelines

```bash
curl -fsS https://api.example.com/servers | jq '.items[] | {name, status}'
```

Save while inspecting:

```bash
curl -fsS URL | tee response.json | jq .
```

For scripts, combine `-f`, `-sS`, sensible timeouts, and explicit output handling.
