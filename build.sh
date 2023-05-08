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
    apt-get install wget -y
    cd ./github-runner
    export docker_version='20.10.7'
    wget https://github.com/actions/runner/releases/download/v${build_version}/actions-runner-linux-arm64-${build_version}.tar.gz
    tar xzf actions-runner-linux-arm64-${build_version}.tar.gz && rm -rf actions-runner-linux-arm64-${build_version}.tar.gz
    ls -la && pwd
    sed -i '3,9d' ./config.sh && sed -i '3,8d' ./run.sh
#    tar -zcf actions-runner-linux-arm64-2.304.0.tar.gz *
#    sed -i "s/docker_version/${docker_version}/g" Dockerfile
#    sed -i "s/version_key/$build_version/g" Dockerfile
#    docker build . -t ${build_report}/${alias_app}:${build_version}
}

function main() {
    launch
}

main


