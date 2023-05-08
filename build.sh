#!/usr/bin/env bash

build_app=$1
alias_app=$2
build_version=$3
build_report="registry.cn-hangzhou.aliyuncs.com/bohai_repo"

function launch() {
  echo "start build: ${build_report}/${alias_app}:${build_version} for $(uname -m)"
  ${build_app}
  if [[ $? == 0 ]];then
    docker push ${build_report}/${alias_app}:${build_version}
  fi
}

function frpc() {
    cd ./frpc
    sed -i "s/version_key/$build_version/g" Dockerfile
    docker build . -t ${build_report}/${alias_app}:${build_version}
}

function github-runner() {
    cd ./github-runner
    export docker_version='20.10.7'
    apt-get install wget -y
    mkdir docker && cd docker
    curl https://download.docker.com/linux/static/stable/aarch64/docker-${docker_version}.tgz --output docker-${docker_version}.tgz
    tar xzf docker-${docker_version}.tgz && cd docker && tar zcf docker.tar.gz *
    cd ../../ && mv docker/docker/docker.tar.gz ./
    mkdir build && cd build
    wget https://github.com/actions/runner/releases/download/v${build_version}/actions-runner-linux-arm64-${build_version}.tar.gz &>/dev/null
    tar xzf actions-runner-linux-arm64-${build_version}.tar.gz && rm -rf actions-runner-linux-arm64-${build_version}.tar.gz
    sed -i '3,9d' ./config.sh && sed -i '3,8d' ./run.sh
    tar -zcf actions-runner-linux-arm64-${build_version}.tar.gz *
    cd ../ && mv build/actions-runner-linux-arm64-${build_version}.tar.gz ./ && rm -rf build
    sed -i "s/docker_version/${docker_version}/g" Dockerfile
    sed -i "s/version_key/$build_version/g" Dockerfile
    build_report="registry.ap-northeast-1.aliyuncs.com/bohai_repo"
    docker build . -t ${build_report}/${alias_app}:${build_version}
}

function main() {
    launch
}

main


