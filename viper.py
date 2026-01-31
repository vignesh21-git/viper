#!/usr/bin/env python3

"""
$Id: Viper - HTTP Load Testing Tool $

A hybrid threading + async HTTP load testing tool for authorized penetration
testing engagements. Combines multithreading with aiohttp coroutines for
high-concurrency request generation with real-time metrics.

⚠️ **Disclaimer**:
This tool is strictly for authorized penetration testing and load testing
engagements with proper client agreements. Any unauthorized usage is
prohibited and may violate applicable laws.

@author Vignesh A <vickyvignesh2102@gmail.com>
@date 2024-12-25
@version 2.0
"""

import argparse
import asyncio
import threading
import random
import aiohttp
from aiohttp_socks import ProxyConnector
from itertools import cycle
import time
import logging
import sys
import os

VERSION = "2.0"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
]

REFERERS = [
    "http://www.google.com/?q=",
    "http://www.usatoday.com/search/results?q=",
    "http://engadget.search.aol.com/search?q=",
    "http://www.bing.com/search?q=",
    "http://www.yahoo.com/search?p=",
    "http://duckduckgo.com/?q=",
]

PROXY_LIST = []
PROXY_CYCLE = None

BANNER = r"""

 ██╗   ██╗██╗██████╗ ███████╗██████╗
 ██║   ██║██║██╔══██╗██╔════╝██╔══██╗
 ██║   ██║██║██████╔╝█████╗  ██████╔╝
 ╚██╗ ██╔╝██║██╔═══╝ ██╔══╝  ██╔══██╗
  ╚████╔╝ ██║██║     ███████╗██║  ██║
   ╚═══╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
"""


class Metrics:
    """Thread-safe metrics collector."""

    def __init__(self):
        self._lock = threading.Lock()
        self.total_sent = 0
        self.success = 0
        self.failed = 0
        self.bytes_sent = 0
        self.status_codes = {}
        self.active_threads = 0
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def record_request(self, status_code, payload_size):
        with self._lock:
            self.total_sent += 1
            self.bytes_sent += payload_size
            bucket = f"{status_code // 100}xx"
            self.status_codes[bucket] = self.status_codes.get(bucket, 0) + 1
            if 200 <= status_code < 400:
                self.success += 1
            else:
                self.failed += 1

    def record_failure(self):
        with self._lock:
            self.total_sent += 1
            self.failed += 1
            self.status_codes["err"] = self.status_codes.get("err", 0) + 1

    def thread_started(self):
        with self._lock:
            self.active_threads += 1

    def thread_finished(self):
        with self._lock:
            self.active_threads -= 1

    def snapshot(self):
        with self._lock:
            elapsed = time.time() - self.start_time if self.start_time else 0
            rps = self.total_sent / elapsed if elapsed > 0 else 0
            return {
                "elapsed": elapsed,
                "total": self.total_sent,
                "success": self.success,
                "failed": self.failed,
                "bytes": self.bytes_sent,
                "rps": rps,
                "codes": dict(self.status_codes),
                "threads": self.active_threads,
            }


metrics = Metrics()


def load_proxies(proxy_file):
    global PROXY_CYCLE
    with open(proxy_file, "r") as f:
        PROXY_LIST.extend([line.strip() for line in f if line.strip()])
    if PROXY_LIST:
        PROXY_CYCLE = cycle(PROXY_LIST)
    else:
        while True:
            choice = input("[WARNING] No proxies found in the file. Do you want to proceed without proxies? (Y/N): ").strip().lower()
            if choice == 'y':
                print("[INFO] Proceeding without proxies...")
                break
            elif choice == 'n':
                print("[INFO] Exiting as per user request.")
                exit(0)
            else:
                print("[ERROR] Invalid choice. Please enter Y or N.")


def _make_headers():
    """Generate fresh randomized headers for each request."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": random.choice(REFERERS),
        "Connection": "keep-alive",
        f"X-Custom-Header-{random.randint(1, 1000)}": "A" * random.randint(100, 1000),
    }


async def send_request(session, url, payload):
    """Send a single async HTTP POST request."""
    try:
        await asyncio.sleep(random.uniform(0.01, 0.3))
        headers = _make_headers()
        payload_size = len(payload)

        async with session.post(url, headers=headers, data=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            await resp.read()
            metrics.record_request(resp.status, payload_size)
            logging.debug(f"Request to {url} — {resp.status}")

    except Exception as e:
        metrics.record_failure()
        logging.debug(f"Request failed: {e}")


async def coroutine_worker(session, url, num_requests, payload, infinite=False):
    """A single coroutine worker that sends num_requests sequentially."""
    count = 0
    while infinite or count < num_requests:
        await send_request(session, url, payload)
        count += 1


async def thread_main(url, num_coroutines, requests_per_coroutine, proxy=None, infinite=False):
    """Entry point for each thread's asyncio event loop.

    Spawns num_coroutines concurrent workers, each sending requests_per_coroutine requests.
    If a proxy is provided (socks5://, http://, https://), routes all traffic through it.
    """
    payload = "A" * random.randint(5_000, 10_000)

    if proxy:
        connector = ProxyConnector.from_url(proxy, limit=0)
    else:
        connector = aiohttp.TCPConnector(limit=0, enable_cleanup_closed=True)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            coroutine_worker(session, url, requests_per_coroutine, payload, infinite)
            for _ in range(num_coroutines)
        ]
        await asyncio.gather(*tasks)


def thread_function(url, num_coroutines, requests_per_coroutine, proxy=None, infinite=False):
    """Thread wrapper — runs the async event loop."""
    metrics.thread_started()
    try:
        asyncio.run(thread_main(url, num_coroutines, requests_per_coroutine, proxy, infinite))
    finally:
        metrics.thread_finished()


def _format_bytes(b):
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def _format_time(secs):
    m, s = divmod(int(secs), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _bar(pct, width=20):
    filled = int(width * pct / 100)
    return "\u2588" * filled + "\u2591" * (width - filled)


def dashboard_thread(url, stop_event):
    """Live-updating terminal metrics dashboard."""
    while not stop_event.is_set():
        snap = metrics.snapshot()
        total = snap["total"] or 1
        success_pct = snap["success"] / total * 100
        failed_pct = snap["failed"] / total * 100

        lines = []
        lines.append("")
        lines.append(" \033[36m\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\033[0m")
        lines.append(f"  \033[1;35mVIPER v{VERSION}\033[0m  \033[2mTarget:\033[0m \033[33m{url}\033[0m")
        lines.append(" \033[36m\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\033[0m")
        lines.append(f"  \033[37mElapsed     :\033[0m  {_format_time(snap['elapsed'])}")
        lines.append(f"  \033[37mThreads     :\033[0m  \033[1;32m{snap['threads']}\033[0m active")
        lines.append(f"  \033[37mReq/sec     :\033[0m  \033[1;33m{snap['rps']:,.1f}\033[0m")
        lines.append(" \033[36m\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\033[0m")
        lines.append(f"  \033[37mTotal Sent   :\033[0m  \033[1m{snap['total']:,}\033[0m")
        lines.append(f"  \033[32mSuccess      :\033[0m  {snap['success']:,}   ({success_pct:.1f}%)")
        lines.append(f"  \033[31mFailed       :\033[0m  {snap['failed']:,}   ({failed_pct:.1f}%)")
        lines.append(f"  \033[37mData Sent    :\033[0m  {_format_bytes(snap['bytes'])}")
        lines.append(" \033[36m\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\033[0m")
        lines.append("  \033[1mStatus Codes:\033[0m")

        code_order = ["2xx", "3xx", "4xx", "5xx", "err"]
        code_colors = {"2xx": "32", "3xx": "36", "4xx": "33", "5xx": "31", "err": "91"}
        for code in code_order:
            count = snap["codes"].get(code, 0)
            if count == 0:
                continue
            pct = count / total * 100
            color = code_colors.get(code, "37")
            lines.append(f"    \033[{color}m{code}\033[0m {_bar(pct)} \033[1m{pct:5.1f}%\033[0m  ({count:,})")

        lines.append(" \033[36m\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\033[0m")
        lines.append("  \033[2mCtrl+C to stop\033[0m")
        lines.append("")

        # Move cursor to top and redraw
        output = f"\033[H\033[J" + "\n".join(lines)
        sys.stdout.write(output)
        sys.stdout.flush()

        stop_event.wait(0.5)


def main():
    parser = argparse.ArgumentParser(
        description="Viper - HTTP Load Testing Tool for Authorized Pentesting",
        epilog="Use only with proper authorization and client agreements.",
    )
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--threads", type=int, default=20, help="Number of threads (default: 20)")
    parser.add_argument("--coroutines", type=int, default=100, help="Coroutines per thread (default: 100)")
    parser.add_argument("--requests", type=int, default=500, help="Requests per coroutine (default: 500)")
    parser.add_argument("--proxy-file", help="File containing proxy addresses, one per line (socks5://host:port, http://host:port)")
    parser.add_argument("--infinite", action="store_true", help="Run indefinitely until Ctrl+C")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose per-request logging")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

    print(f"\033[35m{BANNER}\033[0m")
    print(f"  \033[1mTarget :\033[0m {args.url}")
    print(f"  \033[1mThreads:\033[0m {args.threads}  |  \033[1mCoroutines/thread:\033[0m {args.coroutines}  |  \033[1mReqs/coroutine:\033[0m {args.requests}")
    total = args.threads * args.coroutines * args.requests
    if not args.infinite:
        print(f"  \033[1mTotal  :\033[0m {total:,} requests")
    else:
        print(f"  \033[1mMode   :\033[0m Infinite (Ctrl+C to stop)")
    print()

    if args.proxy_file:
        load_proxies(args.proxy_file)
        if PROXY_LIST:
            print(f"  \033[1mProxies:\033[0m {len(PROXY_LIST)} loaded\n")

    time.sleep(1.5)

    metrics.start()
    stop_event = threading.Event()

    # Start dashboard
    dash = threading.Thread(target=dashboard_thread, args=(args.url, stop_event), daemon=True)
    dash.start()

    threads = []
    for i in range(args.threads):
        proxy = next(PROXY_CYCLE) if PROXY_CYCLE else None

        t = threading.Thread(
            target=thread_function,
            args=(args.url, args.coroutines, args.requests, proxy, args.infinite),
        )
        threads.append(t)
        t.start()

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        time.sleep(0.6)

        # Final summary
        snap = metrics.snapshot()
        total = snap["total"] or 1
        print("\033[H\033[J")
        print(f"\033[35m{BANNER}\033[0m")
        print(" \033[1;36m FINAL RESULTS\033[0m")
        print(" \033[36m\u2550" * 50 + "\033[0m")
        print(f"  Target       :  {args.url}")
        print(f"  Duration     :  {_format_time(snap['elapsed'])}")
        print(f"  Total Sent   :  {snap['total']:,}")
        print(f"  Success      :  \033[32m{snap['success']:,}\033[0m  ({snap['success']/total*100:.1f}%)")
        print(f"  Failed       :  \033[31m{snap['failed']:,}\033[0m  ({snap['failed']/total*100:.1f}%)")
        print(f"  Avg Req/sec  :  \033[33m{snap['rps']:,.1f}\033[0m")
        print(f"  Data Sent    :  {_format_bytes(snap['bytes'])}")
        print(" \033[36m\u2500" * 50 + "\033[0m")
        for code in ["2xx", "3xx", "4xx", "5xx", "err"]:
            count = snap["codes"].get(code, 0)
            if count:
                pct = count / total * 100
                print(f"    {code}  {_bar(pct)}  {pct:5.1f}%  ({count:,})")
        print(" \033[36m\u2550" * 50 + "\033[0m")
        print()


if __name__ == "__main__":
    main()
