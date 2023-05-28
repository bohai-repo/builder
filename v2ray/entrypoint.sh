function pass(){
    echo -e "\033[32m\033[01m$1\033[0m"
}

function fail(){
    echo -e "\033[31m\033[01m$1\033[0m"
}

function info(){
    echo -e "\033[34m\033[01m$1\033[0m"
}

function main(){
    sed -i "s/v2ray_path/${v2ray_path}/g" /etc/nginx/conf/nginx.conf
    sed -i "s/v2ray_domain/${v2ray_domain}/g" /etc/nginx/conf/nginx.conf
    sed -i "s/v2ray_uuid/${v2ray_uuid}/g" /app/v2ray/config.json
    sed -i "s/v2ray_email/${v2ray_email}/g" /app/v2ray/config.json
    sed -i "s/v2ray_path/${v2ray_path}/g" /app/v2ray/config.json
    echo " "
    echo "----------Launch Testing----------"
    if [[ -f /etc/nginx/ssl/ssl.cer ]] && [[ -f /etc/nginx/ssl/ssl.key ]];then
      echo "TLS Pass: [$(pass Pass)]"
    else
      echo "TLS Pass: [$(fail Fail)]"
      exit 1
    fi

    # launching nginx
    /etc/nginx/sbin/nginx -t &>/dev/null
    if [[ $? == 0 ]];then
      echo "NGINX Pass: [$(pass Pass)]"
    else
      echo "NGINX pass: [$(fail Fail)]"
      exit 1
    fi

    # launching v2ray
    /app/v2ray/v2ray -config /app/v2ray/config.json -test &>/dev/null
    if [[ $? == 0 ]];then
      echo "V2RAY Pass: [$(pass Pass)]"
    else
      echo "V2RAY Pass: [$(fail Fail)]"
      exit 1
    fi

    echo " "
    echo "----------Launching--------------"
    /etc/nginx/sbin/nginx
    if [[ $? == 0 ]];then
      echo "Launching NGINX Pass: [$(pass Pass)]"
    else
      echo "Launching NGINX Pass: [$(fail Fail)]"
      exit 1
    fi

    export V2RAY_VMESS_AEAD_FORCED=false
    nohup /app/v2ray/v2ray -config /app/v2ray/config.json &>/dev/null &
    if [[ $? == 0 ]];then
      echo "Launching V2RAY Pass: [$(pass Pass)]"
    else
      echo "Launching V2RAY Pass: [$(fail Fail)]"
      exit 1
    fi

      echo " "
      echo "----------CLENT CONFIGURE------------"
      echo "v2ray_port: $(info ${v2ray_port})"
      echo "v2ray_alterid: $(info 64)"
      echo "v2ray_protocol: $(info ws)"
      echo "v2ray_security: $(info tls)"
      echo "v2ray_addr: $(info ${v2ray_domain})"
      echo "v2ray_uuid: $(info ${v2ray_uuid})"
      echo "v2ray_path: $(info ${v2ray_path})"
      echo "v2ray_encryption: $(info aes-128-gcm)"
      echo " "
      echo "----------CLIENT WEB LOG------------"

      tail -f /tmp/access.log
}

main