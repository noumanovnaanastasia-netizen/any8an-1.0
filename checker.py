import urllib.request
import base64
import socket
import time
import re
from concurrent.futures import ThreadPoolExecutor

NORMAL_URLS = [
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://githubusercontent.com"
]

WHITELIST_URLS = [
    "https://githubusercontent.com",
    "
    "https://github.com/igareck/vpn-configs-for-russia/blob/main/WHITE-CIDR-RU-checked.txt"
]

def fetch_keys(urls):
    keys = set()
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('utf-8', errors='ignore').strip()
                if "://" not in content:
                    try:
                        content = base64.b64decode(content).decode('utf-8', errors='ignore')
                    except Exception:
                        pass
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith(("vless://", "trojan://", "ss://")):
                        keys.add(line)
        except Exception as e:
            print(f"Ошибка загрузки {url}: {e}")
    return list(keys)

def parse_host_port(key):
    try:
        match = re.search(r'@([^:/?#]+):(\d+)', key)
        if match:
            return match.group(1), int(match.group(2))
    except Exception:
        pass
    return None, None

def check_ping(key):
    host, port = parse_host_port(key)
    if not host or not port:
        return None
    start = time.time()
    try:
        with socket.create_connection((host, port), timeout=2.0):
            ping = round((time.time() - start) * 1000)
            return (ping, host, key)
    except Exception:
        return None

def get_best_keys(keys, limit=5):
    valid = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(check_ping, keys[:300])
        for res in results:
            if res:
                valid.append(res)
    
    valid.sort(key=lambda x: x[0])
    
    best = []
    seen_hosts = set()
    for ping, host, key in valid:
        if host not in seen_hosts:
            seen_hosts.add(host)
            best.append(key)
        if len(best) >= limit:
            break
    return best

def main():
    normal_raw = fetch_keys(NORMAL_URLS)
    best_normal = get_best_keys(normal_raw, limit=5)

    white_raw = fetch_keys(WHITELIST_URLS)
    best_white = get_best_keys(white_raw, limit=5)

    final_list = []
    for i, k in enumerate(best_normal, 1):
        base = k.split("#")[0]
        final_list.append(f"{base}#🌍_Обычный_{i}")
        
    for i, k in enumerate(best_white, 1):
        base = k.split("#")[0]
        final_list.append(f"{base}#🛡_Белый_список_{i}")

    result_text = "\n".join(final_list)
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(result_text)
    print(f"Готово! Сохранено ключей: {len(final_list)}")

if __name__ == "__main__":
    main()
