
## preparation

Preparation before deployment:

- Docker installed
- Linux for Centos7
- Can use port 443
- Domain name * 1
- SSL certificate * 1

## Build

```
docker build . -t v2ray:latest
```

## launch

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
-e v2ray_uuid='<UUID value>'       \
-e v2ray_path='<PATH value>'       \
-e v2ray_domain='<you domain>'     \
-e v2ray_email='<you email addr>'  \
-v /app/v2ray/ssl/:/etc/nginx/ssl  \
v2ray:latest
```