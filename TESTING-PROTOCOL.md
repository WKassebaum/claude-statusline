# Safe Testing Protocol for Claude Code Token Tracking

## ⚠️ CRITICAL SAFETY WARNINGS

**Before testing:**
- ✅ Ensure you have a working Claude Code installation before enabling tracking
- ✅ Test in a **separate terminal** - never your main working environment
- ✅ Have an escape plan ready (see Emergency Recovery below)

**Never:**
- ❌ Enable token tracking in your main .zshrc without testing first
- ❌ Test with important work sessions - use a disposable Claude session
- ❌ Skip the validation steps

## Pre-Flight Safety Checklist

Run these checks **before** enabling token tracking:

```bash
# 1. Validate your setup
./claude-token-safe-test.sh

# 2. Ensure Claude Code works normally
claude --version
claude --help
```

## Step-by-Step Testing Protocol

### Phase 1: Environment Validation (5 minutes)

1. **Open a NEW terminal** (dedicated for testing)
2. **Run pre-flight checks:**
   ```bash
   cd /path/to/claude-statusline-fix
   ./claude-token-safe-test.sh
   ```
3. **Wait for ✅ Pre-flight checks passed!**

### Phase 2: Isolated Token Tracking Test (10 minutes)

**In the same test terminal:**

1. **Enable tracking (isolated):**
   ```bash
   export CLAUDE_TOKEN_TRACKING=1
   source ./claude-token-config.sh
   ```

2. **Validate environment:**
   ```bash
   echo "OTEL_EXPORTER_OTLP_PROTOCOL: $OTEL_EXPORTER_OTLP_PROTOCOL"
   # Should show: http/json
   ```

3. **Test Claude basic functionality:**
   ```bash
   claude --version
   # Should work without errors
   ```

4. **Test Claude startup:**
   ```bash
   echo "exit" | claude
   # Should start and exit cleanly
   ```

5. **Monitor for metrics:**
   ```bash
   # In another terminal:
   tail -f ~/.claude/token-metrics.json
   
   # Then run a simple Claude command:
   echo "What is 2+2?" | claude
   ```

### Phase 3: Full Integration Test (15 minutes)

**Only proceed if Phase 2 passed completely:**

1. **Test statusline integration:**
   ```bash
   # Run a Claude session with some interaction
   claude
   # Type a few messages, check if statusline shows 📊 indicator
   ```

2. **Verify metrics accuracy:**
   ```bash
   cat ~/.claude/token-metrics.json
   # Check timestamps are recent and token counts are reasonable
   ```

### Phase 4: Production Enablement (Only if all tests pass)

1. **Update your .zshrc safely:**
   ```bash
   # Option A: Use the safer config sourcing approach
   echo 'source "$HOME/WorkDev/MCP-Dev/claude-statusline-fix/claude-token-config.sh"' >> ~/.zshrc
   
   # Option B: Modify CLAUDE_TOKEN_TRACKING variable
   sed -i '' 's/export CLAUDE_TOKEN_TRACKING=0/export CLAUDE_TOKEN_TRACKING=1/' ~/.zshrc
   ```

2. **Test in a new terminal:**
   ```bash
   # Open fresh terminal
   claude --version  # Should work
   claude  # Should work with token tracking
   ```

## Emergency Recovery

If Claude Code crashes or behaves strangely:

### Immediate Recovery
```bash
# In any terminal:
export CLAUDE_TOKEN_TRACKING=0
unset CLAUDE_CODE_ENABLE_TELEMETRY
unset OTEL_METRICS_EXPORTER
unset OTEL_EXPORTER_OTLP_ENDPOINT
unset OTEL_EXPORTER_OTLP_PROTOCOL
unset OTEL_METRIC_EXPORT_INTERVAL

# Test Claude recovery:
claude --version
```

### Permanent Disable
```bash
# Edit .zshrc to disable:
sed -i '' 's/export CLAUDE_TOKEN_TRACKING=1/export CLAUDE_TOKEN_TRACKING=0/' ~/.zshrc

# Or comment out the sourcing line:
sed -i '' 's/^source.*claude-token-config.sh/# &/' ~/.zshrc

# Reload:
source ~/.zshrc
```

## Common Issues & Solutions

### Claude Code Won't Start
**Cause:** Missing `OTEL_EXPORTER_OTLP_PROTOCOL=http/json`
**Solution:** Run emergency recovery above

### Proxy Won't Start
**Cause:** Port 4318 occupied or permission issues
**Solution:** 
```bash
# Kill conflicting processes:
sudo lsof -ti:4318 | xargs kill -9

# Or use different port:
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4319
```

### Statusline Shows No Metrics
**Cause:** Metrics file not updating or proxy not capturing
**Solution:**
```bash
# Check proxy logs:
tail /tmp/token-metrics-proxy.log

# Restart proxy:
./stop-token-proxy.sh
./start-token-proxy.sh
```

## Success Criteria

✅ **All tests pass if:**
- Claude Code starts normally with telemetry enabled
- Statusline shows 📊 indicator with actual token counts
- Metrics file updates during Claude usage
- No crashes or error messages
- Emergency recovery works

## Rollback Plan

If issues persist after testing:
1. Disable in .zshrc: `CLAUDE_TOKEN_TRACKING=0`
2. Remove proxy: `./stop-token-proxy.sh`
3. Clean environment: Run emergency recovery commands
4. Report issue with logs from `/tmp/token-metrics-proxy.log`