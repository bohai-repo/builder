## PHP for 7.3

启动

```
docker pull registry.ap-northeast-1.aliyuncs.com/bohai_repo/php-arm:7.3
docker rm -f php73
docker run -itd --name=php73 \
--restart=always \
-p 9000:9000 \
-v /app/nginx/html:/app/nginx/html \
registry.ap-northeast-1.aliyuncs.com/bohai_repo/php-arm:7.3
```

配置

```
        location ~ \.php$ {
            root           /app/nginx/html;
            fastcgi_pass   <php_ip>:9000;
            fastcgi_index  index.php;
            fastcgi_param  SCRIPT_FILENAME  /app/nginx/html/$fastcgi_script_name;
            include        fastcgi_params;
            access_log     logs/php_access.log;
            error_log      logs/php_error.log  notice;
        }
```

授权

```
chown -R nobody:nobody /app/nginx/html/
```