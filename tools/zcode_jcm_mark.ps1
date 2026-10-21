# zcode_jcm_mark.ps1 - ZCode PostToolUse hook. Writes the ONE marker that releases the
# Read/Bash-search guard in zcode_jcm_guard.ps1.
#
# v2 (owner order 2026-10-20, after the W3-session grep drift): ONLY Skill(jcodemunch)
# releases the guard. Bare jCodemunch MCP calls NO LONGER write the marker - the exact
# drift mode was "early resolve_repo calls wrote the marker, every later grep sailed".
# The skill is the entry point because its contract is the health flow the owner
# specified: analyze target indexes -> fix stale ones -> verify the fix -> proceed.
# Skill names may arrive plugin-namespaced (tools:jcodemunch) - match on the last
# colon segment.
#
# Wired in the NEXUSMILL repo's .zcode/config.json (PostToolUse, matcher
# "Skill|mcp__(plugin_jcodemunch_jcodemunch|jcodemunch)__.*" - landed with the G6 v2
# tranche there; THIS Tools copy is the canonical twin SOURCE, not the wired instance):
# Skill events carry the release decision; the MCP matcher row remains so the hook can
# deliberately IGNORE those events (documented non-release). The session id arrives as
# -SessionId (expanded from ${CLAUDE_SESSION_ID} by the hook runner) because ZCode
# payloads carry none.
#
# Fail-open: any error exits 0 and writes nothing (the guard simply keeps blocking, which
# is the safe direction for a rule-enforcement marker).

param([string]$SessionId = "")
$ErrorActionPreference = "Stop"
try {
    $raw = [Console]::In.ReadToEnd()
    if (-not $raw) { exit 0 }
    $payload = $raw | ConvertFrom-Json

    $tool = [string]$payload.tool_name

    if ($tool -eq "Skill") {
        $skill = [string]$payload.tool_input.skill
        if (-not $skill) { exit 0 }
        $tail = ($skill -split ':')[-1]
        if ($tail -ne "jcodemunch") { exit 0 }
    }
    else {
        # v2: bare jCodemunch MCP calls are deliberately NOT a release - the matcher
        # still routes them here (both mount spellings) so this branch is the
        # documented ignore. A future re-widening is a one-line change at this exit.
        exit 0
    }

    $sid = if ($SessionId) { $SessionId } else { [string]$payload.session_id }
    # the SAME fallback the guard uses: an unexpanded literal ${CLAUDE_SESSION_ID} must resolve
    # to the shared "nosession" marker on BOTH sides or the release path is dead (gate r4 f1)
    if (-not $sid -or $sid -eq '${CLAUDE_SESSION_ID}') { $sid = "nosession" }
    $marker = Join-Path $env:TEMP ("jcmz_used_" + ($sid -replace '[^A-Za-z0-9_\-]', '_') + ".flag")
    Set-Content -LiteralPath $marker -Value (Get-Date -Format s) -ErrorAction SilentlyContinue
    exit 0
}
catch {
    exit 0
}
