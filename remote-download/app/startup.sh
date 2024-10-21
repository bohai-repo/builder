#!/bin/sh
function init(){
        WORKSPACE='/app/'
        if [[ $USE_HTTPS == '' ]];then USE_HTTPS='false';fi
        cd $WORKSPACE
        && sed -i "s/123456/$PASSWORD/g" /app/.env \
        && sed -i "s/127.0.0.1/$SERVER_NAME/g" /app/.env \
        && sed -i "s/USE_HTTPS=false/USE_HTTPS=$USE_HTTPS/g" /app/.env
}

function start(){
        nohup node app.js 1>/dev/null 2>/dev/null &
        tailf /app/access.log
}

function main(){
        init
}

main && start