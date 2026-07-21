#!/bin/bash
# tacape - statusline for Claude Code.
#
# Renders: [TACAPE:LEVEL] <dir> (<branch>) <model>
#
# Wire it up in your settings file:
#   "statusLine": { "type": "command", "command": "bash /path/to/tacape-statusline.sh" }
#
# No node, no jq. This runs on every statusline refresh, so it stays cheap.

set -u

CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
MODE_FILE="$CONFIG_DIR/.tacape-mode"

# --- level badge -------------------------------------------------------------
# Refuse symlinks: a local attacker could point the mode file at an arbitrary
# file and have the statusline render its bytes, including ANSI escape
# sequences, into the terminal on every refresh.
LEVEL="full"
if [ -f "$MODE_FILE" ] && [ ! -L "$MODE_FILE" ]; then
  # Cap the read and strip everything outside [a-z]. Blocks escape injection
  # and OSC hyperlink spoofing through the file contents.
  LEVEL=$(head -c 16 "$MODE_FILE" 2>/dev/null | tr -d '\n\r' | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z')
fi

# Whitelist. Anything unexpected renders nothing rather than echoing bytes.
case "$LEVEL" in
  lite|full|ultra) ;;
  off) LEVEL="off" ;;
  *) LEVEL="full" ;;
esac

# Environment override wins, matching the activation hook's precedence.
if [ -n "${TACAPE_LEVEL:-}" ]; then
  case "$TACAPE_LEVEL" in
    lite|full|ultra|off) LEVEL="$TACAPE_LEVEL" ;;
  esac
fi

if [ "$LEVEL" = "off" ]; then
  BADGE=$(printf '\033[38;5;244m[tacape:off]\033[0m')
else
  UPPER=$(printf '%s' "$LEVEL" | tr '[:lower:]' '[:upper:]')
  BADGE=$(printf '\033[38;5;173m[TACAPE:%s]\033[0m' "$UPPER")
fi

# --- context from the payload ------------------------------------------------
# Claude Code sends a JSON object on stdin. Pull the two fields worth showing
# without taking a JSON parser dependency.
PAYLOAD=$(head -c 8192)

extract() {
  printf '%s' "$PAYLOAD" \
    | tr -d '\n' \
    | grep -o "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" \
    | head -1 \
    | sed 's/.*:[[:space:]]*"//; s/"$//' \
    | tr -d '\000-\037\177'
}

CWD=$(extract 'current_dir')
[ -z "$CWD" ] && CWD=$(extract 'cwd')
[ -z "$CWD" ] && CWD="$PWD"
DIR="${CWD/#$HOME/\~}"

MODEL=$(extract 'display_name')

# --- git branch --------------------------------------------------------------
BRANCH=""
if command -v git >/dev/null 2>&1; then
  B=$(git -C "$CWD" rev-parse --abbrev-ref HEAD 2>/dev/null)
  # A detached HEAD and a fresh repo with no commits both report the literal "HEAD".
  # Show the short sha instead, which is what the user can act on.
  if [ "$B" = "HEAD" ]; then
    B=$(git -C "$CWD" rev-parse --short HEAD 2>/dev/null || printf 'no commits')
  fi
  if [ -n "$B" ]; then
    # status --porcelain also catches untracked files, which `diff HEAD` misses, and it does
    # not error on a repo with zero commits the way `diff HEAD` does.
    DIRTY=""
    [ -n "$(git -C "$CWD" status --porcelain 2>/dev/null | head -1)" ] && DIRTY="*"
    BRANCH=$(printf ' \033[38;5;66m(%s%s)\033[0m' "$B" "$DIRTY")
  fi
fi

# --- render ------------------------------------------------------------------
printf '%s \033[38;5;110m%s\033[0m%s' "$BADGE" "$DIR" "$BRANCH"
[ -n "$MODEL" ] && printf ' \033[38;5;244m%s\033[0m' "$MODEL"
