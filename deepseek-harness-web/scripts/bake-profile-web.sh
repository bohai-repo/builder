#!/bin/sh
# 在镜像构建阶段调用：安装 plugins.txt 中的插件，输出到 /opt/dsh-web/profile-web
set -eu

PLUGINS_FILE="${1:-/opt/dsh-web/plugins.txt}"
OUT="${2:-/opt/dsh-web/profile-web}"
PROFILE_DIR="${DSH_HOME:-/root/.dsh}/profiles/web"

mkdir -p "$PROFILE_DIR"
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

if [ -f "$PLUGINS_FILE" ]; then
  plugins=$(grep -v '^[[:space:]]*#' "$PLUGINS_FILE" | grep -v '^[[:space:]]*$' || true)
  if [ -n "$plugins" ]; then
    command -v pnpm >/dev/null 2>&1 || { echo "bake-profile-web: pnpm required" >&2; exit 1; }
    echo "$plugins" | while IFS= read -r pkg; do
      [ -n "$pkg" ] || continue
      echo "bake-profile-web: dsh plugin --profile web add -w $pkg"
      dsh plugin --profile web add -w "$pkg"
    done
  else
    echo "bake-profile-web: plugins.txt empty, seed only"
  fi
fi

# add 之后仍强制 patchReload=startup（避免被模板改回 live）
node -e '
const fs = require("fs");
const p = process.argv[1];
const j = JSON.parse(fs.readFileSync(p, "utf8"));
j.dsh = j.dsh || {};
j.dsh.profile = j.dsh.profile || {};
j.dsh.profile.patchReload = "startup";
fs.writeFileSync(p, JSON.stringify(j, null, 2) + "\n");
console.log("bake-profile-web: patchReload=startup -> " + p);
' "$PROFILE_DIR/package.json"

rm -rf "$OUT"
mkdir -p "$(dirname "$OUT")"
cp -a "$PROFILE_DIR" "$OUT"
echo "bake-profile-web: wrote $OUT"
