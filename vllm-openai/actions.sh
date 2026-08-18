#!/bin/sh

build_name='vllm/vllm-openai'

docker pull ${build_name}:${build_version}

echo "FROM ${build_name}:${build_version}" > Dockerfile