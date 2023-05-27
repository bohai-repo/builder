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

    if [[ -f /etc/nginx/ssl/ssl.cer ]] && [[ -f /etc/nginx/ssl/ssl.key ]];then
      echo "ssl pass: [$(pass pass)]"
    else
      echo "nginx pass: [$(fail fail)]"
      exit 1
    fi

    # launching nginx
    /etc/nginx/sbin/nginx &>/dev/null
    if [[ $? == 0 ]];then
      echo "nginx pass: [$(pass pass)]"
      nginx
    else
      echo "nginx pass: [$(fail fail)]"
      exit 1
    fi

    # launching v2ray
    /app/v2ray/v2ray -config /app/v2ray/config.json -test &>/dev/null
    if [[ $? == 0 ]];then
      echo "v2ray pass: [$(pass pass)]"

      echo "v2ray_addr: $(info ${v2ray_domain})"
      echo "v2ray_port: 443"
      echo "v2ray_uuid: $(info ${v2ray_uuid})"
      echo "alter_id: $(info 64)"
      echo "protocol: $(info ws)"
      echo "path: $(info ${v2ray_path})"
      echo "transmission: $(info tls)"
      echo "encryption: $(info aes-128-gcm)"

      export V2RAY_VMESS_AEAD_FORCED=false
      /app/v2ray/v2ray -config /app/v2ray/config.json
    else
      echo "v2ray pass: [$(fail fail)]"
      exit 1
    fi
}

main