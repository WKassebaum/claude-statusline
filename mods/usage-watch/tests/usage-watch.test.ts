import type { On, SessionMeasureInput, SessionRateLimit } from 'claude-code'
import { describe, expect, mock, test } from 'claude-code/testing'

const HOME = '/home/t'
const DAYS = `${HOME}/.claude/usage-watch/days`

// 2026-10-08 18:00 UTC is 11:00 on the 8th at UTC-7.
const NOON_ISH = Date.parse('2026-10-08T18:00:00Z')

function world(on: On, options: { offset?: string; now?: number; session?: string } = {}) {
  const files = new Map<string, string>()
  const toasts: string[] = []
  const statuses: (string | undefined)[] = []
  const clock = mock.clock(on, { now: options.now ?? NOON_ISH })
  mock.env(on, { HOME })
  on('session.id', () => ({ value: options.session ?? 'sess-a' }))
  on('process.run', () => ({
    value: {
      exitCode: 0,
      stdout: `${options.offset ?? '-0700'}\n`,
      stderr: '',
      isStdoutTruncated: false,
      isStderrTruncated: false,
    },
  }))
  // The engine's own session.measure echoes what changed.
  on('session.measure', ($, e) => ({ changed: e.changed }))
  on('fs.read', ($, e) => {
    const text = files.get(e.path)
    return text === undefined ? { deny: `ENOENT ${e.path}` } : { value: text }
  })
  on('fs.write', ($, e) => {
    files.set(e.path, e.text)
    return { value: undefined }
  })
  on('fs.list', ($, e) => {
    const prefix = `${e.path}/`
    const value = [...files.keys()]
      .filter(p => p.startsWith(prefix) && !p.slice(prefix.length).includes('/'))
      .map(p => ({ name: p.slice(prefix.length), kind: 'file' as const, size: 0, mtimeMs: 0, isLink: false }))
    return { value }
  })
  on('ui.toast', ($, e) => {
    toasts.push(e.text)
    return { value: undefined }
  })
  on('ui.status', ($, e) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  return { files, toasts, statuses, clock }
}

function measure(over: Partial<SessionMeasureInput>): SessionMeasureInput {
  return { context: { window: 200_000 }, rateLimits: [], changed: [], ...over }
}

function fiveHour(percentUsed: number): SessionRateLimit {
  return { kind: 'five_hour', percentUsed, resetsAt: '2026-10-08T20:12:00Z' }
}

describe('rate-limit alerts', () => {
  test('toasts once per step and re-arms after the window resets', async ($, on) => {
    const w = world(on)
    for (const pct of [50, 81, 85, 91, 95]) {
      await $.session.measure(measure({ rateLimits: [fiveHour(pct)], changed: ['rateLimits'] }))
    }
    expect(w.toasts).toEqual([
      '⚠️ 5-hour limit at 81% — resets in 2h12m',
      '⚠️ 5-hour limit at 91% — resets in 2h12m',
    ])

    await $.session.measure(measure({ rateLimits: [fiveHour(3)], changed: ['rateLimits'] }))
    await $.session.measure(measure({ rateLimits: [fiveHour(92)], changed: ['rateLimits'] }))
    expect(w.toasts.length).toBe(3)
    expect(w.toasts[2]).toContain('at 92%')
  })

  test('tracks each window on its own', async ($, on) => {
    const w = world(on)
    await $.session.measure(measure({
      rateLimits: [fiveHour(85), { kind: 'seven_day', percentUsed: 82 }],
      changed: ['rateLimits'],
    }))
    expect(w.toasts).toEqual([
      '⚠️ 5-hour limit at 85% — resets in 2h12m',
      '⚠️ Weekly limit at 82%',
    ])
  })
})

describe('context alert', () => {
  test('toasts once past 80% and again only after dropping below 50%', async ($, on) => {
    const w = world(on)
    const at = (percent: number) =>
      $.session.measure(measure({
        context: { window: 200_000, tokens: percent * 2_000, percent },
        changed: ['context'],
      }))
    for (const pct of [40, 82, 90]) await at(pct)
    expect(w.toasts).toEqual(['🧠 Context 82% full (164K/200K) — consider /compact'])

    await at(60)
    await at(85)
    expect(w.toasts.length).toBe(1)

    await at(20)
    await at(81)
    expect(w.toasts.length).toBe(2)
  })
})

describe('daily cost', () => {
  test('adds each cost increase to the local day and pins the total', async ($, on) => {
    const w = world(on)
    w.files.set(`${DAYS}/2026-10-08/sess-b.json`, JSON.stringify({ usd: 10 }))

    await $.session.measure(measure({ cost: { usd: 1.5 }, changed: ['cost'] }))
    await $.session.measure(measure({ cost: { usd: 4 }, changed: ['cost'] }))

    expect(JSON.parse(w.files.get(`${DAYS}/2026-10-08/sess-a.json`)!)).toEqual({ usd: 4 })
    expect(w.statuses.at(-1)).toBe('📅 $14.00 today across 2 sessions')
  })

  test('counts spend after /clear resets the session total', async ($, on) => {
    const w = world(on)
    await $.session.measure(measure({ cost: { usd: 5 }, changed: ['cost'] }))
    await $.session.measure(measure({ cost: { usd: 0.75 }, changed: ['cost'] }))
    expect(JSON.parse(w.files.get(`${DAYS}/2026-10-08/sess-a.json`)!)).toEqual({ usd: 5.75 })
  })

  test('resumes from the saved session total instead of recounting it', async ($, on) => {
    const w = world(on)
    w.files.set(`${HOME}/.claude/usage-watch/sessions/sess-a.json`, JSON.stringify({ lastUsd: 20 }))
    await $.session.measure(measure({ cost: { usd: 22 }, changed: ['cost'] }))
    expect(JSON.parse(w.files.get(`${DAYS}/2026-10-08/sess-a.json`)!)).toEqual({ usd: 2 })
  })

  test('files spend under the local date, not the UTC one', async ($, on) => {
    // 06:30 UTC on the 8th is 23:30 on the 7th at UTC-7.
    const w = world(on, { now: Date.parse('2026-10-08T06:30:00Z') })
    await $.session.measure(measure({ cost: { usd: 3 }, changed: ['cost'] }))
    expect(w.files.has(`${DAYS}/2026-10-07/sess-a.json`)).toBe(true)
  })

  test('ignores measurements where cost did not move', async ($, on) => {
    const w = world(on)
    await $.session.measure(measure({ cost: { usd: 3 }, changed: ['context'] }))
    expect(w.files.size).toBe(0)
    expect(w.statuses).toEqual([])
  })
})
