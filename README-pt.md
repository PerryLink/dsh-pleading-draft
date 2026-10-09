# dsh-pleading-draft — Verificação da completude da lista de elementos da petição inicial, linha por pedido

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-pleading-draft` lê uma lista de elementos da petição inicial —o cabeçalho do processo mais uma linha por pedido, com as suas colunas `序号`、`诉讼请求`、`事实依据`、`证据`、`法律依据`、`金额` e `期限`— e verifica a completude e a coerência interna desse documento: se cada pedido regista o seu fundamento de facto, indica provas e apresenta o seu fundamento jurídico, se o pedido com montante indica também prazo de cumprimento, se o cabeçalho nomeia o autor e o réu, se não há números de elemento repetidos e se não resta nenhum marcador de modelo por substituir na coluna dos pedidos.

## Como é a saída

![Terminal demo of dsh-pleading-draft: real output over its PL-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-pleading-draft/main/docs/assets/dsh-pleading-draft-demo.png)

Saída real deste plugin sobre o seu próprio fixture de teste `PL-001` — não é uma simulação. O pacote de regras não inventa citações, por isso cada achado nomeia a cláusula aplicada e avisa que o seu texto não foi obtido.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| O pedido está redigido, mas a coluna das provas não aponta para nada. | `PL-002` assinala a linha cuja coluna `证据` não aponta para provas: verifica que a referência está escrita, não que a prova exista, esteja completa ou diga respeito a esse pedido em concreto. |
| A coluna do fundamento jurídico contém apenas uma frase genérica, como «as disposições aplicáveis». | `PL-003` exige que a coluna `法律依据` esteja preenchida em cada elemento do pedido. Reporta a coluna vazia; não verifica se a norma citada existe, está em vigor ou se aplica ao caso. |
| O montante está indicado, mas não há prazo de cumprimento registado. | `PL-004` só dispara quando a coluna `金额` está preenchida e exige então a coluna `期限`: um montante sem prazo é reportado. A um pedido meramente declarativo não se pede um prazo que ele não tem. Não se verifica se o montante está bem calculado nem se o prazo é razoável. |
| Que campos deve conter o cabeçalho do processo? | `PL-005` exige que o cabeçalho nomeie o autor e o réu; ambos são campos de configuração, pelo que o seu próprio formulário pode acrescentar a causa e o tribunal recetor. Não verifica se as partes são as corretas para esse pedido. |
| O que acontece se a coluna dos pedidos ainda contiver um marcador de modelo? | `PL-007` assinala-o: os termos que procura são `【`, `】`, `{{`, `}}`, `XXX`, `xxx`, `待填`, `待补充`, `TBD`, `todo` e `示例`. Um pedido vago que não contenha nenhum desses termos passa, porque avaliar a precisão exigível a um pedido é um juízo jurídico. |
| Uma regra aparece em `skipped` em vez de reportar algo. Isso significa que passou? | Não. `skipped` nomeia uma verificação que não correu: `PL-002`, por exemplo, surge aí quando estava desativada na configuração, quando ficou de fora pela seleção `only` ou quando o material cumpria a sua precondição e não foi encontrada qualquer diferença. Uma verificação que não corre não pode dar por boa uma coluna, e o seu limite mantém-se: nunca vê se a prova é suficiente ou corresponde ao pedido. |

## Normas que segue

| Documento | Número | Regras que o citam |
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

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-pleading-draft
dsh --profile <name> --dump-config | grep 'dsh-pleading-draft'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/pleading-draft.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-pleading-draft
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-pleading-draft contributors.
