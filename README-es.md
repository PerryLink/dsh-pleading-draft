# dsh-pleading-draft

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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-pleading-draft
dsh --profile <name> --dump-config | grep 'dsh-pleading-draft'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/pleading-draft.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-pleading-draft
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-pleading-draft contributors.
