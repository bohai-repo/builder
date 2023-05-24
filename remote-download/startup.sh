#!/bin/sh
function init(){
        WORKSPACE='/app/remote_download'
        if [[ $USE_HTTPS == '' ]];then USE_HTTPS='false';fi
        cd $WORKSPACE
        sed -i "s/123456/$PASSWORD/g" /app/www/index.html \
        && sed -i "s/123456/$PASSWORD/g" /app/remote_download/.env \
        && sed -i "s/127.0.0.1/$SERVER_NAME/g" /app/remote_download/.env \
        && sed -i "s/127.0.0.1/$SERVER_NAME/g" /etc/nginx/conf/nginx.conf \
        && sed -i "s/USE_HTTPS=false/USE_HTTPS=$USE_HTTPS/g" /app/remote_download/.env
}

function enable_oss_minio(){
        echo "$MINIO_ACCESS_KEY_ID:$MINIO_SECRET_ACCESS_KEY" > $HOME/.remote-download-s3fs ; chmod 600 ${HOME}/.remote-download-s3fs
        s3fs \
        -o passwd_file=$HOME/.remote-download-s3fs \
        -o url=$MINIO_SERVER_URL \
        -o allow_other \
        -o nonempty \
        -o no_check_certificate \
        -o use_path_request_style \
        -o umask=000 $MINIO_BUCKET_NAME /app/remote_download/files
}

function start(){
        nohup node app.js 1>/dev/null 2>/dev/null &
        /etc/nginx/sbin/nginx
        tailf /app/remote_download/access.log
}

function main(){
        # init config
        init

        # enable minio remote storage
        if [[ $REMOTE_STORAGE == "minio" ]];then
                enable_oss_minio
        fi
}

main && start