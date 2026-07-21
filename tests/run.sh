#!/bin/bash
# tacape test suite. Pure bash plus node, no dependencies, no framework.
#
# Run: bash tests/run.sh
#
# This exists because skills/tacape-code/SKILL.md says "a feature ships with tests, no test not
# done", and because it says a rule enforced by nothing is indistinguishable from a rule that
# passes. A plugin arguing that prompt rules decay and belong in the tool layer has to hold its
# own rules in the tool layer too.

set -u
cd "$(dirname "$0")/.." || exit 1
ROOT="$PWD"

PASS=0
FAIL=0

ok()   { PASS=$((PASS+1)); printf '  ok    %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  FAIL  %s\n' "$1"; [ -n "${2:-}" ] && printf '        %s\n' "$2"; }
group(){ printf '\n%s\n' "$1"; }

# assert_eq <label> <expected> <actual>
assert_eq() {
  if [ "$2" = "$3" ]; then ok "$1"; else bad "$1" "expected [$2] got [$3]"; fi
}
# assert_contains <label> <needle> <haystack>
assert_contains() {
  case "$3" in *"$2"*) ok "$1" ;; *) bad "$1" "missing [$2] in [${3:0:120}]" ;; esac
}
# assert_empty <label> <actual>
assert_empty() {
  if [ -z "$2" ]; then ok "$1"; else bad "$1" "expected empty, got [${2:0:120}]"; fi
}

GUARD="node $ROOT/hooks/tacape-emdash-guard.js"
ACTIVATE="node $ROOT/hooks/tacape-activate.js"
STATUS="bash $ROOT/hooks/tacape-statusline.sh"

# Built with printf so this file never contains the literal characters it bans.
EM=$(printf '\u2014')
EN=$(printf '\u2013')

# ---------------------------------------------------------------------------
group 'repo invariant'

# -I skips binary files. A PNG's bytes match the pattern by coincidence, and a
# binary has no prose to fix, so a hit there is always a false positive.
HITS=$(grep -rlIP '\x{2013}|\x{2014}|\x{2015}' . --exclude-dir=.git 2>/dev/null)
assert_empty 'no dash-family character anywhere in the repo' "$HITS"

for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json \
         .codex-plugin/plugin.json gemini-extension.json; do
  if node -e "JSON.parse(require('fs').readFileSync('$f','utf8'))" 2>/dev/null; then
    ok "valid json: $f"
  else
    bad "valid json: $f"
  fi
done

CC_VER=$(node -e "process.stdout.write(require('$ROOT/.claude-plugin/plugin.json').version)")
CX_VER=$(node -e "process.stdout.write(require('$ROOT/.codex-plugin/plugin.json').version)")
GM_VER=$(node -e "process.stdout.write(require('$ROOT/gemini-extension.json').version)")
assert_eq 'codex manifest version matches claude' "$CC_VER" "$CX_VER"
assert_eq 'gemini manifest version matches claude' "$CC_VER" "$GM_VER"

# Every skill directory must carry a SKILL.md whose name field matches the directory.
for d in skills/*/; do
  name=$(basename "$d")
  if [ ! -f "$d/SKILL.md" ]; then bad "skill has SKILL.md: $name"; continue; fi
  declared=$(sed -n 's/^name:[[:space:]]*//p' "$d/SKILL.md" | head -1 | tr -d '\r')
  assert_eq "skill name matches dir: $name" "$name" "$declared"
done

# ---------------------------------------------------------------------------
group 'em dash guard: denies'

OUT=$(printf '{"tool_input":{"file_path":"a.md","content":"x %s y"}}' "$EM" | $GUARD)
assert_contains 'content with em dash is denied' '"permissionDecision":"deny"' "$OUT"

OUT=$(printf '{"tool_input":{"file_path":"a.ts","new_string":"a %s b"}}' "$EM" | $GUARD)
assert_contains 'new_string with em dash is denied' '"permissionDecision":"deny"' "$OUT"

OUT=$(printf '{"tool_input":{"file_path":"a.md","content":"x %s y"}}' "$EN" | $GUARD)
assert_contains 'en dash is denied too' 'U+2013' "$OUT"

# Regression: a field list missed this shape entirely. The walk must find it.
OUT=$(printf '{"tool_input":{"file_path":"a.ts","edits":[{"new_string":"ok"},{"new_string":"b %s c"}]}}' "$EM" | $GUARD)
assert_contains 'nested edits array is denied' '"permissionDecision":"deny"' "$OUT"
assert_contains 'deny message names the payload path' 'edits[1]' "$OUT"

# ---------------------------------------------------------------------------
group 'em dash guard: allows'

# An allow must emit NOTHING. Emitting permissionDecision "allow" would auto-approve every
# write in the session, which is a far worse bug than the one this hook fixes.
OUT=$(echo '{"tool_input":{"content":"x - y"}}' | $GUARD)
assert_empty 'clean payload emits nothing, does not auto-approve' "$OUT"

OUT=$(printf '{"tool_input":{"old_string":"a %s b","new_string":"a, b"}}' "$EM" | $GUARD)
assert_empty 'removing an existing em dash is allowed' "$OUT"

OUT=$(printf '{"tool_input":{"content":"a %s b"}}' "$EM" | TACAPE_ALLOW_EMDASH=1 $GUARD)
assert_empty 'escape hatch allows' "$OUT"

OUT=$(printf 'not json at all' | $GUARD)
assert_empty 'malformed input fails open' "$OUT"

OUT=$(printf '' | $GUARD)
assert_empty 'empty input fails open' "$OUT"

OUT=$(printf '{"tool_input":null}' | $GUARD)
assert_empty 'null tool_input fails open' "$OUT"

# Regression: Bash was briefly added to the matcher. It denied `grep -rn "<char>" .` and
# `sed -i "s/<char>/,/g" f.md`, the two commands you most need in a repo that bans the character,
# because a command string cannot distinguish writing from searching or deleting. The guard must
# not be reachable from Bash; the pre-commit hook and CI cover that layer instead.
MATCHER=$(node -e "process.stdout.write(require('$ROOT/.claude-plugin/plugin.json').hooks.PreToolUse[0].matcher)")
case "$MATCHER" in
  *Bash*) bad 'guard is not wired to Bash' "matcher is [$MATCHER]; searching or removing the character would be denied" ;;
  *) ok 'guard is not wired to Bash' ;;
esac

# The docs must describe the tools the matcher actually lists.
for tool in Write Edit NotebookEdit; do
  case "$MATCHER" in
    *"$tool"*)
      if grep -q "\`$tool\`" README.md; then ok "docs mention matched tool: $tool"
      else bad "docs mention matched tool: $tool"; fi ;;
  esac
done

# The pre-commit hook is the layer that catches what the guard cannot see.
if [ -x hooks/pre-commit ] && grep -q 'diff --cached' hooks/pre-commit; then
  ok 'pre-commit hook covers the write paths the guard cannot see'
else
  bad 'pre-commit hook covers the write paths the guard cannot see'
fi

# ---------------------------------------------------------------------------
group 'activation hook'

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

OUT=$(CLAUDE_CONFIG_DIR="$TMP" $ACTIVATE | head -1)
assert_contains 'reports the active level' 'TACAPE ACTIVE - level: full' "$OUT"

OUT=$(CLAUDE_CONFIG_DIR="$TMP" TACAPE_LEVEL=ultra $ACTIVATE)
assert_contains 'ultra keeps its own intensity row' '**ultra**' "$OUT"
case "$OUT" in *'**lite**'*) bad 'ultra filters out other intensity rows' ;; *) ok 'ultra filters out other intensity rows' ;; esac

OUT=$(CLAUDE_CONFIG_DIR="$TMP" TACAPE_LEVEL=off $ACTIVATE)
assert_empty 'off emits nothing' "$OUT"

# Regression: TACAPE_LEVEL is documented as a per-session override. It must not rewrite the
# persisted default, or one `TACAPE_LEVEL=ultra claude` silently changes every future session.
printf 'full' > "$TMP/.tacape-mode"
CLAUDE_CONFIG_DIR="$TMP" TACAPE_LEVEL=ultra $ACTIVATE >/dev/null
assert_eq 'env override does not persist' 'full' "$(cat "$TMP/.tacape-mode")"

rm -f "$TMP/.tacape-mode"
CLAUDE_CONFIG_DIR="$TMP" $ACTIVATE >/dev/null
assert_eq 'default level is persisted when absent' 'full' "$(cat "$TMP/.tacape-mode" 2>/dev/null)"

# ---------------------------------------------------------------------------
group 'statusline'

PAYLOAD='{"model":{"display_name":"Opus"},"workspace":{"current_dir":"'"$ROOT"'"}}'
OUT=$(echo "$PAYLOAD" | $STATUS)
assert_contains 'renders the level badge' 'TACAPE:FULL' "$OUT"
assert_contains 'renders the model' 'Opus' "$OUT"

OUT=$(echo "$PAYLOAD" | TACAPE_LEVEL=ultra $STATUS)
assert_contains 'badge follows the env override' 'TACAPE:ULTRA' "$OUT"

OUT=$(printf '' | $STATUS)
assert_contains 'survives empty stdin' 'TACAPE' "$OUT"

# Non-ASCII paths are ordinary. Stripping them corrupted the path AND killed the branch,
# because the mangled path was then handed to git.
UTF="$TMP/ação"
mkdir -p "$UTF"
OUT=$(echo '{"workspace":{"current_dir":"'"$UTF"'"}}' | $STATUS)
assert_contains 'preserves a UTF-8 path' 'ação' "$OUT"

# A planted mode file must never reach the terminal: a statusline writes raw bytes to it.
printf '\033]8;;http://evil\033\\PWNED' > "$TMP/.tacape-mode"
OUT=$(echo '{"workspace":{"current_dir":"'"$TMP"'"}}' | CLAUDE_CONFIG_DIR="$TMP" $STATUS)
case "$OUT" in
  *PWNED*|*'evil'*) bad 'hostile mode file is not rendered' "leaked: $OUT" ;;
  *) ok 'hostile mode file is not rendered' ;;
esac
rm -f "$TMP/.tacape-mode"

# ---------------------------------------------------------------------------
group 'ruleset consistency'

# skills/tacape/SKILL.md and AGENTS.md are two hand-maintained copies of the same rules.
# CLAUDE.md requires they change together. These assertions are that requirement, enforced.
check_both() {
  local label="$1" needle="$2"
  local a b
  grep -qF "$needle" skills/tacape/SKILL.md && a=1 || a=0
  grep -qF "$needle" AGENTS.md && b=1 || b=0
  if [ "$a" = "1" ] && [ "$b" = "1" ]; then ok "$label"
  elif [ "$a" = "0" ] && [ "$b" = "0" ]; then bad "$label" "absent from BOTH copies"
  else bad "$label" "present in SKILL.md=$a AGENTS.md=$b (drift)"; fi
}

check_both 'both copies ban U+2014'            'Zero U+2014'
check_both 'both copies cap lists at 5'        'Cap lists at 5'
check_both 'both copies keep the off switch'   'normal mode'
check_both 'both copies keep safety override'  'Safety beats brevity'
check_both 'both copies exempt code comments'  'Internal code comments are exempt'

# One concrete claim that drifted before: where the level persists.
if grep -q 'persists for the session' AGENTS.md; then
  bad 'level persistence described consistently' "AGENTS.md says 'for the session'; it persists across sessions in ~/.claude/.tacape-mode"
else
  ok 'level persistence described consistently'
fi

# The documented slash command must be the one Claude Code actually registers.
if grep -rn '`/tacape[ `]' README.md INSTALL.md >/dev/null 2>&1; then
  bad 'docs use the namespaced slash command' "found bare /tacape; the real name is /tacape:tacape"
else
  ok 'docs use the namespaced slash command'
fi

# ---------------------------------------------------------------------------
printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
