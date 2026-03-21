# ULP DNS Node Fabric v1

## Purpose
Make the DNS layout operationally consistent across three capacity nodes while keeping function surfaces stable:

- `portal.*` -> projection/UI
- `artifact.*` -> artifact/static data plane
- `mcp.*` -> control plane API
- `sid.*` / `oid.*` -> identity and object resolution

## Current Resolved A Records (2026-03-21)

- `universal-life-protocol.com` -> `74.208.190.29`
- `portal.universal-life-protocol.com` -> `74.208.190.29`
- `artifact.universal-life-protocol.com` -> `74.208.190.29`
- `mcp.universal-life-protocol.com` -> `74.208.190.29`
- `portal.small.universal-life-protocol.com` -> `69.48.202.32`
- `mcp.small.universal-life-protocol.com` -> `69.48.202.32`
- `portal.medium.universal-life-protocol.com` -> `65.38.98.105`
- `mcp.medium.universal-life-protocol.com` -> `65.38.98.105`
- `portal.large.universal-life-protocol.com` -> `74.208.190.29`
- `mcp.large.universal-life-protocol.com` -> `74.208.190.29`

## Canonical Naming Rule

Use:

`<function>.<capacity>.universal-life-protocol.com`

Examples:

- `portal.small.universal-life-protocol.com`
- `artifact.medium.universal-life-protocol.com`
- `mcp.large.universal-life-protocol.com`

Keep function roots as default public aliases:

- `portal` -> large
- `artifact` -> large
- `mcp` -> large

Avoid capacity-only hosts (`small`, `medium`) in app routing.

## Node Roles

- `small` (`69.48.202.32`): control-plane constrained runtime
- `medium` (`65.38.98.105`): balanced runtime
- `large` (`74.208.190.29`): default public entry

## Nginx Front Door (Per Node)

Install:

```bash
apt update
apt install -y nginx certbot python3-certbot-nginx
```

Create `/etc/nginx/sites-available/ulp-node.conf`:

```nginx
map $host $portal_root {
  default /var/www/ulp-root;
}

map $host $artifact_root {
  default /var/www/ulp-root;
}

server {
  listen 80;
  server_name
    universal-life-protocol.com
    www.universal-life-protocol.com
    portal.universal-life-protocol.com
    portal.small.universal-life-protocol.com
    portal.medium.universal-life-protocol.com
    portal.large.universal-life-protocol.com;

  location / {
    root $portal_root;
    try_files $uri $uri/ /index.html;
  }
}

server {
  listen 80;
  server_name
    artifact.universal-life-protocol.com
    artifact.small.universal-life-protocol.com
    artifact.medium.universal-life-protocol.com
    artifact.large.universal-life-protocol.com;

  location / {
    root $artifact_root;
    autoindex on;
    add_header Cache-Control "public, max-age=60";
    try_files $uri =404;
  }
}

server {
  listen 80;
  server_name
    mcp.universal-life-protocol.com
    mcp.small.universal-life-protocol.com
    mcp.medium.universal-life-protocol.com
    mcp.large.universal-life-protocol.com;

  location /mcp {
    proxy_pass http://127.0.0.1:18787/mcp;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 120s;
  }
}
```

Enable:

```bash
ln -sf /etc/nginx/sites-available/ulp-node.conf /etc/nginx/sites-enabled/ulp-node.conf
nginx -t
systemctl reload nginx
```

TLS:

```bash
certbot --nginx -d universal-life-protocol.com -d www.universal-life-protocol.com \
  -d portal.universal-life-protocol.com -d artifact.universal-life-protocol.com -d mcp.universal-life-protocol.com
```

Run this per node with that node’s hostnames.

## MCP Runtime (Per Node)

Use localhost-only bind:

```bash
export HOST=127.0.0.1
export PORT=18787
export MCP_MAX_LOAD_PER_CPU=1.0
export MCP_MIN_FREE_MEM_MB=128
```

Start:

```bash
cd /opt/atomic-kernel
npm run -s mcp:unified:server
```

## systemd Service (Per Node)

`/etc/systemd/system/atomic-kernel-mcp.service`:

```ini
[Unit]
Description=Atomic Kernel Unified MCP
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/atomic-kernel
EnvironmentFile=/etc/atomic-kernel/node.env
ExecStart=/usr/bin/npm run -s mcp:unified:server
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
```

Apply:

```bash
mkdir -p /etc/atomic-kernel
cat >/etc/atomic-kernel/node.env <<'EOF'
HOST=127.0.0.1
PORT=18787
MCP_MAX_LOAD_PER_CPU=1.0
MCP_MIN_FREE_MEM_MB=128
EOF

systemctl daemon-reload
systemctl enable atomic-kernel-mcp
systemctl restart atomic-kernel-mcp
systemctl status atomic-kernel-mcp --no-pager
```

## Semantic Parity Checks Across Capacity Tiers

All MCP tiers must preserve semantics and shape for identical payloads.

Check basic endpoint health:

```bash
curl -i https://mcp.small.universal-life-protocol.com/mcp
curl -i https://mcp.medium.universal-life-protocol.com/mcp
curl -i https://mcp.large.universal-life-protocol.com/mcp
```

Check immersive static parity:

```bash
curl -fsSL https://portal.small.universal-life-protocol.com/docs/immersive-data/cues/ch_1d1b90232e14.cinematic_cues.v1.json | sha256sum
curl -fsSL https://portal.medium.universal-life-protocol.com/docs/immersive-data/cues/ch_1d1b90232e14.cinematic_cues.v1.json | sha256sum
curl -fsSL https://portal.large.universal-life-protocol.com/docs/immersive-data/cues/ch_1d1b90232e14.cinematic_cues.v1.json | sha256sum
```

Hashes should match.

## Operational Invariant

Capacity tier changes throughput only.
It must not change:

- control-plane schema
- tool names
- response shape
- policy behavior
- deterministic artifact digests
