# fc-proxy
将阿里云函数的机器集群作为代理池.

本项目灵感和部分代码来自 https://github.com/shimmeris/SCFProxy, 主要将项目从腾讯云平台迁移到阿里云函数.

阿里云函数用：server.py

本地代理：
mitmdump -s client.py -p 9998 --no-http2 -v --listen-host 127.0.0.1

远程代理：
mitmdump -s client.py -p 9998 --no-http2 --set block_global=false -v --listen-host 0.0.0.0

远程代理+账号密码认证：
mitmdump -s client.py -p 9998 --no-http2 --set block_global=false -v --proxyauth 123a:123a --listen-host 0.0.0.0 

linux 证书配置
cp ~/.mitmproxy/mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
update-ca-certificates

docker 证书配置

docker cp /root/.mitmproxy/mitmproxy-ca-cert.pem 3f7049bba817:/usr/local/share/ca-certificates/mitmproxy.crt && docker exec -it 3f7049bba817 /bin/bash -i update-ca-certificates 

curl 去验证是否认证成功
curl -x http://123a:123a@ip:8888 http://ip.me

## 原理
详细原理参见文章[浅谈云函数的利用面](https://xz.aliyun.com/t/9502)

我的博客[相关链接](https://blog.lyc8503.net/post/sfc-proxy-pool/)
