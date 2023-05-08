#!/usr/bin/env sh

build_app=$1
build_version=$2
build_report="registry.cn-hangzhou.aliyuncs.com/bohai_repo"

function envfile() {
  echo "hello"
}

function frpc() {
    cd ./${build_app}
    sed -i "s/version_key/$build_version/g" Dockerfile
    docker build . -t ${build_report}/${build_app}:${build_version}
}


function main() {
    envfile
}

main;${build_app}


