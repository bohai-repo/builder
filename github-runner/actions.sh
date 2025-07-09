#!/usr/bin/env bash

docker_version='20.10.7'
runner_version='2.304.0'

apt install -y wget
mkdir build && cd build

# 配置docker客户端
set_docker_cli() {
    echo "start download docker......"
    wget https://download.docker.com/linux/static/stable/$(uname -m)/docker-${docker_version}.tgz \
    && tar xzf docker-${docker_version}.tgz \
    && cd docker ; tar zcvf docker_cli.tar.gz * \
    && cd ../ ; mv docker/docker_cli.tar.gz ./
}

# 配置runner
set_github_runner() {
    echo "start download runner......"
    wget https://github.com/actions/runner/releases/download/v${runner_version}/actions-runner-linux-${cpu_platform}-${runner_version}.tar.gz \
    && tar xzf actions-runner-linux-${cpu_platform}-${runner_version}.tar.gz \
    # 这里删除了两个文件中判断是否 root 用户的部分
    && sed -i '3,9d' ./config.sh \
    && sed -i '3,8d' ./run.sh \
    # 重新打包
    && tar zcvf actions-runner.tar.gz *
}

# 清理遗留软件包
clean() {
    rm -rf bin docker externals run-helper* *.sh
    rm -rf docker-${docker_version}.tgz
    rm -rf actions-runner-linux-${cpu_platform}-${runner_version}.tar.gz
}

main() {
     if [ "$(uname -m)" = "x86_64" ]; then
          cpu_platform=x64
      else
        if [ "$(uname -m)" = "aarch64" ]; then
          cpu_platform=arm64
        fi
      fi

      set_docker_cli
      set_github_runner
      clean
}

main