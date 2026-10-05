# 运行与复现（第二期 0.2.0）

默认候选为 `text-embedding-v4`；BGE 仅供历史实验。已完成真实新模型的公开小样本检索诊断，见 [PILOT_RESULTS.md](PILOT_RESULTS.md)，当前没有官方成绩。需要 Python 3.10+；部署镜像使用 Python 3.12。

## 私有配置

复制 `env.example` 为 `.env`，填写：

- `MEMORY_API_KEY`：自行生成的服务鉴权密钥，供 AML 调用 Add/Search。
- `DASHSCOPE_API_KEY`：百炼账户的模型密钥，不是 Eval Key。
- `AE_EMBEDDING_URL`：百炼控制台显示的原生 HTTP 完整 endpoint；路径以 `/api/v1/services/embeddings/text-embedding/text-embedding` 结尾，不是 OpenAI 兼容的 `/embeddings`。业务空间与地域必须匹配密钥。

仅在启用 `AE_PLANNER=1` 时需要 `OPENAI_API_KEY`。默认 `AE_PLANNER=0` 仍调用向量模型。真实密钥不提交 GitHub。

## 安装与自测

在本目录运行：

```bash
python -m pip install -r requirements.txt
python preflight.py --env-file .env
python preflight.py --env-file .env --live --output runs/live-probe.json
python -m unittest discover -s tests -v
```

第一项 preflight 不访问网络，只检查配置。`--live` 对合成记忆做真实模型调用，使用临时数据库；验证鉴权、写入确认、重复与冲突请求、中文和选项检索、用户隔离、增量更新以及持久化恢复。它是进程内 HTTP 自测，不是公网测试或官方 Smoke，不占官方额度。失败仅输出脱敏状态。

`/health` 证明服务进程和本地存储已初始化，不保证上游模型此刻可用；真实可用性需通过 Add/Search 验证。

## Windows 本地启动

从项目根目录运行：

```powershell
.\competition\start_local.ps1 -EnvFile .\competition\.env
```

监听 `127.0.0.1:18081`。启动器把数据放在 `competition/runs/local-service-dashscope/`，与 BGE 分开。环境文件只按 KEY=value 读取，不执行其中的 shell 表达式。

DashScope 模式优先使用 `competition/.venv-cycle2`，不存在时才回退到历史研究环境或 PATH 中的 Python。BGE 模式仍使用研究环境。关闭启动进程会停止服务；这不是系统开机自启服务。

在另一个终端进入 `competition` 目录后，可以对运行中的服务做合成数据 HTTP 检查：

```bash
python probe_http.py --base-url http://127.0.0.1:18081 --env-file .env --output runs/http-before-restart.json
```

停止服务并以同一配置、同一数据库重新启动，再运行恢复检查：

```bash
python probe_http.py --base-url http://127.0.0.1:18081 --env-file .env --recover-from runs/http-before-restart.json --output runs/http-after-restart.json
```

探测会写入随机前缀的两个合成用户，并消耗少量真实 Embedding 用量。向目标仅发送 `MEMORY_API_KEY`，不发送百炼 Key；不跟随重定向。外部地址必须使用 HTTPS。它不启动官方 Smoke/Full。

## 个人电脑公网入口（Tailscale Funnel）

已有登录中的 Tailscale 时，可对本项目服务执行：

```powershell
tailscale funnel --bg http://127.0.0.1:18081
tailscale funnel status
```

首次启用可能给出网页授权链接，须完成账号侧授权后才能继续。成功后使用命令实际返回的 HTTPS 地址，并将上述 HTTP 探测的 `--base-url` 改成该地址。仅本机成功或仅看到 Tailscale 私网 IP 不等于公网可达；还应从外部网络验证 Health、鉴权和 Add/Search。

Funnel 提供 tailnet 域名，具有不可自定义的带宽限制，见 [Tailscale 官方说明](https://tailscale.com/docs/features/tailscale-funnel)。是否能支撑 Full 仍需验收。电脑需保持联网、接电且不休眠；后台 Funnel 不会替代本地服务进程。停止本次入口可使用 `tailscale funnel --https=443 off`；不要用 reset 清除其他项目可能使用的入口。

## Linux / Docker 部署

在源码包根目录准备 `.env`，先启动仅本机可访问的服务：

```bash
docker compose up -d --build memory
curl --fail http://127.0.0.1:18081/health
```

数据位于独立 Docker volume。公开前让域名解析到服务器，开放 80/443，并在 `.env` 中将 `AE_DOMAIN` 改为真实域名，然后：

```bash
docker compose --profile public up -d
```

Caddy 提供 HTTPS 并代理到容器；不配置访问日志。`/health` 无鉴权，`/add`、`/search` 使用 `X-Api-Key`、`Authorization: Bearer` 或 `Authorization: Token`。代理等待响应最长 1800 秒；域名、证书和公网可达性需部署后验证。

本机尚未构建镜像，因为 Docker Linux engine 不可用。服务器验证成功后记录实际镜像 ID/摘要与源码 commit，Full 期间不要重建或更新。不要运行会删除数据卷的 `docker compose down -v`。

## 公开集复测

新模型必须使用新数据库和新输出目录。先用同一组公开题做小规模对照，再扩大范围；没有凭证时不要把模拟测试称为效果评测。

环境变量配置完成后，从本目录运行：

```bash
python evaluate_retrieval.py --env-file .env --embedding-backend dashscope --data-dir /path/to/LoCoMo_refined/data/public --output runs/v4-pilot --limit 20 --modes hybrid_window
```

即使 `--limit 20`，被选中的对话也会先完整入库，不能把 20 题误当成只写 20 段。费用取决于完整历史和检索调用。脚本会记录模型身份、数据/源码哈希和上游报告的 Token 用量；这是检索诊断，不含官方 Answer/Eval 分数。

`AE_EMBEDDING_MAX_REQUESTS` 可设置本进程最多请求次数（含重试），`0` 为不限制；重启会重置，不能替代账户侧额度管理。若上游未返回用量或网络中断，记录的 Token 可能低于实际计费。

同协议可用原输出目录断点续跑；更换模型、维度、endpoint 或分块配置必须更换数据库。向量适配器每批最多 10 条，不给文本加 BGE 前缀。上游限制单条 8192 Token；超限不静默截断，应按真实调用结果处理。长文本本地分块，过长问题由上游显式拒绝。

## 历史 BGE 实验

本地历史模型仍可显式选择，但不作为此次拟提交版本：

```powershell
.\competition\start_local.ps1 -EmbeddingBackend bge -Device cpu
```

该路径需要 `requirements-local.txt` 与原模型目录。旧实验命令需加 `--embedding-backend bge`。历史日志和数据库不修改；旧分数不能迁移到新模型。

## 容量与数据

先按 Add/Search 并发各 1 联调。当前存储层串行调用 Embedding，精确检索和每用户 BM25 的大规模延迟与内存仍需实测。6000+ 题、约 300M Token 是官网整个文本基准规模，不是可据此直接确定服务器容量的单用户负载。

评测数据与公开诊断数据使用不同数据库/卷。官方数据仅用于当次评测；按规则在结束后 30 天内清除副本和备份。未暴露远程删除接口；`MemoryStore.purge_user()` 用于本地管理。正式成绩仍需官方 Smoke、Full 和复核。
