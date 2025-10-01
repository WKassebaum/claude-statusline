# Claude Statusline - Model Display Examples

## Successfully Tested Models

### Claude Sonnet 4.5 (NEW)
```
🤖 Sonnet 4.5 | 💰 $298.82 session / $177.09 today / $177.09 block (4h 2m left) | 🔥 2.8M/min | 89.0M tokens | 91.1% used | ~4h2m left
```

### Claude Sonnet 4
```
🤖 Sonnet 4 | 💰 $298.82 session / $177.09 today / $177.09 block (4h 2m left) | 🔥 2.8M/min | 89.0M tokens | 91.1% used | ~4h2m left
```

### Claude Sonnet 3.5
```
🤖 Sonnet 3.5 | 💰 $298.82 session / $177.09 today / $177.09 block (4h 2m left) | 🔥 2.8M/min | 89.0M tokens | 91.1% used | ~4h2m left
```

### Claude Opus 4.1
```
🤖 Opus 4.1 | 💰 $298.82 session / $177.09 today / $177.09 block (4h 2m left) | 🔥 2.8M/min | 88.9M tokens | 91.0% used | ~4h2m left
```

## Model Detection Logic

The statusline checks for model identifiers in order:
1. `sonnet-4-5` or `sonnet 4.5` → displays as "Sonnet 4.5"
2. `sonnet-4` or `sonnet 4` → displays as "Sonnet 4"
3. `sonnet-3-5` or `sonnet 3.5` → displays as "Sonnet 3.5"
4. `opus-4-1` or `opus 4.1` → displays as "Opus 4.1"
5. `opus-4` or `opus 4` → displays as "Opus 4"
6. `haiku` → displays as "Haiku"

## API Model Identifiers Supported

### Anthropic API
- `claude-sonnet-4-5-20250929` ✅
- `claude-sonnet-4-5` ✅
- `claude-sonnet-4-20241022` ✅
- `claude-opus-4-1-20250805` ✅
- `claude-3-5-sonnet-20241022` ✅

### AWS Bedrock
- `anthropic.claude-sonnet-4-5-20250929-v1:0` ✅
- `anthropic.claude-opus-4-1-20250805-v1:0` ✅

### GCP Vertex AI
- `claude-sonnet-4-5@20250929` ✅

## With CCR Integration (Coming Soon)

When Claude Code Router is active:

### Anthropic Model via CCR
```
🤖 Sonnet 4.5 | 🧮 CCR Metrics | 💰 $150.00 session / $177.09 today | 89.0M tokens | 91.1% used
```

### XAI/Grok Model via CCR
```
🤖 grok-4-fast | 🧮 CCR Metrics | 💰 $25.50 session / $177.09 today | 45.2M tokens | 46.3% used
```

## Testing

All model detection tests pass:
```bash
$ python3 test-sonnet-45-detection.py
Testing Model Name Detection
============================================================
✅ PASS | claude-sonnet-4-5-20250929               → Sonnet 4.5
✅ PASS | claude-sonnet-4-5                        → Sonnet 4.5
✅ PASS | claude-sonnet-4-20241022                 → Sonnet 4
✅ PASS | claude-sonnet-4                          → Sonnet 4
✅ PASS | claude-sonnet-3-5-20241022               → Sonnet 3.5
✅ PASS | claude-opus-4-1-20250805                 → Opus 4.1
✅ PASS | claude-opus-4-20241022                   → Opus 4
✅ PASS | claude-3-haiku-20240307                  → Haiku
============================================================
✅ All tests passed!
```
