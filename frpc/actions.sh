function frpc() {
    cd ./frpc && apt-get install wget -y
    sed -i "s/version_key/$build_version/g" Dockerfile
}