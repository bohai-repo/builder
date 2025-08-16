function config_generation() {
  # get client protocol
  protocol=$1
  server_location=$(curl -4sk myip.ipip.net|awk '{print $4}')

  if [[ ${protocol} == 'vmess' ]]; then
    vmess_info=$(jq -n -c --arg v2ray_domain "$v2ray_domain" --arg server_location "$server_location" --arg v2ray_user "$v2ray_user" --arg v2ray_port "$v2ray_port" --arg v2ray_uuid "$v2ray_uuid" --arg v2ray_path "$v2ray_path" '{v: 2,ps: "\($server_location)-容器节点-\($v2ray_user)",add: $v2ray_domain,port: $v2ray_port,id: $v2ray_uuid,aid: 64,net: "ws","type":"none",host: "",path: $v2ray_path,tls: "tls"}')
    echo "vmess://$(echo -n ${vmess_info} | base64 -w 0)"
  fi
}

function main(){
    sed -i "s/v2ray_path/${v2ray_path}/g" /etc/nginx/conf/nginx.conf
    sed -i "s/v2ray_domain/${v2ray_domain}/g" /etc/nginx/conf/nginx.conf
    sed -i "s/v2ray_uuid/${v2ray_uuid}/g" /app/v2ray/config.json
    sed -i "s/v2ray_user/${v2ray_user}/g" /app/v2ray/config.json
    sed -i "s/v2ray_path/${v2ray_path}/g" /app/v2ray/config.json

    sed -i "s/timestamp/$(date +%s)/g" /etc/nginx/html/index.html
    sed -i "s/v2ray_domain/${v2ray_domain}:${v2ray_port}/g" /etc/nginx/html/index.html
    sed -i "s/v2ray_hostname/$(hostname)/g" /etc/nginx/html/index.html

    if [[ ! -f /etc/nginx/ssl/ssl.cer ]] && [[ ! -f /etc/nginx/ssl/ssl.key ]];then
      echo "[ERROR] https certificate file required in /etc/nginx/ssl/{ssl.cer、ssl.key}."
      exit 1
    fi

    # launching nginx
    /etc/nginx/sbin/nginx -t &>/tmp/start_detection.log
    if [[ $? != 0 ]];then
      echo "[ERROR] nginx failed to start,please review the startup log and attempt to repair it."
      echo ""
      cat /tmp/start_detection.log
      exit 1
    else
      /etc/nginx/sbin/nginx
    fi

    # launching v2ray
    /app/v2ray/v2ray -config /app/v2ray/config.json -test &>/tmp/start_detection.log
    if [[ $? != 0 ]];then
      echo "[ERROR] v2ray-core failed to start,please review the startup log and attempt to repair it."
      echo ""
      cat /tmp/start_detection.log
      exit 1
    else
      nohup /app/v2ray/v2ray -config /app/v2ray/config.json &>/dev/null &
      nohup /app/v2ray/v2ray-exporter --v2ray-endpoint "127.0.0.1:11235" --listen "0.0.0.0:8443" &>/dev/null &
    fi

    echo "----------client config info------------"
    echo "v2ray-core port: ${v2ray_port}"
    echo "v2ray-core alterid: 64"
    echo "v2ray-core protocol: ws"
    echo "v2ray-core security: tls"
    echo "v2ray-core addr: ${v2ray_domain}"
    echo "v2ray-core uuid: ${v2ray_uuid}"
    echo "v2ray-core path: ${v2ray_path}"
    echo "v2ray-core encryption: aes-128-gcm"
    echo " "
    echo " "
    echo "----------vmess url info------------"
    echo "$(config_generation  vmess)"
    echo " "
    echo " "
    echo "----------client access log-----------"
    tail -f /tmp/access.log
}

main