## 适用于多场景的Jenkins Slave

- 可使用kubectl
- 可使用docker
- 适用arm64/amd64多架构

使用

```
docker rm -f jenkins-slave
docker run --init -d --name=jenkins-slave \
  -v /root/.ssh:/root/.ssh \
  -v /root/.kube:/root/.kube \
  -v $(which docker):/usr/bin/docker \
  -v $(which kubectl):/usr/bin/kubectl \
  -v /app/jenkins/agent:/home/jenkins/agent \
  -v /var/run/docker.sock:/var/run/docker.sock \
  registry.ap-northeast-1.aliyuncs.com/bohai_repo/jenkins-slave-amd64:1.0.0-SNAPSHOT \
  -url http://<jenkins-server:port> \
  -workDir=/home/jenkins/agent <secret> <agent name>
```

镜像列表

|AMD64|registry.ap-northeast-1.aliyuncs.com/bohai_repo/jenkins-slave-amd64:1.0.0-SNAPSHOT|
|ARM64|registry.ap-northeast-1.aliyuncs.com/bohai_repo/jenkins-slave-arm64:1.0.0-SNAPSHOT|
