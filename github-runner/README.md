## Building the container

`docker build -t github-runner .`

## Features

* Repository runners
* Organizational runners
* Labels
* Graceful shutdown
* Supports arm64 and amd64
* Support for installing additional debian packages
* Auto-update after the release of a new version

## Examples

Register a runner to a repository.

```sh
docker run -itd --name github-runner \
     -e REGIST_TYPE='personal' \
     -e GITHUB_OWNER=username-or-organization \
     -e GITHUB_REPOSITORY=my-repository \
     -e GITHUB_PAT=[PAT] \
     -v /var/run/docker.sock:/var/run/docker.sock \
     registry.ap-northeast-1.aliyuncs.com/bohai_repo/github-runner:2.304.0
```

Register a runner with github token.

```sh
docker run -itd --name github-runner \
     -e GITHUB_OWNER=username-or-organization \
     -e GITHUB_REPOSITORY=my-repository \
     -e GITHUB_TOKEN=[github.token] \
     -v /var/run/docker.sock:/var/run/docker.sock \
     registry.ap-northeast-1.aliyuncs.com/bohai_repo/github-runner:2.304.0
```

Create an organization-wide runner.

```sh
docker run -itd --name github-runner \
    -e REGIST_TYPE='organizational' \
    -e GITHUB_ORG_NAME=username-or-organization \
    -e GITHUB_PAT=[PAT] \
     -v /var/run/docker.sock:/var/run/docker.sock \
    registry.ap-northeast-1.aliyuncs.com/bohai_repo/github-runner:2.304.0
```

Set labels on the runner.

```sh
add env:

    -e RUNNER_LABELS='[you labels]' \
```

Use arm64 CPU

```sh
change image:

registry.ap-northeast-1.aliyuncs.com/bohai_repo/github-runner-arm64:2.304.0
```

Install additional tools on the runner.

```sh
docker run -itd --name github-runner \
    -e GITHUB_OWNER=username-or-organization \
    -e GITHUB_REPOSITORY=my-repository \
    -e GITHUB_PAT=[PAT] \
    -e ADDITIONAL_PACKAGES=firefox-esr,chromium \
     -v /var/run/docker.sock:/var/run/docker.sock \
    registry.ap-northeast-1.aliyuncs.com/bohai_repo/github-runner:2.304.0
```

Running GitHub Actions on Kubernetes

```shell
kubectl create ns actions-builder
kubectl apply -f deployment.yml -n actions-builder
```

```shell
kubectl get po -n actions-builder

NAME                                      READY   STATUS    RESTARTS   AGE
github-actions-builder-68f989b844-2gf7z   1/1     Running   0          70s
github-actions-builder-68f989b844-2lnv6   1/1     Running   0          70s
github-actions-builder-68f989b844-8zhpl   1/1     Running   0          70s
github-actions-builder-68f989b844-fzmwm   1/1     Running   0          66s
github-actions-builder-68f989b844-n95gj   1/1     Running   0          65s
github-actions-builder-68f989b844-npmvd   1/1     Running   0          67s
github-actions-builder-68f989b844-p9l9b   1/1     Running   0          70s
github-actions-builder-68f989b844-s6gvj   1/1     Running   0          66s
github-actions-builder-68f989b844-vhfhq   1/1     Running   0          70s
github-actions-builder-68f989b844-vrhjh   1/1     Running   0          65s
```

![](https://resource.static.tencent.itan90.cn/mac_pic/2023-05-08/PihTM1.png)