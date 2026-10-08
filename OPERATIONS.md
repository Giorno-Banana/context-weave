# 运行与复现：Context Weave 0.3.1

需要 Python 3.10+。本候选在 Add 阶段通过 OpenRouter 调用 `openai/gpt-4o-mini`，Embedding 使用百炼 `text-embedding-v4`。Search 的可选规划器关闭。

## 私有配置

复制 `env.example` 为 `.env`，填入 `MEMORY_API_KEY`、`DASHSCOPE_API_KEY`、百炼原生 HTTP `AE_EMBEDDING_URL` 和 `OPENROUTER_API_KEY`。Key 均不得提交仓库。保持 `AE_ADD_INDEXER=1`、`AE_PLANNER=0`，使用全新 `AE_DATABASE` 路径。旧版本数据库不会自动迁移或清空，配置不匹配会拒绝启动。

OpenRouter 请求固定为 `https://openrouter.ai/api/v1/chat/completions` 和 `openai/gpt-4o-mini`。只允许 OpenAI provider，不启用模型或提供方回退，要求支持 JSON Schema 的 endpoint。上游不可用、响应被截断、出现无效引用等情况会让 Add 返回 503，且不会提交部分记忆。

## 安装和验证

在仓库根目录运行：

```bash
python -m pip install -r requirements.txt
python preflight.py --env-file .env
python -m unittest discover -s tests -v
python preflight.py --env-file .env --live --output runs/live-probe.json
```

默认 preflight 不访问网络。`--live` 会用临时数据库和合成数据调用真实 Embedding 与 GPT-4o-mini，产生少量上游用量；它不是官方 Smoke，不消耗 Full 次数。报告只记录检查结果和上游用量，不记录 Key 或原始模型对话。`/health` 显示本地配置，不代表上游余额、额度或调用一定成功。

## 启动

Windows 在仓库根目录运行：

```powershell
.\start_local.ps1 -EnvFile .\.env
```

启动器依次查找本目录 `.venv-cycle2`、上级目录 `models/.venv` 和 PATH 中的 Python，监听 `127.0.0.1:18081`，数据写入本目录 `runs/context-weave-v031-dashscope/`。它不会设置开机自启；电脑和服务需持续运行。已有 Tailscale Funnel 可继续代理同一端口，接口仍需服务 Key。

Docker 方式使用 `.env` 和新数据库路径：

```bash
docker compose up -d --build memory
```

如使用 Caddy 公网 profile，配置 `AE_DOMAIN` 后运行 `docker compose --profile public up -d`。本次未声称完成 Docker 镜像构建。

## HTTP 检查和公开诊断

```bash
python probe_http.py --base-url http://127.0.0.1:18081 --env-file .env --output runs/http-probe.json
python evaluate_retrieval.py --env-file .env --embedding-backend dashscope --data-dir /path/to/public-data --output runs/v031-pilot --limit 20 --modes hybrid_window
```

这些命令只使用自行准备的合成或公开数据。公开诊断会先写入所选对话的完整历史，费用不只取决于问题数。更改源码、模型、索引配置必须使用新输出目录和数据库。PILOT_RESULTS.md 是历史 0.2.0 基线报告，不是新版本结果。

## 并发、费用和持久化

平台初始并发配置为 Add 16 / Search 16；本地 Add LLM 并发默认 4，Embedding 仍在存储层串行调用。每次模型请求最多 8 个、每个最多 1000 字符的分块，最多重试 3 次。模型输出的短语会增加 Embedding 输入长度，Add 阶段也增加 GPT-4o-mini 费用。不能把基准总 Token 数直接当成实际计费用量或单用户内存规模。

`AE_ADD_LLM_MAX_REQUESTS` 和 `AE_EMBEDDING_MAX_REQUESTS` 为进程内次数上限，0 表示无限制；重启会重置，不能替代提供方账户额度。已成功 Add 的同一 request_id 重试不会重复调用模型；并发重复请求在单进程内合并，数据库事务防止部分写入。

官方数据仅用于当前评测，使用独立数据库，按赛事要求清除到期数据与备份。Full 前须先批准该版本并通过该版本的 Smoke；评测期间保持源码、模型配置、数据库和运行服务稳定。
