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

function main() {
    launch
}

main


