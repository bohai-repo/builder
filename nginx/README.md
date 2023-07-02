## 启动

```
docker pull registry.ap-northeast-1.aliyuncs.com/bohai_repo/nginx:1.21.1
docker rm -f nginx
docker run -itd --name=nginx \
--restart=always \
-p 80:80 \
-p 443:443 \
-v /app/nginx/logs/:/app/nginx/logs/ \
-v /app/nginx/conf:/app/nginx/conf.d/ \
registry.ap-northeast-1.aliyuncs.com/bohai_repo/nginx:1.21.1
```

## 示例

/app/nginx/conf/default.conf

```
server {
    listen 80;
    server_name localhost;

    add_header Strict-Transport-Security "max-age=31536000";
    error_page 497  https://$host$request_uri;

    location / {
        index index.html index.htm;
        root /app/nginx/html/;
    }
}
```

```
# curl 127.0.0.1
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```