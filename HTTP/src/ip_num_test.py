import concurrent
from concurrent.futures import ThreadPoolExecutor

import requests

ips = set()


def ac_ip(i):
    print(i)
    r = requests.get("http://myip.ipip.net", proxies={"http": "http://127.0.0.1:8081"})
    ips.add(r.text)


with ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(ac_ip, list(range(200)))

print("".join(ips))
print(len(ips))
