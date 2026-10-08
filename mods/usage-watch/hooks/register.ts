import type {
  EngineInterface,
  Register,
  SessionContextUsage,
  SessionRateLimit,
} from 'claude-code'

type Engine = EngineInterface

// What one load of the module remembers; a hot reload starts it over.
type Memory = {
  alertedStep: Map<string, number>
  isContextArmed: boolean
  lastUsd: number | undefined
  root: string | null | undefined
  offset: { minutes: number; fetchedAt: number } | undefined
}

// Toast once per step as a plan window climbs; re-arm when it falls back below the last.
const RATE_STEPS = [90, 80] as const
// Toast once when context passes WARN; re-arm after it drops below REARM (a compaction).
const CONTEXT_WARN = 80
const CONTEXT_REARM = 50
const TOAST_MS = 8_000
// Other sessions' spend and a new day show up on this cadence between turns.
const STATUS_REFRESH_MS = 5 * 60_000
const OFFSET_TTL_MS = 60 * 60_000

const LIMIT_LABELS: Record<string, string> = {
  five_hour: '5-hour limit',
  seven_day: 'Weekly limit',
  spend_limit: 'Spend limit',
}

// Daily spend lives in one small file per session per day, so concurrent
// sessions never write the same file:
//   ~/.claude/usage-watch/days/<YYYY-MM-DD>/<session>.json  { usd }
//   ~/.claude/usage-watch/sessions/<session>.json           { lastUsd }
export const register: Register = on => {
  const memory: Memory = {
    alertedStep: new Map(),
    isContextArmed: true,
    lastUsd: undefined,
    root: undefined,
    offset: undefined,
  }

  on('session.start', async ($, e, next) => {
    const started = await next(e)
    await showToday($, memory)
    $.clock.every(STATUS_REFRESH_MS, () => showToday($, memory))
    return started
  })

  on('session.measure', async ($, e, next) => {
    try {
      await alertRateLimits($, memory, e.rateLimits)
      alertContext($, memory, e.context)
      if (e.cost && e.changed.includes('cost')) {
        await recordCost($, memory, e.cost.usd)
      }
    } catch (error) {
      $.ui.log(`usage-watch: ${String(error)}`, { to: 'debug' })
    }
    return next(e)
  })
}

async function alertRateLimits($: Engine, memory: Memory, limits: readonly SessionRateLimit[]) {
  for (const limit of limits) {
    const pct = limit.percentUsed
    const step = RATE_STEPS.find(s => pct >= s)
    if (step === undefined) {
      memory.alertedStep.delete(limit.kind)
      continue
    }
    if (step <= (memory.alertedStep.get(limit.kind) ?? 0)) continue
    memory.alertedStep.set(limit.kind, step)

    const label = LIMIT_LABELS[limit.kind] ?? limit.kind
    const resetsAt = limit.resetsAt ? Date.parse(limit.resetsAt) : NaN
    const resets = Number.isNaN(resetsAt)
      ? ''
      : ` — resets in ${formatDuration(resetsAt - (await $.clock.now()))}`
    $.ui.toast(`⚠️ ${label} at ${Math.round(pct)}%${resets}`, { timeoutMs: TOAST_MS })
  }
}

function alertContext($: Engine, memory: Memory, context: SessionContextUsage) {
  const pct = context.percent
  if (pct === undefined) return
  if (pct < CONTEXT_REARM) {
    memory.isContextArmed = true
    return
  }
  if (pct < CONTEXT_WARN || !memory.isContextArmed) return
  memory.isContextArmed = false
  const used =
    context.tokens === undefined
      ? ''
      : ` (${formatTokens(context.tokens)}/${formatTokens(context.window)})`
  $.ui.toast(`🧠 Context ${pct}% full${used} — consider /compact`, { timeoutMs: TOAST_MS })
}

async function recordCost($: Engine, memory: Memory, usd: number) {
  const dir = await storeRoot($, memory)
  if (dir === null) return
  const id = await $.session.id()
  const sessionPath = `${dir}/sessions/${id}.json`
  const last = memory.lastUsd ?? numberField(await readJson($, sessionPath), 'lastUsd') ?? 0
  // The session total only falls on /clear, which starts it over from zero.
  const delta = usd >= last ? usd - last : usd
  memory.lastUsd = usd

  if (delta > 0) {
    const dayPath = `${dir}/days/${await localDay($, memory)}/${id}.json`
    const spent = numberField(await readJson($, dayPath), 'usd') ?? 0
    await $.fs.write(dayPath, JSON.stringify({ usd: spent + delta }))
  }
  await $.fs.write(sessionPath, JSON.stringify({ lastUsd: usd }))
  await showToday($, memory)
}

async function showToday($: Engine, memory: Memory) {
  const dir = await storeRoot($, memory)
  if (dir === null) return
  const dayDir = `${dir}/days/${await localDay($, memory)}`
  const entries = await $.fs.list(dayDir).catch(() => [])
  let total = 0
  let sessions = 0
  for (const entry of entries) {
    if (entry.kind !== 'file' || !entry.name.endsWith('.json')) continue
    const usd = numberField(await readJson($, `${dayDir}/${entry.name}`), 'usd')
    if (usd === undefined) continue
    total += usd
    sessions += 1
  }
  $.ui.status(
    sessions === 0
      ? undefined
      : `📅 $${total.toFixed(2)} today across ${sessions} session${sessions === 1 ? '' : 's'}`,
  )
}

async function storeRoot($: Engine, memory: Memory): Promise<string | null> {
  if (memory.root === undefined) {
    const home = (await $.env.get('HOME')) ?? (await $.env.get('USERPROFILE'))
    memory.root = home ? `${home}/.claude/usage-watch` : null
  }
  return memory.root
}

async function localDay($: Engine, memory: Memory): Promise<string> {
  const now = await $.clock.now()
  if (memory.offset === undefined || now - memory.offset.fetchedAt > OFFSET_TTL_MS) {
    memory.offset = { minutes: await utcOffsetMinutes($, now), fetchedAt: now }
  }
  return new Date(now + memory.offset.minutes * 60_000).toISOString().slice(0, 10)
}

// The host's zone from `date +%z`; the environment's own Date may not carry it.
// Falls back to Date where there is no `date` (Windows).
async function utcOffsetMinutes($: Engine, now: number): Promise<number> {
  try {
    const { exitCode, stdout } = await $.process.run(['date', '+%z'], { timeoutMs: 2_000 })
    const match = /^([+-])(\d\d)(\d\d)$/.exec(stdout.trim())
    if (exitCode === 0 && match) {
      const minutes = Number(match[2]) * 60 + Number(match[3])
      return match[1] === '-' ? -minutes : minutes
    }
  } catch {
    // fall through to Date
  }
  return -new Date(now).getTimezoneOffset()
}

async function readJson($: Engine, path: string): Promise<unknown> {
  try {
    return JSON.parse(await $.fs.read(path))
  } catch {
    return undefined
  }
}

function numberField(value: unknown, key: string): number | undefined {
  if (typeof value !== 'object' || value === null) return undefined
  const field = (value as Record<string, unknown>)[key]
  return typeof field === 'number' && Number.isFinite(field) ? field : undefined
}

function formatDuration(ms: number): string {
  const totalMinutes = Math.max(0, Math.floor(ms / 60_000))
  const days = Math.floor(totalMinutes / 1440)
  const hours = Math.floor((totalMinutes % 1440) / 60)
  const minutes = totalMinutes % 60
  if (days) return `${days}d${hours}h`
  if (hours) return `${hours}h${minutes}m`
  return `${minutes}m`
}

function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) return `${(tokens / 1_000_000).toFixed(1)}M`
  if (tokens >= 1_000) return `${Math.round(tokens / 1_000)}K`
  return String(tokens)
}
