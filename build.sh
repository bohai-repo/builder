#!/usr/bin/env bash

build_app=$1
alias_app=$2
build_version=$3
build_report="registry.cn-hangzhou.aliyuncs.com/bohai_repo"

function envfile() {
  echo "start build: ${build_report}/${alias_app}:${build_version}"
  echo "-------------------"
}

function frpc() {
    cd ./frpc
    sed -i "s/version_key/$build_version/g" Dockerfile
    docker build . -t ${build_report}/${alias_app}:${build_version}
    docker push ${build_report}/${alias_app}:${build_version}
}

function main() {
    echo "     "
    envfile
}

main;${build_app}


