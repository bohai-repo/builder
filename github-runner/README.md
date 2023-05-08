## Building the container

`docker build -t github-runner .`

## Features

* Repository runners
* Organizational runners
* Labels
* Graceful shutdown
* Support for installing additional debian packages
* Auto-update after the release of a new version

## Examples

Register a runner to a repository.

```sh
docker run --name github-runner \
     -e GITHUB_OWNER=username-or-organization \
     -e GITHUB_REPOSITORY=my-repository \
     -e GITHUB_PAT=[PAT] \
     registry.ap-northeast-1.aliyuncs.com/bohai_repo/github-runner:2.278.0
```

Register a runner with github token.

```sh
docker run --name github-runner \
     -e GITHUB_OWNER=username-or-organization \
     -e GITHUB_REPOSITORY=my-repository \
     -e GITHUB_TOKEN=[github.token] \
     registry.ap-northeast-1.aliyuncs.com/bohai_repo/github-runner:2.278.0
```

Create an organization-wide runner.

```sh
docker run --name github-runner \
    -e GITHUB_OWNER=username-or-organization \
    -e GITHUB_PAT=[PAT] \
    registry.ap-northeast-1.aliyuncs.com/bohai_repo/github-runner:2.278.0
```

Set labels on the runner.

```sh
docker run --name github-runner \
    -e GITHUB_OWNER=username-or-organization \
    -e GITHUB_REPOSITORY=my-repository \
    -e GITHUB_PAT=[PAT] \
    -e RUNNER_LABELS=comma,separated,labels \
    registry.ap-northeast-1.aliyuncs.com/bohai_repo/github-runner:2.278.0
```

Install additional tools on the runner.

```sh
docker run --name github-runner \
    -e GITHUB_OWNER=username-or-organization \
    -e GITHUB_REPOSITORY=my-repository \
    -e GITHUB_PAT=[PAT] \
    -e ADDITIONAL_PACKAGES=firefox-esr,chromium \
    registry.ap-northeast-1.aliyuncs.com/bohai_repo/github-runner:2.278.0
```
