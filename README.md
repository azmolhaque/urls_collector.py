# 🌐 urls_collector.py

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-yellow)

> Collects historical and crawled URLs for a list of live hosts, de-duplicates them, checks which are still alive, and filters down to the **signal-rich** ones (parameters, API paths, auth/redirect/token endpoints) worth a closer look.

This is the natural next step after [`subdomain_enum.py`](https://github.com/azmolhaque/subdomain_enum.py): feed it the live-hosts list and it builds your URL attack surface.

---

## ⚠️ Authorized use only

Use this only against hosts you own or are **explicitly authorized** to test. See [`LICENSE`](LICENSE).

---

## Pipeline

```
subdomains_alive.txt
   │
   ├─ katana        ┐
   ├─ waybackurls   ├─ combine + sort -u ─► httpx (alive) ─► regex filter ─► signal_urls.txt.gz
   └─ gau           ┘
```

The regex filter keeps URLs matching high-signal patterns: query parameters, `/api/`, `.php`/`.aspx`, `login`/`auth`/`token`, `redirect`/`callback`, `/config`, and `.js`.

## Requirements

Pure Python (standard library), but it depends on these external tools being installed and on your `PATH`:

| Tool | Purpose |
| :--- | :--- |
| [katana](https://github.com/projectdiscovery/katana) | Active crawling |
| [waybackurls](https://github.com/tomnomnom/waybackurls) | Wayback Machine URLs |
| [gau](https://github.com/lc/gau) | URLs from Wayback / Common Crawl / OTX / URLScan |
| [httpx](https://github.com/projectdiscovery/httpx) | Liveness check |

## Usage

```bash
# Input: one live host per line (e.g. the output of subdomain_enum.py)
cp /path/to/subdomains_alive.txt .
python3 urls_collector.py
```

Result: `output/signal_urls.txt.gz` — a compressed, de-duplicated list of live, signal-rich URLs.

## License

MIT — see [`LICENSE`](LICENSE).
