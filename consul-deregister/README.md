## Consul deregister

巡检consul中异常的服务节点并将其注销

### 构建

```shell
docker build . -t consul-deregister:1.0.0-SNAPSHOT
```

### 配置

config.ini

```ini
[consul_deregister]
# consul的端口
consul_port=8500
# consul的地址
consul_host=1.1.1.1
# 服务检测列表
svc_names=linux
# 服务检测时间(秒)
svc_detection_interval=300
```
### 启动

```shell
docker rm -f consul-deregister
docker run -itd --name=consul-deregister -v $PWD/config.ini:/config.ini consul-deregister:1.0.0-SNAPSHOT

```

### 查看日志

```
docker logs -f --tail=200 consul-deregister
2023-05-08 14:59:56 [INFO] request code: [200]  delete exception linux node: [localhost-192.168.60.125]
2023-05-08 14:59:56 [INFO] request code: [200]  delete exception linux node: [localhost-192.168.60.175]
2023-05-08 14:59:56 [INFO] service: linux all health
```
