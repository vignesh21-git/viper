# Viper - HTTP Load Testing Tool

A hybrid threading + async HTTP load testing tool built for authorized penetration testing engagements. Combines multithreading with `aiohttp` coroutines for high-concurrency request generation, with a real-time terminal metrics dashboard.

---

## How It Works

1. **Threads + Async Coroutines:** Each thread runs its own asyncio event loop with N concurrent coroutines, all sharing an `aiohttp.ClientSession` for connection pooling.
2. **Randomized Headers:** User-Agent, Referer, and custom headers are randomized per request.
3. **Proxy Support:** Routes traffic through SOCKS5 or HTTP proxies via `aiohttp-socks`. Proxies are distributed round-robin across threads.
4. **Live Dashboard:** Real-time terminal display showing req/sec, success/fail rates, status code distribution with ASCII bar charts, and data sent.

---

## Installation

```bash
git clone https://github.com/vigneshka/viper.git
cd viper
pip3 install -r requirements.txt
```

### Dependencies

- `aiohttp` — async HTTP client
- `aiohttp-socks` — SOCKS5/HTTP proxy support for aiohttp

---

## Usage

```bash
python3 viper.py --url <target_url> [options]
```

### Options

| Argument | Description | Default |
|---|---|---|
| `--url` | Target URL (required) | — |
| `--threads` | Number of threads | 20 |
| `--coroutines` | Coroutines per thread | 100 |
| `--requests` | Requests per coroutine | 500 |
| `--proxy-file` | File with proxy addresses (one per line) | None |
| `--infinite` | Run indefinitely until Ctrl+C | Off |
| `--verbose` | Enable per-request debug logging | Off |

### Examples

```bash
# Basic run with defaults (20 threads × 100 coroutines × 500 requests = 1M requests)
python3 viper.py --url http://target.com

# Custom concurrency
python3 viper.py --url http://target.com --threads 10 --coroutines 50 --requests 100

# With SOCKS5 proxies
python3 viper.py --url http://target.com --proxy-file proxies.txt

# Infinite mode with verbose logging
python3 viper.py --url http://target.com --infinite --verbose
```

---

## Proxy File Format

One proxy per line with scheme prefix:

```
socks5://127.0.0.1:1080
socks5://192.168.1.100:1080
http://10.0.0.1:8080
https://proxy.example.com:3128
```

If the proxy file exists but is empty, the tool will prompt whether to continue without proxies.

---

## Live Dashboard

During execution, Viper displays a live-updating terminal dashboard:

```
 ══════════════════════════════════════════════════
  VIPER v2.0  Target: http://target.com
 ══════════════════════════════════════════════════
  Elapsed     :  00:01:23
  Threads     :  20 active
  Req/sec     :  1,247.3
 ──────────────────────────────────────────────────
  Total Sent   :  103,284
  Success      :  98,412   (95.3%)
  Failed       :  4,872    (4.7%)
  Data Sent    :  847.2 MB
 ──────────────────────────────────────────────────
  Status Codes:
    2xx ████████████████████░░░░  82.1%  (84,802)
    4xx ██░░░░░░░░░░░░░░░░░░░░░░  10.0%  (10,328)
    5xx █░░░░░░░░░░░░░░░░░░░░░░░   4.7%  (4,872)
 ══════════════════════════════════════════════════
  Ctrl+C to stop
```

A final summary with totals is printed on exit.

---

## Disclaimer

This tool is strictly for **authorized penetration testing and load testing engagements** with proper client agreements. Any unauthorized usage is prohibited and may violate applicable laws. Always ensure you have written authorization before running this tool against any target.
