#!/bin/sh
# 在镜像构建阶段调用：安装 plugins.txt 中的插件，输出到 /opt/dsh-web/profile-web
set -eu

PLUGINS_FILE="${1:-/opt/dsh-web/plugins.txt}"
OUT="${2:-/opt/dsh-web/profile-web}"
PROFILE_DIR="${DSH_HOME:-/root/.dsh}/profiles/web"

mkdir -p "$PROFILE_DIR"

# 与 dsh initProfile 对齐：先有 workspace，再 add，避免
# ERR_PNPM_NOT_IN_WORKSPACE / ERR_PNPM_ADDING_TO_ROOT。
cat > "$PROFILE_DIR/package.json" <<'JSON'
{
  "name": "dsh-profile-web",
  "private": true,
  "dependencies": {},
  "dsh": {
    "profile": {
      "bundles": ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-web-app"],
      "patchReload": "startup"
    }
  }
}
JSON

cat > "$PROFILE_DIR/pnpm-workspace.yaml" <<'YAML'
packages:
  - .

nodeLinker: hoisted
autoInstallPeers: false
YAML

add_plugin() {
  pkg=$1
  echo "bake-profile-web: dsh plugin --profile web add $pkg"
  # 无 workspace / 新 pnpm：裸 add；有 workspace 且 pnpm 拒 root：再试 -w
  if dsh plugin --profile web add "$pkg"; then
    return 0
  fi
  echo "bake-profile-web: retry with -w for $pkg"
  dsh plugin --profile web add -w "$pkg"
}

if [ -f "$PLUGINS_FILE" ]; then
  plugins=$(grep -v '^[[:space:]]*#' "$PLUGINS_FILE" | grep -v '^[[:space:]]*$' || true)
  if [ -n "$plugins" ]; then
    command -v pnpm >/dev/null 2>&1 || { echo "bake-profile-web: pnpm required" >&2; exit 1; }
    # 不用管道，避免子 shell 吞掉 add 失败
    old_ifs=$IFS
    IFS='
'
    set -f
    for pkg in $plugins; do
      IFS=$old_ifs
      set +f
      [ -n "$pkg" ] || continue
      add_plugin "$pkg"
    done
    IFS=$old_ifs
    set +f
  else
    echo "bake-profile-web: plugins.txt empty, seed only"
  fi
fi

# add 之后仍强制 patchReload=startup（避免被模板改回 live）
sed -i 's/"patchReload"[[:space:]]*:[[:space:]]*"[^"]*"/"patchReload": "startup"/g' "$PROFILE_DIR/package.json"
echo "bake-profile-web: patchReload=startup -> $PROFILE_DIR/package.json"

rm -rf "$OUT"
mkdir -p "$(dirname "$OUT")"
cp -a "$PROFILE_DIR" "$OUT"
echo "bake-profile-web: wrote $OUT"
