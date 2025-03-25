## 编译

```shell
# 修改基础镜像的CPU平台
sh build.sh

# 构建并运行
docker build -t registry.cn-hangzhou.aliyuncs.com/bohai_repo/remote-download-service:1.0.0-SNAPSHOT .
docker rm -f remote-download-service
docker run -itd --name remote-download-service \
-p 8888:80 \
-e USE_HTTPS=false \
-e SERVER_NAME=138.2.87.251:8888 \
-e PASSWORD=123456 \
-v /data/remote-download-service/data:/app/remote-download-service/files \
registry.cn-hangzhou.aliyuncs.com/bohai_repo/remote-download-service:1.0.0-SNAPSHOT
docker logs -f --tail=200 remote-download-service
```

## 日志

```
[2024-9-23 15:18][INIT] remote-download-service started
[2024-9-23 15:18][INIT] service monitor:          http://172.17.0.15:8080/metrics
[2024-9-23 15:18][INIT] service health check:     http://172.17.0.15:8080/health
```