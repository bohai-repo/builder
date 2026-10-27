# deepseek-harness-web

基于 [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)（`dsh`）Web 配置的 Docker 镜像：在容器内跑浏览器版 dsh，构建时把插件烤进 `web` profile，运行时用 compose 持久化工作区与凭据。

镜像名：`registry.cn-hangzhou.aliyuncs.com/bohai_repo/deepseek-harness-web:1.0.0`  
默认 dsh 版本：`0.2.1-rc.2`（见 `Dockerfile` 中 `DSH_VERSION`）

## 功能概览

- 多阶段构建：build 阶段安装 pnpm / dsh、按 `dsh/plugins.txt` bake 插件；runtime 只保留 Node、dsh 与烤好的 profile
- 首次启动若尚无 `profiles/web`，从镜像拷入烤好的 profile；之后保留卷上改动。升级镜像后需人工同步 profile。会话与凭据仍落在 `./home`
- 支持官方 DeepSeek，或自定义 OpenAI 兼容网关（`BASE_URL` + `MODEL`）

## 快速开始

```bash
cd deepseek-harness-web   # 本仓库根目录
cp .env.example .env
# 编辑 .env，至少填写 API_KEY

docker compose build
docker compose up -d
docker compose logs -f dsh-web
```

日志里会出现类似：

```text
dsh web: http://<绑定IP>:3080/?token=...
```

用该 URL 打开一次即可换取签名 cookie；之后同一浏览器可直接访问 `http://<绑定IP>:3080/`（需持久化 `./home`，见下文「认证说明」）。

停止：

```bash
docker compose down
```

## 环境变量

复制自 `.env.example`，常用项：

| 变量 | 说明 |
|------|------|
| `API_KEY` | **必填**。未设 `BASE_URL` 时作为 DeepSeek 密钥（并写入 `DEEPSEEK_API_KEY`） |
| `BASE_URL` | 可选。自定义 OpenAI 兼容网关根地址；设置后必须同时提供 `MODEL` |
| `MODEL` | 可选。模型 id，多个用逗号分隔，第一个为默认 |
| `PORT` | 宿主机映射端口，默认 `3080` |
| `DSH_WEB_HOST` | 容器内 webserver 绑定的具体 IPv4；不设则自动探测。**不要写 `0.0.0.0`** |
| `TRUSTED_HOST` | 域名访问时额外信任的 Host（`host` 或 `host:port`，逗号分隔） |
| `WORKSPACE_DIR` | 首次启动预建的默认工作目录名，默认 `default`（落在 `/root/default`） |
| `LOG_LEVEL` | 日志级别，如 `debug` |

数据卷：`./home` → `/root`（含 `.dsh` 配置、会话、凭据与工作区）。

## 目录结构

```text
deepseek-harness-web/
├── Dockerfile                 # 多阶段构建
├── docker-compose.yml
├── .env.example
├── dsh/
│   ├── plugins.txt            # 构建时烤入的插件列表
│   └── cordis.patch.yml       # webserver 监听等补丁（host 占位符运行时替换）
└── scripts/
    ├── bake-profile-web.sh    # 构建期：seed profile + dsh plugin add
    ├── entrypoint.sh          # 运行期：还原 profile、绑 host、拉起 dsh
    ├── sync-provider.sh       # 按 BASE_URL/MODEL 同步自定义 provider
    └── dsh-restart            # 容器内重启 dsh 辅助命令
```

## 内置插件

插件在**镜像构建**时由 `scripts/bake-profile-web.sh` 读取 `dsh/plugins.txt`，执行 `dsh plugin --profile web add …`，结果写入 `/opt/dsh-web/profile-web`。当前列表：

| 源 | 说明 |
|----|------|
| [`ds-bot`](https://www.npmjs.com/package/ds-bot) | **DS Bot**：长驻 Bot 团队。支持 Main Bot、Bot 互发消息、群聊、独立工作目录与权限预设、记忆与用量统计等。把单会话 Web UI 扩展成可协作的多智能体工作区。仓库：[Fei2411/DS-Bot](https://github.com/Fei2411/DS-Bot) |
| [`dsh-vault`](https://www.npmjs.com/package/dsh-vault) | **加密凭据库**：主密码 + AES-256-GCM 存用户名/邮箱/手机/密码、TOTP、SSH / API Key / OAuth 等；提供模型工具（增删改查、搜索、生成密码、TOTP）与设置页。搜索结果不含密文。仓库：[Ox0400/dsh-vault](https://github.com/Ox0400/dsh-vault) |
| [`dsh-jenkins-panel`](https://www.npmjs.com/package/dsh-jenkins-panel) | **Jenkins 面板**：一组 `jenkins_*` 工具（触发构建、状态/日志/历史/产物、任务操作等）+ 官方右侧栏可视化（触发总览、任务树、日志与产物）；支持多连接与 Token（走 dsh 凭据）；可选构建失败后自动回推分析。 |
| [`github:fishquito7/dsh-skill-mcp-panel`](https://github.com/Fishquito7/dsh-skill-mcp-panel) | **Skill / MCP 管理面板**：在 Web UI 中管理 skill 与 MCP，便于可视化增删与查看连接状态。 |

> `plugins.txt` 支持注释行与空行；源可以是 npm 包名，或 `github:owner/repo#ref` 等形式（以当前 dsh / pnpm 能识别的为准）。

### 增删插件

1. 编辑 `dsh/plugins.txt`（每行一个源）
2. 重新构建镜像：`docker compose build --no-cache`
3. 清掉旧 profile 后重启，让入口脚本再次从镜像拷入：
   `rm -rf ./home/.dsh/profiles && docker compose up -d`

说明：

- 运行时**仅首次**（`$DSH_HOME/profiles/web` 不存在）从镜像拷入烤好的 profile；之后面板 / 运行时改动会留在卷上。
- 改 `plugins.txt` 重建镜像后，若不手动清 `./home/.dsh/profiles`，容器会继续用旧 profile，与镜像不一致。
- 部分依赖（如带原生编译脚本的 SSH 相关包）可能触发 pnpm 的 `ERR_PNPM_IGNORED_BUILDS`；需在 bake 用的 `pnpm-workspace.yaml` 里预先允许对应包的 install 脚本（例如 `onlyBuiltDependencies` / `allowBuilds`，或 `dangerouslyAllowAllBuilds`）。

## 认证说明

- 启动日志中的 `?token=` 是**进程级一次性 launch token**，无法配置成固定值；用来换签名 cookie 后会从 URL 去掉。
- Cookie 签名密钥保存在 `$DSH_HOME/.credentials.yaml`（即卷上的 `./home/.dsh/.credentials.yaml`）。**持久化 `./home` 后**，同一浏览器在 cookie 有效期内（默认约 30 天）可直接打开根 URL，不必每次抄新 token。
- 更稳妥的对外暴露方式：前置反向代理做登录/TLS，并为域名配置 `TRUSTED_HOST`（以及需要时的 `--public-url`，见上游 dsh-web-app 文档）。本镜像默认明文 HTTP 绑定具体 IP。

## 常用运维

```bash
# 看日志里的访问 URL / token
docker compose logs -f dsh-web

# 改插件或 Dockerfile 后全量重建
docker compose build --no-cache && docker compose up -d

# 升级 dsh：改 Dockerfile 的 ARG DSH_VERSION 后重建
```

容器内也可使用 `dsh-restart`（由 entrypoint 链到 `/usr/local/bin`）在不杀容器的情况下重启 dsh 进程。

## 相关链接

- DeepSeek Harness：<https://github.com/deepseek-ai/deepseek-harness>
- 本仓库插件列表：[`dsh/plugins.txt`](dsh/plugins.txt)
