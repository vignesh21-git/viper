# viper.py - Hybrid HTTP DoS Tool

## **What is viper.py?**

`viper.py` is a versatile and powerful HTTP Denial of Service (DoS) tool designed for stress testing web servers. It combines **multithreading** and **coroutines** to deliver high-performance attacks, targeting **Layer 7 (Application Layer)** vulnerabilities. It supports features like randomized headers, proxy integration, and dynamic request generation to mimic legitimate traffic, making it harder to detect.

---

## **How Does viper.py Work?**

1. **Multiple Threads and Coroutines:**
   - Threads manage coroutine loops for sending a high volume of asynchronous HTTP requests.
2. **Randomized Request Parameters:**   
   - User-Agent, Referer, and query strings are randomized to simulate legitimate traffic.
3. **Proxy Support:**
   - Allows testing with multiple SOCKS5 proxies to mask source IPs.
4. **Dynamic Adjustments:**
   - Monitors server responses and adjusts request rates or concurrency dynamically.
5. **Exhausts Server Resources:**
   - Overwhelms the web server by consuming CPU, memory, and thread pools, leading to denial of service.

---

## **How to Install and Run viper.py**

### **Installation**

Clone the repository from GitHub:
```bash
git clone https://github.com/your-repo/viper.git
cd viper
```

Ensure you have Python 3 installed. Install the required dependencies using:
```bash
pip3 install -r requirements.txt
```

---

### **Running viper.py**

To run a basic attack:
```bash
python3 viper.py --url example.com --threads 10 --coroutines 50 --requests 20
```

---

### **SOCKS5 Proxy Support**

If you plan on using SOCKS5 proxies, ensure you have the `PySocks` library installed:
```bash
pip3 install PySocks
```

You can then use the `--proxy-file` option to specify a file containing proxy addresses:
```bash
python3 viper.py --url example.com --threads 10 --coroutines 50 --requests 20 --proxy-file proxies.txt
```

The proxy file should contain one proxy address per line, in the format:
```
127.0.0.1:8080
192.168.1.100:1080
```

---

## **Configuration Options**

`viper.py` provides various command-line arguments to customize the attack:

| Argument           | Description                                   | Default            |
|--------------------|-----------------------------------------------|--------------------|
| `--url`           | Target URL for the attack                    | Required           |
| `--threads`       | Number of threads to spawn                   | 10                 |
| `--coroutines`    | Number of coroutines per thread              | 50                 |
| `--requests`      | Number of requests per coroutine             | 20                 |
| `--proxy-file`    | File containing proxy addresses              | None               |
| `--useragents`    | File with custom User-Agent strings          | Randomized built-in|
| `--sleeptime`     | Time to sleep between requests (seconds)     | 0.1-0.5 (random)   |
| `--verbose`       | Increases logging output                     | Off                |

---

## **Example Commands**

### **Basic Usage**
Run the tool against a target URL:
```bash
python3 viper.py --url example.com --threads 15 --coroutines 100 --requests 25
```

### **Using Proxies**
Run with SOCKS5 proxies from a file:
```bash
python3 viper.py --url example.com --threads 10 --coroutines 50 --requests 20 --proxy-file proxies.txt
```

### **Verbose Mode**
Enable detailed logging:
```bash
python3 viper.py --url example.com --threads 10 --verbose
```

---

## **Disclaimer**

⚠️ **Caution:** This tool is intended for testing **your own servers** or those you have explicit permission to test. Unauthorized use against third-party systems is illegal and unethical. Always ensure you have proper authorization before conducting any stress tests.
