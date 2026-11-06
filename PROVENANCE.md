# 版本与许可记录

作者与维护者：王子铭（[Giorno-Banana](https://github.com/Giorno-Banana)）。本项目新代码采用 [MIT 许可证](LICENSE)。

2026-09-29：0.2.0 默认 Embedding 改为百炼 `text-embedding-v4`（1024 维）；BGE 仅保留在历史实验路径。适配器使用[百炼原生文本向量同步 API](https://help.aliyun.com/zh/model-studio/text-embedding-synchronous-api/)，未包含模型权重。方法与验证范围见 README、SUBMISSION 和 PILOT_RESULTS。

历史模型与诊断数据：

- [BGE-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)：历史实验使用的嵌入模型；模型适用其许可证与模型卡。0.2.0 配置使用 text-embedding-v4。
- [LoCoMo-Refined](https://github.com/mem-eval-suite/LoCoMo_refined)：本地公开诊断数据，发布候选包不附带数据或答案。

API 契约依据 [AML API Guide](https://agentmemories.ai/api-guide)。历史规划模块接口依据 [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) 和 [GPT-4o-mini](https://developers.openai.com/api/docs/models/gpt-4o-mini)。第二期规则已于 2026-09-29 重新核验，当前按赛事 FAQ 的模型要求准备，详见 README_CYCLE2.md。

代码采用 MIT 许可；依赖、模型和数据适用各自许可证。发布包不包含模型权重、原始诊断数据或标准答案。

## 0.3.0 Add 阶段更新（2026-10-06）

新增通过 [OpenRouter Chat Completions](https://openrouter.ai/docs/quickstart) 调用 `openai/gpt-4o-mini` 的适配器。新增的 Add 索引处理使用模型选择原文短语，代码验证其为原文子串，再用于向量与 BM25 索引加权。模型输出不会作为新事实或最终答案返回。提供方固定为 OpenAI，使用[结构化输出](https://openrouter.ai/docs/guides/features/structured-outputs)及[提供方参数约束](https://openrouter.ai/docs/guides/routing/provider-selection)。这是新的方法配置，其效果需要单独验证；历史基线分数不能直接移作本版本成绩。

## 0.3.1 reliability update (2026-10-08)

This version replaced free-form cue copying with integer selection of deterministic source spans, added private per-request batch checkpoints and sanitized diagnostic logs. This changes the method identity and requires an independently bound version and a fresh database. It does not claim a measured quality improvement.
