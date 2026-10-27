#!/bin/sh
set -eu

# 仅属主可读写：dsh 生成的密钥（如 .credentials.yaml）需为 0600，
# dsh-credentials-local 加载时会校验。
umask 077

mkdir -p "$DSH_HOME" /root
# 持久化卷上若误把 cordis.patch.yml 建成目录，cp 会拷进目录内，
# dsh 读该路径仍报 EISDIR；先删再拷，保证目标一定是文件。
rm -rf "$DSH_HOME/cordis.patch.yml"
cp /opt/dsh-web/cordis.patch.yml "$DSH_HOME/cordis.patch.yml"

# dsh 0.2+：webserver.host 必填且不能是 0.0.0.0；替换模板占位符。
BIND_HOST="${DSH_WEB_HOST:-$(hostname -i 2>/dev/null | awk '{print $1}')}"
BIND_HOST="${BIND_HOST:-127.0.0.1}"
sed -i "s/__BIND_HOST__/$BIND_HOST/g" "$DSH_HOME/cordis.patch.yml"

# 收紧已有敏感文件权限（dsh 拒绝 0644 的 credentials）。
chmod 600 "$DSH_HOME/.credentials.yaml" "$DSH_HOME/.env" 2>/dev/null || true

# .dsh/profiles 是 dsh 管理的运行时（插件包 + 动态 #include）。
# 仅首次（尚无 profiles/web）时从镜像烤好的 profile-web 拷入；
# 之后保留卷上改动（面板加插件、MCP 等）。升级镜像 / 改 plugins.txt 后
# 需人工同步，例如：rm -rf ./home/.dsh/profiles && docker compose restart
mkdir -p "$DSH_HOME/profiles"
if [ ! -d "$DSH_HOME/profiles/web" ]; then
  cp -a /opt/dsh-web/profile-web "$DSH_HOME/profiles/web"
fi

# 官方 DeepSeek 路由：仅在未使用自定义 BASE_URL 时生效。
if [ -z "${BASE_URL:-}" ] && [ -n "${API_KEY:-}" ] && [ -z "${DEEPSEEK_API_KEY:-}" ]; then
  export DEEPSEEK_API_KEY="$API_KEY"
fi

# 写入自定义 OpenAI 兼容 provider（BASE_URL + MODEL），或清理托管块。
/opt/dsh-web/sync-provider.sh

# 预建默认工作目录，方便首次 Web UI 目录选择器选用。
# 目录名可用 WORKSPACE_DIR 覆盖。
default_ws="${WORKSPACE_DIR:-default}"
case "$default_ws" in
  /?*) ws_path="$default_ws" ;;
  *)   ws_path="/root/$default_ws" ;;
esac
mkdir -p "$ws_path"

# 保留 Docker CMD 参数（如 --port 3080）。逐行暂存原始 argv，
# 再原样追加，避免 eval 二次解析（空格、引号、元字符等）。
cmd_args_tmp=$(mktemp)
printf '%s\n' "$@" > "$cmd_args_tmp"

set -- dsh --profile web --no-open --host "$BIND_HOST"

# 域名访问：浏览器 Host 必须在信任列表（逗号分隔的 host 或 host:port）。
if [ -n "${TRUSTED_HOST:-}" ]; then
  OLDIFS=$IFS
  IFS=','
  for host in $TRUSTED_HOST; do
    host=$(printf '%s' "$host" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    if [ -n "$host" ]; then
      set -- "$@" --trusted-host "$host"
    fi
  done
  IFS=$OLDIFS
fi

# 逐行追加原始 CMD 参数，取值原样保留。
while IFS= read -r arg; do
  set -- "$@" "$arg"
done < "$cmd_args_tmp"
rm -f "$cmd_args_tmp"

# 循环拉起 dsh：安装插件会退出 dsh，但不应拖垮容器。
# PID 1 保持存活；SIGTERM/SIGINT 转发给当前 dsh，然后干净退出循环。
stopping=0
dsh_pid=0
stop_now() {
  stopping=1
  # 将停止信号转发给正在运行的 dsh，便于其优雅退出。
  [ "$dsh_pid" -ne 0 ] && kill -TERM "$dsh_pid" 2>/dev/null || true
}

trap stop_now TERM INT
while [ "$stopping" -eq 0 ]; do
  "$@" &
  dsh_pid=$!
  if wait "$dsh_pid"; then
    code=0
  else
    code=$?
  fi
  dsh_pid=0
  [ "$stopping" -eq 1 ] && break
  echo "dsh exited (code $code); restarting in 2s..."
  sleep 2
done
exit $code
