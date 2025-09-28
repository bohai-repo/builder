## Assistant

ops_transfer_docker

```
- 作用：转存海外镜像仓库到阿里云镜像仓库
- 输入：帮我下载镜像: nginx:latest
- 输出：registry.cn-hangzhou.aliyuncs.com/bohai_repo/nginx:latest
```

ops_transfer_downloadfile

```
- 作用：转存海外地址的文件链接加速国内下载
- 输入：帮我下载文件: https://xxx.com/xxx
- 输出：请访问 https://download.init.ac/files/xxx 进行下载
```

ops_transfer_localfile

```
- 作用：将用户输入的文件上传至https://transfer.init.ac/有效期保持一天
- 输入：#file
- 输出: 请访问 https://transfer.init.ac/xxx/xxx 进行下载
```