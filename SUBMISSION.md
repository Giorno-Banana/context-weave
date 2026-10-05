# 第二期参赛材料草稿

状态：本地待补齐，未提交平台。不得把真实 Key 填进此公开文件。

| 字段 | 内容 |
|---|---|
| 评测类型 | Textual Memory / 文本记忆 |
| 参赛组别 | Open-source Methods / 开源方法榜 |
| 系统名称 | Context Weave |
| 版本 | 0.2.0 |
| 联系人、邮箱、机构 | 秦天朗；recursive roll；联系邮箱仅通过非公开申请表提供 |
| GitHub 仓库 | https://github.com/Giorno-Banana/context-weave |
| 固定 commit | 申请表登记本仓库所选版本的完整 commit SHA；本文件不自引用其所在提交 |
| 开源许可证、作者 | MIT；王子铭（Giorno-Banana），见 LICENSE |
| Add | `https://wzm.tail36b9f2.ts.net/add` |
| Search | `https://wzm.tail36b9f2.ts.net/search` |
| Health | `https://wzm.tail36b9f2.ts.net/health`，无需鉴权 |
| 鉴权 | `X-Api-Key`（也支持 Bearer / Token） |
| Memory System Key | 经官方受控表单提供，禁止加入仓库 |
| Eval Key | 待官方签发，禁止加入仓库 |
| Add / Search 并发 | 按平台可选范围配置；计划 Add 16 / Search 16；Full 容量仍待验证 |
| 存储、带宽及运行限制 | Windows 个人电脑，约 31.4 GiB 内存；Tailscale Funnel 公网 IP 路径的 HTTPS 小样本已通过；Full 容量与持续运行仍待验收 |

## 方法说明

Add 按原文字符跨度分块，持久化原文、来源角色、会话和可用的时间戳，调用 `text-embedding-v4` 建立向量索引。Search 在完整 user_id 范围内进行向量与 BM25 检索，用 RRF 合并排名，并按上下文预算加入相邻原文。返回 id/content 等证据字段，不生成最终答案，不接收其他问题或标准答案。

## 拟固定配置

- Embedding：百炼 `text-embedding-v4`，1024 维，document/query 类型，无自定义 instruction，无静默截断，L2 归一化。
- 分块：1000 字符，重叠 120 字符；向量候选上限 200。
- Search：`hybrid_window`，响应上限遵守平台 top_k（正式 100）；本地上下文预算 24000 字符。这是候选策略，不是声称平台预算为 24000。
- 规划 LLM：默认不调用；若经验证后启用，固定 `gpt-4o-mini`，必须更新提交配置与版本记录。
- 资源实现：单进程 FastAPI、SQLite WAL、每用户精确向量检索与 BM25，缓存至多 4 个用户。Embedding 调用当前在存储层串行化；实际吞吐尚未测定。
- 以上固定配置是基线候选，真实模型对照后再冻结 Full 版本。

## 复现与归属

按 README 和 OPERATIONS 部署，公开 [PROVENANCE.md](PROVENANCE.md)，补全原始作者、技术报告、许可证与实际采用的方法改动。历史 BGE/Qwen 分数不作为本版本成绩。

## 提交前剩余验证

真实 Embedding 自测、40 题公开集检索诊断、本机 HTTP 鉴权与隔离、进程重启恢复、通过公网 IP 路径的 HTTPS 检查已通过，见 [PILOT_RESULTS.md](PILOT_RESULTS.md)。本申请仍需完成接口绑定及必要的官方验证；Full 容量和稳定性仍待验收。由平台控制 Answer、Eval 及公榜审核。
