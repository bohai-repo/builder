## Consul deregister

巡检consul中异常的服务节点并将其注销

### 构建

```shell
docker build . -t consul-deregister:1.0.0-SNAPSHOT
```

### 配置

```
mkdir /app/consul-deregister
vim config.ini
```

config.ini

```ini
[consul_deregister]
# consul的端口
consul_port=8500
# consul的地址
consul_host=1.1.1.1
# 服务检测列表 (多个服务以空格分割)
svc_names=linux windows
# 服务检测时间(秒)
svc_detection_interval=300
```
### 启动

```shell
vim startup.sh
```

startup.sh

```shell
docker pull registry.cn-hangzhou.aliyuncs.com/bohai_repo/consul-deregister:1.0.0-SNAPSHOT
docker rm -f consul-deregister
docker run -itd --name=consul-deregister -v $PWD/config.ini:/config.ini registry.cn-hangzhou.aliyuncs.com/bohai_repo/consul-deregister:1.0.0-SNAPSHOT
```


sh startup.sh

### 查看日志

```
docker logs -f --tail=200 consul-deregister
2023-05-08 14:59:56 [INFO] request code: [200]  delete exception linux node: [localhost-192.168.60.125]
2023-05-08 14:59:56 [INFO] request code: [200]  delete exception linux node: [localhost-192.168.60.175]
2023-05-08 14:59:56 [INFO] service: linux all health
```
