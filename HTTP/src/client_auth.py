import json
import pickle
from typing import List
from random import choice
from urllib.parse import urlparse
from base64 import b64encode, b64decode

from mitmproxy import http, ctx
from mitmproxy.version import VERSION

# 兼容 mitmproxy v6/v7+
if int(VERSION[0]) > 6:
    from mitmproxy.http import Headers
else:
    from mitmproxy.net.http import Headers

# 云函数服务列表
scf_servers: List[str] = ["https://xxx.run"]
SCF_TOKEN = "Token"

# 代理账号密码
PROXY_USERNAME = "123a"
PROXY_PASSWORD = "123a"

# ========== 认证处理逻辑 ==========
def check_proxy_auth(auth_header: str) -> bool:
    if not auth_header:
        return False
    try:
        auth_type, credentials = auth_header.split(" ", 1)
        if auth_type.lower() != "basic":
            return False
        decoded = b64decode(credentials).decode()
        username, password = decoded.split(":", 1)
        return username == PROXY_USERNAME and password == PROXY_PASSWORD
    except Exception:
        return False

# ========== HTTPS CONNECT 请求认证 ==========
def http_connect(flow: http.HTTPFlow):
    auth_header = flow.request.headers.get("Proxy-Authorization")
    if not check_proxy_auth(auth_header):
        flow.response = http.Response.make(
            407,
            b"Proxy Authentication Required",
            {"Proxy-Authenticate": 'Basic realm="mitmproxy"'}
        )

# ========== HTTP 请求处理 ==========
def request(flow: http.HTTPFlow):
    # 仅对明文 HTTP 请求进行认证（HTTPS 已在 http_connect 中处理）
    if flow.request.scheme == "http":
        auth_header = flow.request.headers.get("Proxy-Authorization")
        if not check_proxy_auth(auth_header):
            flow.response = http.Response.make(
                407,
                b"Proxy Authentication Required",
                {"Proxy-Authenticate": 'Basic realm="mitmproxy"'}
            )
            return

    # 转发请求到云函数
    scf_server = choice(scf_servers)
    r = flow.request
    data = {
        "method": r.method,
        "url": r.pretty_url,
        "headers": dict(r.headers),
        "cookies": dict(r.cookies),
        "params": dict(r.query),
        "data": b64encode(r.raw_content).decode("ascii"),
    }

    flow.request = flow.request.make(
        "POST",
        url=scf_server,
        content=json.dumps(data),
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, compress",
            "Accept-Language": "en-us;q=0.8",
            "Cache-Control": "max-age=0",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Connection": "close",
            "Host": urlparse(scf_server).netloc,
            "SCF-Token": SCF_TOKEN,
        },
    )

# ========== 云函数返回响应解析 ==========
def response(flow: http.HTTPFlow):
    if flow.response.status_code != 200:
        ctx.log.warn("Cloud function error: %d" % flow.response.status_code)

    if flow.response.status_code == 401:
        flow.response.headers = Headers(content_type="text/html;charset=utf-8")
        return

    if flow.response.status_code == 433:
        flow.response.headers = Headers(content_type="text/html;charset=utf-8")
        flow.response.text = "<html><body>操作已超过云函数服务最大时间限制，可在函数配置中修改执行超时时间</body></html>"
        return

    if flow.response.status_code == 200:
        try:
            body = flow.response.content.decode("utf-8")
            resp = pickle.loads(b64decode(body))
            r = http.Response.make(
                status_code=resp.status_code,
                headers=dict(resp.headers),
                content=resp.content,
            )
            if "Content-Encoding" in resp.headers:
                r.headers["Content-Encoding"] = resp.headers["Content-Encoding"]
            flow.response = r
        except Exception as e:
            ctx.log.error(f"Failed to parse cloud response: {e}")
            flow.response = http.Response.make(
                502, b"Invalid response from cloud function"
            )
