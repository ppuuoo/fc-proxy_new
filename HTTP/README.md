# HTTP Proxy
## 安装
需 Python >= 3.8
```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## 项目配置
### 函数配置
开通阿里云函数 FC, 在你想要的地区创建 HTTP 触发器触发的云函数, 将 server.py 的内容复制到 index.py 中, 点击部署.

记录下函数的公网访问地址, 填写进 client.py 中. (建议同时修改 Token.)

可以在多个地区部署多个云函数, 同时使用多个地址.


## 客户端配置
本项目基于 mitmproxy 提供本地代理，为代理 HTTPS 流量需安装证书。
运行 `mitmdump` 命令，证书目录自动生成在在 ~/.mitmproxy 中，安装并信任。

开启代理开始运行：
```bash
mitmdump -s client.py -p 8081 --no-http2
```

如在 VPS 上运行需将 `block_global` 参数设为 false
```bash
mitmdump -s client.py -p 8081 --no-http2 --set block_global=false
```

### ip 数量
经测试，单个地区服务器 200 个请求分配 ip 数量在 50 左右。

## 限制
1. 请求与响应流量包不能大于 6M
2. 可在云函数环境配置中修改执行超时时间
3. 因云函数限制不能进行长连接，仅支持代理 HTTP 流量

## 免责声明
此工具仅供测试和教育使用，请勿用于非法目的。
