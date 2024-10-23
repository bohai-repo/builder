#!/usr/bin/env bash

amd64_base='registry.ap-northeast-1.aliyuncs.com/bohai_repo/node-web-alpine:16.0.0'
arm64_base='registry.ap-northeast-1.aliyuncs.com/bohai_repo/node-web-alpine:16.0.0-arm'

if [ "$(uname -m)" = "x86_64" ]; then
  sed -i "s|^FROM base_platfrom|FROM ${amd64_base}|" Dockerfile
elif [ "$(uname -m)" = "aarch64" ]; then
  sed -i "s|^FROM base_platfrom|FROM ${arm64_base}|" Dockerfile
fi