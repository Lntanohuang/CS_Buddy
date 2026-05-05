# LearnPal 验收体系演进 Roadmap

> 这是一个长期跟进文档。每次发现新问题、做出新决策、跨过一个阶段,直接来这里改。
> Agent 不许擅自改这个文件的"锁定决策"段落,只能在"开放问题"段落追加观察。

---

## 当前阶段: V1-精简 (设计已锁,实施 in progress)

### 锁定决策

| 项 | 决策 | 备注 |
|---|---|---|
| 入口 | `scripts/smoke.sh` + `scripts/verify.sh` | verify 内部用 `--fast` / `--full` flag |
| 数据集规模 | 12 case × k=2 sample = 24 数据点 | 单人项目尺度,先保跑通 |
| 裁判模型 | 讯飞 `lite`(同业务模型) | 接受自评偏差作为已知风险 |
| 裁判调用策略 | A: 一次调用产出所有指标 | 24 次裁判调用/run,信号噪但成本可控 |
| 评估框架 | **不引入** Ragas / promptfoo / DeepEval | 全部用 Python + 一份统一 rubric prompt |
| RAG ground truth | 12 case 中标 6 个 `expected_contexts` | 用 `source + header` 路径作为 chunk 标识(FAISS doc_id 不稳) |
| Stop hook | 跑 `verify --fast` | 会话结束时间从 ~30s 拉到 ~2-3min |
| 反 gaming 硬规则 | `evals/` 目录 agent 不许动;history.jsonl append-only;触达评估目录的 commit 强制人审 | 一旦放开,整个体系崩 |

### V1 评估的四块分

1. **运行健康**(硬性 pass/fail)— smoke.sh 通
2. **规则断言分**— skill_id / tool_calls / expected_facts 包含 / must_not_contain 不出现
3. **答案质量分**— 一份 rubric prompt,裁判返回 `answer_quality_score`
4. **RAG 分**(6 个 case)— 同一份 prompt 同时返回 `faithfulness` / `answer_relevancy` / `context_recall`

### V1 文件树(待实施)

```
evals/
  cases.yaml                # 12 case
  rubrics/
    unified_judge.txt       # 统一裁判 prompt(返回 JSON)
  results/
    latest.jsonl            # 本次结果
    history.jsonl           # append-only 历次汇总
  scripts/
    run_eval.py
    judge.py                # 调裁判 LLM,解析 JSON
    assert_eval.py          # per-case 2/3 majority + aggregate -2pp + 两比例检验
    summarize.py
scripts/verify.sh           # 入口
server/app/agent/graph.py   # 回写 trace: skill_id / tool_calls / retrieved_doc_ids / graph_path
docs/VERIFICATION_ROADMAP.md  # 本文件
```

---

## V1 已知限制(接受作为风险,不在 V1 范围内解决)

| # | 限制 | 后果 |
|---|---|---|
| 1 | lite 自评 lite | 分数虚高 |
| 2 | 单 prompt 多指标 | 单个指标信号噪一点 |
| 3 | 6/12 case 标 RAG ground truth | RAG 层只覆盖一半 case |
| 4 | N=12, k=2 | 统计力弱,2-3 case 翻车就触发"退化"误报 |
| 5 | 没有盲测保留集 | agent / 你自己都看得见 cases.yaml,有偷懒空间 |
| 6 | previous.jsonl 比对粒度粗 | 噪声主导,小退化看不出来 |
| 7 | 样本漂移 | 产品改了,case 没改,假回归 |
| 8 | `expected_contexts` 用 source+header | 知识库重组时这些路径会漂,标注会失效 |
| 9 | `知识库/数据结构/` 全 PDF,未进索引 | RAG 评估只覆盖"计算机网络"领域 |

---

## 升级触发条件(什么时候回头补)

| 限制 | 触发条件 | 升级到 |
|---|---|---|
| #1 lite 自评偏差 | 跑 5+ 次后分数稳定在 0.85+ 但你体感产品有问题 | 切 `pro` 或 `max` 当裁判(改 1 行配置) |
| #2 单 prompt 多指标 | 某个指标的 LLM 输出反复让你怀疑(比如 faithfulness 总是 1.0) | 把那个指标单独拆出来,引入 Ragas 标准实现 |
| #3 6/12 RAG 覆盖 | 标的 6 个用着没问题 | 标到 12/12 |
| #4 N/k 太小 | baseline 跑稳后,出现 ≥1 次误报阻断 | 升到 N=30, k=3 |
| #5 无盲测集 | 任何一次"为过 gate 改 cases.yaml"事件 | **立刻**引入 20% 盲测保留集 |
| #6 比对粒度 | 误报阻断 | 加完整 Wilson CI + 两比例检验 |
| #7 样本漂移 | 两次"追假回归追到根因 = case 过时" | 设月度 case review 流程 |
| #8 source+header 漂移 | 知识库重组后标注大量失效 | 引入稳定 chunk_id(loader 改) |
| #9 PDF 未索引 | "数据结构"领域的 case 想加但加不了 | 扩 loader 支持 PDF |

---

## V2 backlog(按优先级排序)

1. **20% 盲测保留集** — 反 gaming 第二道墙
2. **N=30, k=3 + Wilson 95% CI 阻断** — 真的把统计力做起来
3. **全 12 case 标 expected_contexts** — RAG 层完整覆盖
4. **history.jsonl 趋势可视化** — 简单 HTML / matplotlib 即可,不引入大工具

## V3 backlog

- 跨厂商裁判(避免单厂商偏差)
- 自动 case 轮换 / 退役机制
- 真实用户问题入库(从产品日志采样,人工筛选)

---

## 持续跟进检查清单

**每周或每次大改后看一次**:
- [ ] history.jsonl 有没有连续 ≥3 次同方向退化?
- [ ] 哪些指标稳定 0.95+ 没区分度?→ 说明判得太松或 case 太简单
- [ ] 哪些指标频繁失败?→ 说明阈值或 rubric 出问题
- [ ] 是否出现"我下意识想去改 cases.yaml 让它过"的瞬间?→ 触发 #5 升级

**每月看一次**:
- [ ] 抽查 3 个 case 的 expected_facts,是否还反映你现在对"好答案"的标准?过时的更新或废弃
- [ ] history.jsonl 体积控制(超 10MB 归档)

---

## 开放问题(还没好答案,持续观察)

> Agent 可以在这里追加观察记录,但不要假装解决。

- **流程失真**:虽然有 evals/ 不许动的硬规则,但人类自己改 cases.yaml 让 verify 过的诱惑还在。盲测集是反制(V2),V1 期间靠你自律 + git diff 让自己看见这个动作。
- **样本漂移**:产品能力变化时 expected_facts 怎么自动同步?目前无解,只能人工 review。
- **知识库 PDF**:loader 只处理 markdown,数据结构那 2 个 PDF 没进索引。要不要扩 loader?(决定后挪到对应 backlog)
- **裁判 prompt 自身的 eval**:rubric prompt 自己的质量谁来评?目前只能"跑出来看分数靠不靠谱",没机制。

---

## 决策变更日志

> 每次锁定决策被改动,在这里追加一行。格式: `YYYY-MM-DD - 改了什么 - 为什么`

- 2026-05-05 - V1-精简方案锁定 - 与 Codex 三轮讨论后收敛,从用户原方案的"三框架并行"瘦身到"trace+一份 prompt"
