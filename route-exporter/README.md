## 京东云路由器Route-exporter

获取以下信息：

- 路由器内存/CPU信息
- 路由器网络速率
- 连接设备信息

## 构建

```
docker build . -t route-exporter
```

## 启动

```shell
docker rm -f route-exporter
docker run -itd -p 8213:8213 \
--name route-exporter \
-e route_ip='路由器IP' \
-e password='后台管理密码' \
--restart=always \
registry.cn-hangzhou.aliyuncs.com/bohai_repo/route-exporter:1.0.0-SNAPSHOT
```

可通过环境变量定制参数：

```ini
# 可选配置
max_retries   # 请求失败重试次数
exporter_port # exporter的端口
timeout       # 请求超时重试间隔(单位：秒)
sleep_time    # 数据采集时间间隔(单位：秒)

# 必要配置
route_ip      # 路由器IP地址
password      # 路由器后台管理密码(通过F12浏览器抓取login接口获取)
```

![](https://resource.static.tencent.itan90.cn/mac_pic/2023-07-01/eSpurp.jpg)