
## Preparation

Preparation before deployment:

- Domain name * 1
- SSL certificate * 1
- BBR Installed (optional)

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
```
edit file startup.sh:
```
docker rm -f v2ray
docker run -itd --name=v2ray \
-p 19110:443 \
-e v2ray_port='19110' \
-e v2ray_domain='<you domain>' \
-e v2ray_uuid='<UUID value>' \
-e v2ray_path='<PATH value>' \
-e v2ray_mail='<user name>' \
-v /app/v2ray/ssl/ssl.cer:/etc/nginx/ssl/ssl.cer \
-v /app/v2ray/ssl/ssl.key:/etc/nginx/ssl/ssl.key \
v2ray:latest
```

## Best Practices


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
-p 19110:443 \
-e v2ray_port='19110' \
-e v2ray_domain='v2ray.demo.com'  \
-e v2ray_uuid='d7af9bc2-67ac-4ca2-8320-93343bcb8086' \
-e v2ray_path='693f'       \
-e v2ray_mail='admin@demo.com'  \
-v /app/v2ray/ssl/:/etc/nginx/ssl  \
v2ray:latest
```

startup logs

```
$ docker logs -f --tail=200 v2ray
----------client config info------------
v2ray-core port: 19110
v2ray-core alterid: 64
v2ray-core protocol: ws
v2ray-core security: tls
v2ray-core addr: v2ray.demo.com
v2ray-core uuid: 45998eac-3949-4c7b-a3c9-bc290182f0ac
v2ray-core path: 69ff
v2ray-core encryption: aes-128-gcm
 
 
----------vmess url info------------
vmess://WwvOS6muW3ni3lrrnlmajoioLngrktZG9ja2VyLWRlbW8iLCJhZGQiOiJmZnktZG9ja2VyLmluaXQuYWMiLCJwb3J0IjoiMTg4NzgiLCJpZCI6IjQ1OTk4ZWFjLTM5NDktNGM3Yi1hM2M5LWJjMjkwMTgyZjBhYyIsImFpZCI6NjQsIm5ldCI6IndzIiwidHlwZSI6Im5vbmUiLCJob3N0IjoiIiwicGF0aCI6IjY5ZmYiLCJ0bHMiOiJ0bHMifQ==
```

