# dsh-pleading-draft — 起诉状要素齐备性核对

`dsh-pleading-draft` 读取一份起诉状（或申请书）要素核对表——案件表头加每项请求要素一行，含 `序号`、`诉讼请求`、`事实依据`、`证据`、`法律依据`、`金额`、`期限` 各栏——核对这份文书自身的齐备与自洽：每项诉请是否写明事实依据、是否指明证据、是否写明法律依据，写了金额的是否也写了履行期限，表头是否写明原告与被告，请求要素序号是否重复，诉请栏是否残留未替换的占位符。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 诉讼请求写了，但「证据」栏什么都没指。 | `PL-002` 会报出 `证据` 栏没有指明证据的行。它只核对是否写明了指向，不判断证据是否存在、是否完整、是否与该项诉请对应。 |
| 「法律依据」栏只写了「相关法律规定」这样一句笼统的话。 | `PL-003` 要求每项请求要素都填写 `法律依据` 栏。栏内空白会被报出；它不校验所引法条是否存在、是否现行有效、是否适用于本案。 |
| 金额写了，履行期限没有写。 | `PL-004` 只在 `金额` 栏已填写时才启动，随后要求填写 `期限` 栏：有金额而无期限的会被报出。确认之诉不会被要求写它本来就没有的期限。金额算得对不对、期限是否合理，它不核对。 |
| 表头必须写哪些字段？ | `PL-005` 要求表头写明原告与被告；这两项是配置字段，本机构表式可以把案由与受诉法院一并加进去。它不判断当事人是不是该案适格的当事人。 |
| 诉请栏里还留着模板占位符，会怎样？ | `PL-007` 会报出。它找的词是 `【`、`】`、`{{`、`}}`、`XXX`、`xxx`、`待填`、`待补充`、`TBD`、`todo`、`示例`。措辞含糊但不含这些词的诉请会通过，因为判断诉请该写到多具体是法律判断。 |
| 某条规则出现在 `skipped` 里，而不是报出差错——算它通过了吗？ | 不算。`skipped` 列的是**没有执行**的检查：例如 `PL-002` 在配置里被停用、被 `only` 限定在本次执行范围之外，或者材料已满足它的前置条件且未发现差异条目时，都会出现在这里。没有执行的检查不可能把某一栏核清，它的能力边界依旧：它看不到证据是否充分、是否与诉请对应。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
|---|---|---|
| 《中华人民共和国民事诉讼法》 | 1991年通过，经 2007、2012、2017、2021、2023 年五次修正（现行条号据 2021 年第四次修正及 2023 年第五次修正文本核对） | PL-001, PL-002, PL-003, PL-004, PL-005, PL-006, PL-007 |

**Boundary:** this plugin checks a **起诉状（或申请书）要素核对表** for completeness — that every claim records
its factual basis, points at evidence, states its legal basis, that a monetary claim states an amount and a
performance deadline, that the document names both parties, that element numbers are unique, and that no
placeholder survives. It does **not** decide whether a claim will succeed, whether it is time-barred, whether
jurisdiction is right, whether the evidence suffices, or whether the case should be accepted. **Those are the
court's determinations and the advocate's substantive judgement.**

> ### ⚠️ What this plugin can and cannot do
>
> **It reads a checklist, not the pleadings, the evidence or the statutes.** So it can only check that a
> column *points at* evidence or *names* a provision — **never that the evidence suffices or that the
> provision exists, is in force, or applies**. `PL-002` and `PL-003` say so in their own notes. Test the
> plugin against a pleading whose cited article was repealed: it will pass, because looking up statutes is a
> different job and one this plugin deliberately does not do.
>
> **Every `excerpt` in the rule pack says, in so many words, that the clause text was not obtained.** The
> regime lives in 《中华人民共和国民事诉讼法》(notably its article on what a statement of claim must record)
> and the Supreme People's Court's interpretation of it. The verification pass could not retrieve verbatim
> clause text, so the pack states the gap in the `excerpt` field itself and keeps every rule at `warn` or
> `info`. **When the texts are in hand, replace each `excerpt` with the real clause and raise `kind` to
> `direct`.**
>
> `PL-004` fires only when an amount column is filled, so a claim for a declaration or for a change of legal
> relation is not asked for a performance deadline it does not have. And `PL-007` catches placeholders only:
> a claim that is vague **without** containing `【】` or `待填` will pass, because judging whether a claim is
> stated with the required precision is a legal judgement.

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-pleading-draft
dsh --profile <name> --dump-config | grep 'dsh-pleading-draft'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/pleading-draft.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-pleading-draft
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-pleading-draft contributors.
