## 描述

用于配合 [樱花面板](https://github.com/ZeroDream-CN/SakuraPanel) 的frpc客户端

具有以下特点：

- 自动拉取配置
- 热加载新配置
- 容器部署启动

## 构建

```shell
docker build . -t frpc:0.28.2-auto
```

## 启动

envfile

```ini
# 配置更新间隔(秒)
exec_sec='60'
# 用户名
appId='xxx'
# 用户密码
appSecretKey='xxxx'
# 节点ID
appServerId='1'
# 请求重试次数
request_trynum='3'
# 请求超时时间(秒)
request_timeout='15'
# 请求面板地址
appurl='https://nat.itan90.cn'
```

```
docker rm -f frpc-auto
docker run -itd --restart=always --name=frpc-auto --env-file ./envfile frpc:0.28.2-auto
```

## 日志

```shell
docker logs -f --tail=200 frpc-auto

2023/05/08 13:10:02 [I] starting auto get conf
2023/05/08 13:10:03 [I] conf has been get
2023/05/08 13:10:03 [I] [admin_api.go:41] Http request [/api/reload]
2023/05/08 13:10:03 [I] [admin_api.go:81] success reload conf
2023/05/08 13:10:03 [I] [admin_api.go:43] Http response [/api/reload], code [200]
2023/05/08 13:10:03 [I] success reload conf
```