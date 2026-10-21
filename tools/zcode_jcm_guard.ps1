# zcode_jcm_guard.ps1 - ZCode PreToolUse hook enforcing the jCodemunch-first rule (G6).
# Twin of tools/jcodemunch_guard.ps1 for the ZCode mount (.zcode/config.json,
# hooks.events.PreToolUse, matcher Read|Bash). ZCode has no Grep/Glob tools - code search goes
# through Bash - so the Bash arm judges the classic search verbs (grep / rg / findstr /
# Select-String / find / fd / Get-ChildItem|gci|dir|ls with a recursive flag) aimed at
# LOCAL code repos, in addition to the Claude-style Read arm. The session marker is written
# ONLY by zcode_jcm_mark.ps1 on a Skill(jcodemunch) invocation (v2); ZCode payloads carry
# no session_id, so the id arrives as the -SessionId argument expanded from
# ${CLAUDE_SESSION_ID} by the hook runner (an unexpanded literal falls back to a shared
# "nosession" marker - documented residual).
#
# v2 SCOPE (owner order 2026-10-20, after the W3-session grep drift): the guard covers
# EVERY repo under source\repos\, not just Nexusmill - the drift session grepped
# Tools/colibri-marketplace freely because they sat outside the v1 scope. "Outside" now
# means outside source\repos entirely (scratch, corpus, system paths stay exempt).
#
# Command-position rule: a search VERB is the FIRST token of a segment split on | ; & and
# NEWLINE, so running e.g. tools/find_stats.py is not a search while "echo x\nrg foo tools/"
# is. Subshell parsing ($( ) indirection) is a DOCUMENTED residual, the same class the
# universal-tools plugin gates document.
#
# Target rule (one classification pass over the command tokens): the doc exemption needs
# EVERY path-like target to be a doc; the outside-repos exemption needs EVERY path-like
# target to resolve outside source\repos. A single mixed token keeps the command gated.
# Relative Read file_paths resolve against the hook cwd before repo scoping.
#
# WHY THE SKILL IS THE RELEASE (v2): one bare jCodemunch call per session released every
# later grep - the 2026-10-20 drift ran resolve_repo early (partial index, empty results)
# and then grepped all day. Skill(jcodemunch) is the entry because the skill CONTRACT is
# the health flow: analyze target indexes -> index_folder the stale ones -> verify the
# fix -> only then proceed. Read/Bash-search is permitted only as the LAST step,
# immediately before editing a file you have already located via jCodemunch.
#
# Escapes (owner's alone, same contract as the plugin gates): ZSKILL_GATE_OFF=1, and the
# one-shot <TEMP>\zskill-gate\OVERRIDE which burns ONLY on a call that would be denied.
#
# FAIL-OPEN BY DESIGN: any error, missing input, or unparseable payload exits 0 (allow).
# A broken guard must never block work.

param([string]$SessionId = "")
$ErrorActionPreference = "Stop"
try {
    $raw = [Console]::In.ReadToEnd()
    if (-not $raw) { exit 0 }
    $payload = $raw | ConvertFrom-Json

    $tool = [string]$payload.tool_name
    if ($tool -notin @("Read", "Bash")) { exit 0 }

    if ($env:ZSKILL_GATE_OFF -eq '1') { exit 0 }

    $sourceExt = @(".py", ".js", ".ts", ".tsx", ".jsx", ".cs", ".c", ".cpp", ".h", ".hpp", ".rs", ".go", ".rb", ".java", ".ps1", ".mjs")
    $cwd = (Get-Location).Path

    if ($tool -eq "Read") {
        $path = [string]$payload.tool_input.file_path
        if (-not $path) { exit 0 }

        # Only guard SOURCE files. Docs, JSON, config, logs and scratch stay freely readable.
        $ext = [System.IO.Path]::GetExtension($path).ToLower()
        if ($sourceExt -notcontains $ext) { exit 0 }

        # A relative file_path resolves against the hook cwd before repo scoping (gate r3 f3);
        # absolute means drive-letter, UNC, or POSIX root (M2 scan MED 3); GetFullPath collapses
        # any .. traversal so "junk/../tools/foo.ps1" cannot ride a lexical junk exemption (M3 HIGH B).
        $isAbs = ($path -match '^[a-zA-Z]:[\\/]') -or ($path -match '^\\\\') -or ($path -match '^//') -or ($path -match '^/')
        if (-not $isAbs) { $path = Join-Path $cwd $path }
        try { $path = [IO.Path]::GetFullPath($path) } catch { }

        # Only guard files inside a LOCAL repo (any source\repos checkout - v2 scope);
        # junk/ is scratch by convention.
        if ($path -notlike "*\source\repos\*" -and $path -notlike "*/source/repos/*") { exit 0 }
        if ($path -like "*\junk\*" -or $path -like "*/junk/*") { exit 0 }
    }
    else {
        $cmd = [string]$payload.tool_input.command
        if (-not $cmd) { exit 0 }
        $blob = $cmd.ToLower()

        $verbs = @('grep', 'rg', 'findstr', 'select-string', 'sls', 'find', 'fd', 'gci', 'get-childitem', 'dir', 'ls')
        $patternVerbs = @('grep', 'rg', 'findstr', 'select-string', 'sls', 'fd')
        $valueFlags = @('-e', '--regexp', '-g', '--glob', '--include', '--exclude', '-name', '-path')
        $isSearch = $false
        $sawTarget = $false; $allNonCode = $true; $allOutside = $true
        # segments keep ORIGINAL CASE: the recursive-flag test is case-sensitive (-R recurse
        # vs -r reverse) and the blob was lowercased (gate r6 F4 regression)
        foreach ($seg in ($cmd -split '[|;&\r\n]+')) {
            # @() forces an array: a pipeline assignment collapses a one-token result to a
            # scalar String, [0] then yields a Char and .Trim throws into the fail-open catch
            # (gate r11 F1)
            $segTokens = @((($seg.Trim()) -split '\s+') | Where-Object { $_ })
            if (-not $segTokens) { continue }
            # the VERB token (verbTokens) is excluded from target classification later -
            # "/usr/bin/rg allocate" is a search, not an outside target (gate r6 F2). A dotted
            # basename (tools/find.py) is NOT a verb - only .exe/.cmd/.bat or no extension
            # count (gate r9 F2)
            $rawFirst = $segTokens[0].Trim('"', "'")
            $bn = $rawFirst -replace '^.*[\\/]'
            if ($bn -match '\.(exe|cmd|bat)$') { $bn = $bn -replace '\.(exe|cmd|bat)$', '' }
            elseif ($bn -match '\.') { $bn = '' }
            $verb = $bn.ToLower()
            if (-not $verb -or $verbs -notcontains $verb) { continue }
            if ($verb -in @('ls', 'dir', 'gci', 'get-childitem')) {
                # genuinely recursive flags only: -R clusters (-Ra), lone -r/-Recurse/-Depth
                # (case-insensitive - PowerShell binding), --recursive, /s /S - reverse-sort
                # clusters like -rt/-rh must not gate (r3 f4c, M2 MED 1, M3 MED 2, r6 F4, r7, r9 F3)
                if ($seg -cmatch '\s(--recursive\b|(?i:-[a-z0-9]*ecurse)\b|-R[a-zA-Z]*\b|-r\b|(?i:-depth)\b|/[sS]\b)') { $isSearch = $true }
            } else { $isSearch = $true }

            # operand classification INSIDE the segment: for pattern-verbs the FIRST non-flag
            # token is the PATTERN (never a target), and a value-carrying flag's next token is
            # a value, not a target - so "rg -e junk/ -e allocate" has NO targets and stays
            # gated as a cwd search (gate r9 F1)
            $patternTaken = $false
            $flagPattern = $false   # -e/--regexp already supplied the pattern (third v2 review)
            $expectValue = $false
            foreach ($tk in ($segTokens | Select-Object -Skip 1)) {
                $tl = $tk.Trim('"', "'").ToLower()
                if ($expectValue) { $expectValue = $false; continue }
                if ($tl -match '^-' -or $tl -match '^/[a-z]{1,2}$') {
                    # -name/-path are find's pattern flags but gci PARAMETERS - the value rule
                    # is scoped to find alone so "gci -Path docs/ -Recurse" keeps its target
                    # (gate r10 F2b)
                    if (($valueFlags -contains $tl) -and ($verb -eq 'find' -or $tl -notin @('-name', '-path'))) {
                        $expectValue = $true
                        if ($tl -in @('-e', '--regexp') -and ($patternVerbs -contains $verb)) { $flagPattern = $true }
                    }
                    continue
                }
                if ((-not $patternTaken) -and ($patternVerbs -contains $verb)) {
                    # gate catch (third v2 review, 2026-10-20) + the r9 F1 decoy rule,
                    # reconciled: a POSITIONAL pattern token is blanket-consumed as the
                    # pattern even when path-shaped (decoy 'rg junk/ -e allocate' must
                    # stay denied) - UNLESS a value flag (-e/--regexp) already supplied
                    # the pattern, in which case the positional IS the target path
                    # ('rg -e TODO <repopath>' from an outside cwd must stay denied).
                    if (-not $flagPattern) { $patternTaken = $true; continue }
                }
                $t = $tk.Trim('"', "'")
                $isPath = ($t -match '[\\/]') -or ($t -match '\.(md|txt|rst|py|js|ts|tsx|jsx|cs|c|cpp|h|hpp|rs|go|rb|java|ps1|mjs)$')
                if (-not $isPath) { continue }
                $sawTarget = $true
                # EVERY non-POSIX token resolves (absolute included - an absolute junk/../
                # stays lexical otherwise, gate r6 F3a). A POSIX-slash token naming THIS repo
                # in its FULL source/repos spelling also resolves so junk/../ collapses in that
                # spelling too (r8 F1, v2 form). Other POSIX tokens stay LEXICAL, INCLUDING
                # a bare /nexusmill prefix (DOCUMENTED RESIDUAL, the r8 F2 8.3 class: the
                # Windows mounts emit /c/... full paths, which ARE handled, so the bare
                # form is not concretely reachable): .NET GetFullPath
                # ('/todo/') fabricates 'C:\todo\', which would read as legitimately outside.
                # A token GetFullPath cannot resolve (glob metachars throw on .NET Framework,
                # r6 F3b) classifies as CODE - fail-closed, never exempt. DOCUMENTED RESIDUAL
                # (r8 F2): an 8.3 short name ('nexus~1') evades the nexusmill substring and
                # classifies outside - deliberate evasion, the subshell/indirection class.
                $rt = $null
                if ($t -match '^/' -and $t -notmatch 'source[\\/]repos') { $rt = $t }
                else { try { $rt = [IO.Path]::GetFullPath($t) } catch { } }
                if ($null -eq $rt) { $allNonCode = $false; $allOutside = $false; continue }
                $rtL = $rt.ToLower()
                $nonCode = ($rtL -match '\.(md|txt|rst)$') -or ($rtL -match '(^|[\\/])docs([\\/]|$)') -or ($rtL -match '(^|[\\/])junk([\\/]|$)')
                if (-not $nonCode) { $allNonCode = $false }
                # v2: "outside" = outside ALL local repos (source\repos in any spelling),
                # so sibling-repo targets (Tools, colibri-marketplace, ...) stay guarded
                # while the E: corpus and scratch stay exempt. A POSIX token under
                # source/repos resolves through GetFullPath (the fabricated C:\... keeps
                # the source/repos segment, so the classification holds).
                $absOutside = (($rtL -match '^[a-z]:[\\/]') -or ($rtL -match '^\\\\') -or ($rtL -match '^//') -or ($rtL -match '^/[^/]+/.')) -and ($rtL -notmatch 'source[\\/]repos')
                if (-not $absOutside) { $allOutside = $false }
            }
        }
        if (-not $isSearch) { exit 0 }
        if ($sawTarget -and $allNonCode) { exit 0 }

        # v2 in-repo test (gate catch 2026-10-20, first v2 review): the blob terms match
        # the WHOLE command including PATTERN tokens, so a pattern-only search that merely
        # mentions 'nexusmill'/'source repos' ("zcat app.log | grep nexusmill") must NOT
        # count as in-repo when the cwd is outside the repos and no path-like target
        # exists. Blob terms apply ONLY to target-bearing commands, where the targets
        # then classify.
        $cwdRepo = ($cwd -like "*\source\repos\*") -or ($cwd -like "*/source/repos/*")
        $blobRepo = ($blob -match 'source[\\/]repos') -or ($blob -match 'nexusmill')
        # gate catch (fourth v2 review): a directory-change operand ('cd <repo> && rg TODO'
        # from an outside cwd) must count as in-repo - cd is not a search verb so its
        # operand never reached target classification and the command escaped.
        $cdRepo = $false
        foreach ($cdSeg in ($cmd -split '[|;&\r\n]+')) {
            $cdTok = @((($cdSeg.Trim()) -split '\s+') | Where-Object { $_ })
            if ($cdTok -and $cdTok[0].Trim('"', "'").ToLower() -in @('cd', 'pushd', 'set-location')) {
                foreach ($cdPath in ($cdTok | Select-Object -Skip 1)) {
                    $cp = $cdPath.Trim('"', "'")
                    if (($cp -match 'source[\\/]repos') -or ($cp -match 'nexusmill')) { $cdRepo = $true }
                }
            }
        }
        $inRepo = $cwdRepo -or $cdRepo -or ($blobRepo -and $sawTarget)
        if (-not $inRepo) { exit 0 }
        if ($sawTarget -and $allOutside) { exit 0 }
    }

    # Session marker, written ONLY by zcode_jcm_mark.ps1 on a Skill(jcodemunch)
    # invocation (v2 - bare jCodemunch MCP calls no longer release).
    $sid = if ($SessionId) { $SessionId } else { [string]$payload.session_id }
    if (-not $sid -or $sid -eq '${CLAUDE_SESSION_ID}') { $sid = "nosession" }
    $marker = Join-Path $env:TEMP ("jcmz_used_" + ($sid -replace '[^A-Za-z0-9_\-]', '_') + ".flag")
    if (Test-Path -LiteralPath $marker) { exit 0 }   # skill ran this session

    # The one-shot escape burns ONLY here, at a call that would actually be denied (gate
    # r3 f7), and ONLY if the OVERRIDE is a REGULAR FILE that is actually deleted (EV-229
    # backport 2026-10-18, the stop gate's M2 class caught live on the colibri twin port):
    # a directory or undeletable OVERRIDE must NOT fail the guard open - it keeps denying.
    $ov = Join-Path $env:TEMP 'zskill-gate\OVERRIDE'
    try {
        if ((Get-Item -LiteralPath $ov -Force -ErrorAction Stop) -is [IO.FileInfo]) {
            Remove-Item -LiteralPath $ov -Force -ErrorAction Stop
            exit 0
        }
    } catch { }

    $reason = @"
BLOCKED by Nexusmill rule G6 (jCodemunch-first, v2). The jcodemunch skill has not run
this session - it is the mandatory entry for ALL code search and location.

Invoke Skill(jcodemunch) FIRST and follow it. Its contract (owner order 2026-10-20):
  1. TARGETS - list every repo the task touches
  2. ANALYZE - resolve_repo each target; index file_count vs the repo's tracked files;
     a partial/stale index (the 2026-10-20 drift root cause) is a FIX trigger, not a
     reason to grep
  3. FIX - index_folder the unhealthy target (junk/media/.secrets ignores)
  4. VERIFY - re-run resolve_repo + a smoke search that MUST return results
  5. PROCEED - search_symbols / search_text / get_symbol_source / get_file_outline

grep/rg/find to LOCATE code is forbidden in every repo under source\repos. Read of a
source file is permitted only immediately before editing a file you located via the
index. A bare jCodemunch call does NOT release this guard - the skill does, because
the skill is what checks index health.
"@

    $out = @{
        hookSpecificOutput = @{
            hookEventName            = "PreToolUse"
            permissionDecision       = "deny"
            permissionDecisionReason = $reason
        }
    }
    $out | ConvertTo-Json -Depth 6 -Compress
    exit 0
}
catch {
    exit 0   # fail open - never block on a guard bug
}
