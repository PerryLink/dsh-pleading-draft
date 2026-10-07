/**
 * dsh-pleading-draft — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'pleading_draft'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  elementNo: ['序号', '要素序号', '编号', 'elementNo'],
  element: ['请求要素', '诉请要素', '要素', 'element'],
  claim: ['诉讼请求', '诉请', '请求事项', 'claim'],
  fact: ['事实依据', '事实', '事实与理由', 'fact'],
  evidence: ['证据', '证据编号', '证据引用', 'evidence'],
  law: ['法律依据', '法条', '法律条款', 'law'],
  amount: ['金额', '诉请金额', '标的额', 'amount'],
  deadline: ['期限', '履行期限', '给付期限', 'deadline'],
  draftedBy: ['撰写人', '承办人', '拟稿人', 'draftedBy'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'elements', '要素'],
  columns: COLUMNS,
  header: {
  caseNo: ['caseNo', '案号', '案件编号'],
  court: ['court', '受诉法院', '受理法院'],
  plaintiff: ['plaintiff', '原告', '申请人'],
  defendant: ['defendant', '被告', '被申请人'],
  cause: ['cause', '案由'],
  draftedAt: ['draftedAt', '撰写日期', '具状日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '诉讼请求',
  'claim',
  '请求要素',
  'element',
  '事实依据',
  'fact',
  '法律依据',
  'law',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
