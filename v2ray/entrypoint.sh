function main(){
    sed -i "s/v2ray_path/${v2ray_path}/g" /etc/nginx/conf/nginx.conf
    sed -i "s/v2ray_domain/${v2ray_domain}/g" /etc/nginx/conf/nginx.conf
    sed -i "s/v2ray_uuid/${v2ray_uuid}/g" /app/v2ray/config.json
    sed -i "s/v2ray_email/${v2ray_email}/g" /app/v2ray/config.json
    sed -i "s/v2ray_path/${v2ray_path}/g" /app/v2ray/config.json
  
      # launching nginx
    /etc/nginx/sbin/nginx -t
    if [[ $? == 0 ]];then
      nginx
    else
      echo "nginx startup failed"
      exit 1
    fi

    # launching v2ray
    /app/v2ray/v2ray -config /app/v2ray/config.json -test
    if [[ $? == 0 ]];then
  
      echo "v2ray_addr: ${v2ray_domain}"
      echo "v2ray_port: 443"
      echo "v2ray_uuid: ${v2ray_uuid}"
      echo "alter_id: 64"
      echo "protocol: ws"
      echo "path: ${v2ray_path}"
      echo "transmission: tls"
      echo "encryption: aes-128-gcm"
    
      export V2RAY_VMESS_AEAD_FORCED=false
      /app/v2ray/v2ray -config /app/v2ray/config.json
    else
      echo "v2ray startup failed"
      exit 1
    fi
}

main