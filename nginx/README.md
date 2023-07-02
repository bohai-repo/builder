## 启动

```
docker run -itd --name=nginx \
--restart=always \
-p 80:80 \
-p 443:443 \
-v /app/nginx/conf:/app/nginx/conf.d/
```
