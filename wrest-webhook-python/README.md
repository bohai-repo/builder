## 简介

一个没屁用但对接了[wrest-chat](https://github.com/opentdp/wrest-chat) 方便发微信消息的一个小脚本

## 配置

wrest的`config.yml`配置中,将web的Address修改为`0.0.0.0`

```
Web:
    Address: 0.0.0.0:7600 # 监听地址，外网访问修改为 0.0.0.0:7600
```

## 启动

```
docker rm -f wrest-webhook
docker run -itd --restart=always --name wrest-webhook \
-p 8872:8872 \
-e wrest_url='http:/127.0.0.1:7600' \
registry.cn-hangzhou.aliyuncs.com/bohai_repo/wrest-webhook-python:1.0.0-SNAPSHOT
docker logs -f --tail=200 wrest-webhook
```

## 测试

```
curl "http://127.0.0.1:8872/api?receiver=你的微信ID&msg=test"
```

## 对接Server酱

打开 `https://sct.ftqq.com/forward`,进入 `通道配置` --> `其他通道` --> `自定义` --> 填入以下内容

```
{
    "url":"http://服务器公网地址:8872/api?receiver=收信群或收信人&msg={{desp}}"
}
```

- 服务器公网地址: 部署接口服务的公网地址
- receiver: 收信群聊的ID;如: xxxxx@chatroom或收信人微信ID

## 对接RSSPush

在RSSPush的任务配置的选项里,可以直接在`Sendkey`中,填入接口服务的地址,如:

```
http://服务器公网地址:8872/api?receiver=收信群或收信人
```
