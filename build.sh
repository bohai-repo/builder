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

  mail_title="来自Github Actions构建的 ${alias_app} ${build_result}通知"
  mail_body="构建应用: ${build_app} for $(uname -m)\n\n发布名称: ${alias_app}\n\n构建版本: ${build_repo}/${alias_app}:${build_version}"

  # for mail_users in ${NOTICE_MAIL};do
  #   curl -s -X POST -H "Content-Type:application/json" -d '{"to":"'"${mail_users}"'","subject":"'"${mail_title}"'","body":"'"${mail_body}"'"}' https://webhook-mail.init.ac/api/${NOTICE_PATH}
  # done
  
  # if [[ ${NOTICE_WECHAT} ]];then
  #   message_title=$(printf "来自Github Actions构建的 %s %s通知" "$alias_app" "$build_result")
  #   message_body=$(printf "\n\n\n构建应用: %s for %s\n\n发布名称: %s\n\n构建版本: %s/%s:%s" "$build_app" "$(uname -m)" "$alias_app" "$build_repo" "$alias_app" "$build_version")
  #   curl -s -G "https://webhook-wrest.init.ac/api" --data-urlencode "receiver=47719964397@chatroom" --data-urlencode "msg=${message_title} ${message_body}"
  # fi 
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
        if [[ -f actions.sh ]];then
          sh actions.sh
        fi
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
