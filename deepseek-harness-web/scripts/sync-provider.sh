#!/bin/sh
# 将托管的自定义 OpenAI 兼容 provider 合并写入 $DSH_HOME/settings.yaml。
# 环境变量：BASE_URL、MODEL（设置 BASE_URL 时必填；逗号分隔多个 id）、
# API_KEY（在配置里以 apiKeyEnv 引用）。第一个 model id 作为默认模型。
set -eu

settings="${DSH_HOME:?DSH_HOME required}/settings.yaml"
begin='# >>> dsh-web-managed'
end='# <<< dsh-web-managed'

yaml_quote() {
  printf "'%s'" "$(printf '%s' "$1" | sed "s/'/''/g")"
}

strip_managed() {
  if [ ! -f "$settings" ]; then
    return 0
  fi
  awk -v b="$begin" -v e="$end" '
    $0 == b { skip=1; next }
    skip && $0 == e { skip=0; next }
    !skip { print }
  ' "$settings" > "$settings.tmp"
  mv "$settings.tmp" "$settings"
  [ -s "$settings" ] || rm -f "$settings"
}

# 删除由 dsh-web-managed 接管的手写顶层段，保证下方托管块是唯一声明。
# 若再出现第二个 llm-pi-ai（例如 Web UI 加的），会形成重复 YAML 键，
# dsh 会拒绝整份文档。
strip_keys() {
  if [ ! -f "$settings" ]; then
    return 0
  fi
  awk '
    BEGIN { skip=0 }
    {
      if (skip) {
        if ($0 ~ /^[[:space:]]/ || $0 ~ /^$/ || $0 ~ /^#/) { next }
        skip=0
      }
      if ($0 == "llm-pi-ai:" || $0 == "agent-default-model:") { skip=1; next }
      print
    }
  ' "$settings" > "$settings.tmp"
  mv "$settings.tmp" "$settings"
  [ -s "$settings" ] || rm -f "$settings"
}

if [ -z "${BASE_URL:-}" ]; then
  # 无自定义路由：清掉托管块及残留的 llm-pi-ai / agent-default-model，
  # 让 dsh 干净回退到默认配置。
  strip_managed
  strip_keys
  exit 0
fi

if [ -z "${MODEL:-}" ]; then
  echo "sync-provider: MODEL is required when BASE_URL is set" >&2
  exit 1
fi

if [ -z "${API_KEY:-}" ]; then
  echo "sync-provider: API_KEY is required when BASE_URL is set" >&2
  exit 1
fi

mkdir -p "$DSH_HOME"
strip_managed
strip_keys

base_q=$(yaml_quote "$BASE_URL")

# 用 IFS 按逗号拆分 MODEL（兼容 sh），去掉空白与空段；
# 第一个非空 id 作为默认模型。
models_block=
first_model=
old_ifs=$IFS
set -f
IFS=','
for id in $MODEL; do
  id=$(printf '%s' "$id" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  [ -n "$id" ] || continue
  if [ -z "$first_model" ]; then
    first_model=$id
  fi
  models_block="${models_block}
        - id: $(yaml_quote "$id")
          # 可选思考强度——pi-ai 全部七档。"off" 不发送 reasoning 字段，
          # 即 provider 默认（见下方 reasoning: off）；其余映射为 OpenAI 兼容写法。
          # 声明 reasoningEfforts 会启用可选思考 UI，并设置
          # compat.supportsReasoningEffort。
          reasoningEfforts:
            off: null
            minimal: minimal_effort
            low: low_effort
            medium: medium_effort
            high: high_effort
            xhigh: xhigh_effort
            max: max_effort
          compat:
            supportsReasoningEffort: true"
done
set +f
IFS=$old_ifs

if [ -z "$first_model" ]; then
  echo "sync-provider: MODEL contains no model ids" >&2
  exit 1
fi
default_q=$(yaml_quote "$first_model")

{
  if [ -f "$settings" ]; then
    cat "$settings"
    printf '\n'
  fi
  cat <<EOF
$begin
llm-pi-ai:
  providers:
    custom:
      displayName: Custom
      apiKeyEnv: API_KEY
      api: openai-completions
      baseURL: $base_q
      # 该 provider 下所有模型的默认思考强度（off = 关闭）。
      reasoning: off
      # 本网关下模型均声明支持图片。这是对端点的声明而非探测：
      # 实际拒图的模型会在对话中被 provider 拒绝。确认真实视觉能力后，
      # 可用模型级 input 字段收窄。
      defaultInput: [text, image]
      models:$models_block
agent-default-model:
  provider: custom
  model: $default_q
$end
EOF
} > "$settings.tmp"
mv "$settings.tmp" "$settings"
