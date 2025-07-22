function main(){
    sed -i "s/v2ray_path/${v2ray_path}/g" /etc/nginx/conf/nginx.conf
    sed -i "s/v2ray_domain/${v2ray_domain}/g" /etc/nginx/conf/nginx.conf
    sed -i "s/v2ray_uuid/${v2ray_uuid}/g" /app/v2ray/config.json
    sed -i "s/v2ray_email/${v2ray_email}/g" /app/v2ray/config.json
    sed -i "s/v2ray_path/${v2ray_path}/g" /app/v2ray/config.json
    echo " "
    echo "----------start verification----------"
    if [[ ! -f /etc/nginx/ssl/ssl.cer ]] && [[ ! -f /etc/nginx/ssl/ssl.key ]];then
      echo "[ERROR] https certificate file required in /etc/nginx/ssl/{ssl.cer、ssl.key}."
      exit 1
    fi

    # launching nginx
    /etc/nginx/sbin/nginx -t &>/dev/null
    if [[ $? != 0 ]];then
      echo "[ERROR] nginx failed to start, check if the passed env is correct."
      exit 1
    else
      /etc/nginx/sbin/nginx
    fi

    # launching v2ray
    /app/v2ray/v2ray -config /app/v2ray/config.json -test &>/dev/null
    if [[ $? != 0 ]];then
      echo "[ERROR] v2ray-core failed to start, check if the passed env is correct."
      exit 1
    else
      nohup /app/v2ray/v2ray -config /app/v2ray/config.json &>/dev/null &
      nohup /app/v2ray/v2ray-exporter --v2ray-endpoint "127.0.0.1:11235" --listen "0.0.0.0:8443" &>/dev/null &
    fi

    echo " "
    echo "----------client config info------------"
    echo "v2ray-core port: ${v2ray_port}"
    echo "v2ray-core alterid: 64"
    echo "v2ray-core protocol: ws"
    echo "v2ray-core security: tls"
    echo "v2ray-core addr: ${v2ray_domain}"
    echo "v2ray-core uuid: ${v2ray_uuid}"
    echo "v2ray-core path: ${v2ray_path}"
    echo "v2ray-core encryption: aes-128-gcm"
}

main