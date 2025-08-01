# http.client — HTTP 协议客户端 模块要点

---

## 模块概览

- 提供直接处理 HTTP/HTTPS 底层通信的客户端 API。
- 高层模块 `urllib.request` 基于此模块实现；对于更简洁的用法，推荐使用第三方库 `requests`。
- 在不支持 WASI 的环境（如某些 WebAssembly 平台）中不可用；HTTPS 支持需在编译时启用 SSL（依赖 `ssl` 模块）。

---

## 主要类

- HTTPConnection  
  - 管理到指定主机和端口的 TCP 连接。  
  - 构造参数：`host`, `port=80`, `timeout`, `source_address`, `blocksize`。
- HTTPSConnection  
  - HTTPConnection 子类，默认端口 `443`，通过 SSL/TLS 加密通信。  
  - 额外参数：`context`（`ssl.SSLContext` 实例）、`check_hostname`、支持 ALPN/TLS 1.3。
- HTTPResponse  
  - 封装服务器响应，支持 `.status`, `.reason`, `.headers`, `.read()`, `.getheader(name)` 等方法。
- HTTPMessage  
  - 基于 `email.message.Message`，表示响应头集合。

---

## 常量与异常

- 常量  
  - `HTTP_PORT = 80`  
  - `HTTPS_PORT = 443`  
  - `responses` 字典将 HTTP 状态码映射到标准原因短语（如 `responses[404] == 'NOT FOUND'`）。
- 异常体系  
  - 基类：`HTTPException`  
  - 常见子类：`NotConnected`, `InvalidURL`, `BadStatusLine`, `IncompleteRead`, `LineTooLong`, `RemoteDisconnected` 等。

---

## 核心方法

- 一步式请求  
  - `HTTPConnection.request(method, url, body=None, headers={}, encode_chunked=False)`  
  - 紧接着调用 `getresponse()` 获取 `HTTPResponse` 实例。
- 分步发送  
  1. `putrequest(method, url, skip_host=False, skip_accept_encoding=False)`  
  2. `putheader(header, *values)`
  3. `endheaders(message_body=None, encode_chunked=False)`  
  4. `send(data)`  
- 连接控制  
  - `connect()`, `close()`, `set_tunnel(host, port, headers)`, `set_debuglevel(level)`
- 响应处理  
  - `HTTPResponse.read([amt])`, `readinto(buffer)`  
  - `getheader(name, default)`, `getheaders()`

---

## 使用示例

1. GET 请求  
   ```python
   from http.client import HTTPSConnection

   conn = HTTPSConnection("www.python.org")
   conn.request("GET", "/")
   res = conn.getresponse()
   print(res.status, res.reason)  # 200 OK
   data = res.read()
   ```

2. HEAD 请求  
   ```python
   conn.request("HEAD", "/")
   res = conn.getresponse()
   print(len(res.read()))         # 0
   ```

3. POST 请求  
   ```python
   from urllib.parse import urlencode
   from http.client import HTTPConnection

   params = urlencode({'@number':12524, '@type':'issue', '@action':'show'})
   headers = {"Content-type":"application/x-www-form-urlencoded", "Accept":"text/plain"}

   conn = HTTPConnection("bugs.python.org")
   conn.request("POST", "", params, headers)
   res = conn.getresponse()
   print(res.status, res.reason)  # 302 Found
   ```

4. PUT 请求  
   ```python
   BODY = "***filecontents***"
   conn = HTTPConnection("localhost", 8080)
   conn.request("PUT", "/file", BODY)
   res = conn.getresponse()
   print(res.status, res.reason)  # 200 OK
   ```

---

以上要点涵盖了 `http.client` 模块的核心结构、主要类与方法以及常见用法示例，可帮助快速上手底层 HTTP/HTTPS 客户端编程。