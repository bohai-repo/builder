#!/bin/sh

init(){
        WORKSPACE='/app/remote-download-service/';cd $WORKSPACE
        if [[ $USE_HTTPS == '' ]];then USE_HTTPS='false';fi
        sed -i "s/123456/$PASSWORD/g" /app/remote-download-service/.env \
        && sed -i "s/127.0.0.1/$SERVER_NAME/g" /app/remote-download-service/.env \
        && sed -i "s/127.0.0.1/$SERVER_NAME/g" /etc/nginx/nginx.conf \
        && sed -i "s/USE_HTTPS=false/USE_HTTPS=$USE_HTTPS/g" /app/remote-download-service/.env

        if [[ $SHOW_PASSWD == true ]];then sed -i "s/访问需密码/登录密码: $PASSWORD/g" /app/web/index.html;fi
}

start(){
        /sbin/nginx && node app.js
}

main(){
        init
}

main && start