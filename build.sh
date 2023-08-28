#!/usr/bin/env bash

build_app=$1
alias_app=$2
build_version=$3
build_repo=${build_repo_addr}/${build_repo_name}

function notice() {

  if [[ -z ${NOTICE_MAIL} ]] && [[ -z ${NOTICE_PATH} ]];then
    echo "未定义完整的通知配置,不做构建通知";
    return
  fi

  # 元数据提取
  build_describe=$(curl -s -X GET https://api.github.com/repos/bohai-repo/builder/actions/runs|head -6|grep 'name'|cut -d'"' -f4)
  build_actionid=$(curl -s -X GET https://api.github.com/repos/bohai-repo/builder/actions/runs|head -6|grep 'id'|awk '{print $2}'|cut -d, -f1)

  build_link="https://github.com/bohai-repo/builder/actions/runs/${build_actionid}"

  mail_title="来自Github Actions构建的 ${alias_app} ${build_result}通知"
  mail_body="构建应用: ${build_app} for $(uname -m)\n\n发布名称: ${alias_app}\n\n构建版本: ${build_repo}/${alias_app}:${build_version}\n\n本次构建描述: ${build_describe}\n本次构建地址: ${build_link}"

  for mail_users in ${NOTICE_MAIL};do
    curl -s -X POST -H "Content-Type:application/json" -d '{"to":"'"${mail_users}"'","subject":"'"${mail_title}"'","body":"'"${mail_body}"'"}' https://notify.itan90.cn/mail/${NOTICE_PATH}
  done
}

function launch() {
  echo "start build: ${build_repo}/${alias_app}:${build_version} for $(uname -m)"
  # 兼容精简构建和定制构建
  type ${build_app} &>/dev/null
  if [[ $? == 0 ]];then 
    ${build_app}
  else 
    if [[ -d ./${build_app} ]];then
        cd ./${build_app}
    else
        echo "app ${build_app} does not exist.";exit 1
    fi
  fi
  docker build . -t ${build_repo}/${alias_app}:${build_version}
  if [[ $? == 0 ]];then
    docker push ${build_repo}/${alias_app}:${build_version}
    # 构建残留清理
    if [[ $? == 0 && ${build_app} != 'github-runner' ]];then
        docker rmi ${build_repo}/${alias_app}:${build_version}
    fi
  else
    return 1
  fi
}

function frpc() {
    cd ./frpc && apt-get install wget -y
    sed -i "s/version_key/$build_version/g" Dockerfile
}

function github-runner() {
    export docker_version='20.10.7'
    if [ "$(uname -m)" = "x86_64" ]; then export PLATFORM=x64 ; else if [ "$(uname -m)" = "aarch64" ]; then export PLATFORM=arm64 ; fi fi
    cd ./github-runner && apt-get install wget -y
    mkdir docker && cd docker
    curl https://download.docker.com/linux/static/stable/$(uname -m)/docker-${docker_version}.tgz --output docker-${docker_version}.tgz
    tar xzf docker-${docker_version}.tgz && cd docker && tar zcf docker.tar.gz *
    cd ../../ && mv docker/docker/docker.tar.gz ./
    mkdir build && cd build
    wget https://github.com/actions/runner/releases/download/v${build_version}/actions-runner-linux-${PLATFORM}-${build_version}.tar.gz
    tar xzf actions-runner-linux-${PLATFORM}-${build_version}.tar.gz && rm -rf actions-runner-linux-${PLATFORM}-${build_version}.tar.gz
    sed -i '3,9d' ./config.sh && sed -i '3,8d' ./run.sh
    tar -zcf actions-runner-linux-${build_version}.tar.gz *
    cd ../ && mv build/actions-runner-linux-${build_version}.tar.gz ./ && rm -rf build
    sed -i "s/docker_version/${docker_version}/g" Dockerfile
    sed -i "s/version_key/$build_version/g" Dockerfile
}

function qwx_logstash() {
    cd ./qinwenxiang/logstash
}

function main() {
    launch
    # 构建通知
    if [[ $? == 0 ]];then
      build_result="构建成功"
    else
      build_result="构建失败"
    fi
    notice
}

main
