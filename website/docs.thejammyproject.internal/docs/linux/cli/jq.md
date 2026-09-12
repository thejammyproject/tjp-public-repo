# Linux `jq` Guide

`jq` parses, filters, transforms, and formats JSON.

---

# Basics

```bash
jq . response.json
curl -fsS https://api.example.com/status | jq .
```

Given:

```json
{"service":"api","healthy":true,"ports":[80,443],"owner":{"name":"alice"}}
```

Select values:

```bash
jq '.service' response.json
jq '.owner.name' response.json
jq '.ports[0]' response.json
jq '.ports[]' response.json
```

Use `-r` for raw strings without JSON quotes:

```bash
jq -r '.owner.name' response.json
```

---

# Arrays and Objects

```bash
jq '.items[]' response.json
jq '.items[] | .name' response.json
jq '.items | length' response.json
jq '.items[0:3]' response.json
jq '{name: .service, status: .healthy}' response.json
```

Construct delimited output:

```bash
jq -r '.items[] | [.name, .status] | @tsv' response.json
jq -r '.items[] | [.name, .status] | @csv' response.json
```

---

# Filtering and Sorting

```bash
jq '.items[] | select(.status == "running")' response.json
jq '.items[] | select(.cpu > 80) | {name, cpu}' response.json
jq '.items | sort_by(.cpu) | reverse' response.json
jq '.items | map(.name)' response.json
jq '.items | group_by(.status) | map({status: .[0].status, count: length})' response.json
```

Alternative and default values:

```bash
jq '.message // "no message"' response.json
jq '.items[]? | .name?' response.json
```

`?` suppresses errors for missing or wrongly typed paths; use it deliberately so malformed input is not silently hidden.

---

# Variables and Arguments

Pass shell values safely:

```bash
jq --arg name "$server_name" '.items[] | select(.name == $name)' response.json
jq --argjson limit "$limit" '.items[] | select(.cpu > $limit)' response.json
```

Do not build filters by concatenating untrusted shell text.

Create JSON:

```bash
jq -n --arg name "$server_name" --arg env "$environment" \
    '{name: $name, environment: $env}'
```

---

# Update Data

`jq` writes transformed JSON to stdout; it does not edit the input in place.

```bash
jq '.enabled = true' config.json > config.json.new
jq '.items |= map(select(.disabled != true))' response.json
```

Validate before replacing the original:

```bash
jq empty config.json.new
mv config.json.new config.json
```

---

# Cloud and API Examples

AWS instance IDs:

```bash
aws ec2 describe-instances |
    jq -r '.Reservations[].Instances[].InstanceId'
```

Kubernetes pod names and phases:

```bash
kubectl get pods -o json |
    jq -r '.items[] | [.metadata.name, .status.phase] | @tsv'
```

Fail when an API health value is false:

```bash
curl -fsS URL | jq -e '.healthy == true' > /dev/null
```

With `-e`, false or null results produce a non-zero exit status.

---

# Quick Reference

```bash
jq . file.json
jq -r '.field' file.json
jq '.array[] | select(.active)' file.json
jq -r '.array[] | [.name, .status] | @tsv' file.json
jq --arg value "$value" 'select(.field == $value)' file.json
jq -e '.healthy == true' file.json
```
