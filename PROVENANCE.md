# 来源与方法边界

作者与维护者：王子铭（[Giorno-Banana](https://github.com/Giorno-Banana)）。本项目新代码采用 [MIT 许可证](LICENSE)。

2026-09-29：0.2.0 默认 Embedding 改为百炼 `text-embedding-v4`（1024 维）；BGE 仅保留在历史实验路径。适配器依据[百炼原生文本向量同步 API](https://help.aliyun.com/zh/model-studio/text-embedding-synchronous-api/)独立实现，未包含其模型权重。方法与验证范围见 README、SUBMISSION 和 PILOT_RESULTS。

本目录的实现依据本项目历史实验和公开方法思想重新编写，没有复制四个上游仓库的源文件或提示词。历史复现代码仍位于项目原来的 `repos/` 和 `benchmarks/`，与本目录分开。

方法来源应随正式提交披露：

- [InvMem / vanilla-rag-memory](https://github.com/wenxiaof345-ctrl/vanilla-rag-memory)：原始记忆、稠密/词法混合检索与 RRF 的参照。
- [ActiveMemoryIndex](https://github.com/linxuhao/ActiveMemoryIndex)：原文优先和相邻原文窗口的参照；本候选尚未迁移 AMI 事实抽取。
- [ReFind](https://github.com/imlrz/ReFind)：按问题搜集多处证据的参照；本候选规划模块是有界的两阶段实现，不是 ReFind 原四步状态机。
- [Mem0](https://github.com/mem0ai/mem0)：记忆更新、实体与历史证据保留的研究参照；本候选不包含 Mem0 SDK 或其托管优化。
- 本项目 `benchmarks/hybrid_combinations`：Adaptive-All4 的自适应检索及上下文预算实验。
- 2026-09-07 小样本研究新增 [FlowGrid](https://github.com/dlxeva/flowgrid-aml-retriever) 的来源关联多视图、[aml-memory-mvp](https://github.com/0xboyu/aml-memory-mvp) 的互补证据选择，以及 [LongMemEval](https://arxiv.org/html/2410.10813v2) 的多键索引思路参照；新代码为独立实现，没有复制其源文件。SQLite FTS5 Porter 为标准库运行时能力。上下文向量由现有 BGE 向量池化，未复现论文的事实抽取或 HippoRAG 2 的知识图谱。
- 历史研究工作区另存了前十仓库版本、文件 SHA 与论文链接；发布包不包含该历史实验记录。公开主分支不一定等于榜单评分版本。
- [BGE-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)：历史实验使用的嵌入模型；发布模型时需保留模型自己的许可证与模型卡。0.2.0 拟提交配置使用 text-embedding-v4。
- [LoCoMo-Refined](https://github.com/mem-eval-suite/LoCoMo_refined)：本地公开诊断数据，发布候选包不附带数据或答案。

API 契约依据 [AML API Guide](https://agentmemories.ai/api-guide)。历史规划模块接口依据 [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) 和 [GPT-4o-mini](https://developers.openai.com/api/docs/models/gpt-4o-mini)。第二期规则已于 2026-09-29 重新核验，当前按赛事 FAQ 的模型要求准备，详见 README_CYCLE2.md。

本项目的 MIT 许可仅覆盖新代码，不改变上述项目、第三方依赖、模型和数据的许可。发布包不包含上游仓库、模型权重、原始诊断数据或标准答案。
