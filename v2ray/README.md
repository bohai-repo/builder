
## Preparation

Preparation before deployment:

- Domain name * 1
- SSL certificate * 1
- BBR Installed (optional)
- Suggest using port 443 (optional)

## Build

```
docker build . -t v2ray:latest
```

## Launch

Generate UUID

```
cat /proc/sys/kernel/random/uuid
```

Generate PATH

```
cat /dev/urandom | head -1 | md5sum | head -c 4
```

Launch

```
mkdir -p /app/v2ray/ssl && cd /app/v2ray/

vim startup.sh

docker rm -f v2ray
docker run -itd --name=v2ray -p 443:443 \
-e v2ray_domain='443'              \
-e v2ray_domain='<you domain>'     \
-e v2ray_uuid='<UUID value>'       \
-e v2ray_path='<PATH value>'       \
-e v2ray_email='<you email addr>'  \
-v /app/v2ray/ssl/ssl.cer:/etc/nginx/ssl/ssl.cer  \
-v /app/v2ray/ssl/ssl.key:/etc/nginx/ssl/ssl.key  \
v2ray:latest
```

Best Practices:

```
$ tree /app

/app/
└── v2ray
    ├── ssl
    │   ├── ssl.cer
    │   └── ssl.key
    └── startup.sh
```


```
$ cat startup.sh

docker rm -f v2ray
docker run -itd --name=v2ray \
-p 443:443 \
-e v2ray_port='443' \
-e v2ray_domain='v2ray.demo.com'  \
-e v2ray_uuid='d7af9bc2-67ac-4ca2-8320-93343bcb8086' \
-e v2ray_path='693f'       \
-e v2ray_email='admin@demo.com'  \
-v /app/v2ray/ssl/:/etc/nginx/ssl  \
v2ray:latest
```