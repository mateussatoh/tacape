#!/bin/bash
# Installs tacape's git hooks into this repository.
#
#   bash hooks/install-git-hooks.sh
#
# Symlinks rather than copies, so the hook tracks the repo instead of going stale.

set -eu
cd "$(dirname "$0")/.."

GITDIR=$(git rev-parse --git-dir)
mkdir -p "$GITDIR/hooks"

TARGET="$GITDIR/hooks/pre-commit"
if [ -e "$TARGET" ] && [ ! -L "$TARGET" ]; then
  printf 'A pre-commit hook already exists at %s and is not a symlink.\n' "$TARGET"
  printf 'Not overwriting it. Merge by hand, or move it aside and re-run.\n'
  exit 1
fi

ln -sf "$PWD/hooks/pre-commit" "$TARGET"
chmod +x hooks/pre-commit
printf 'Installed: %s -> hooks/pre-commit\n' "$TARGET"
printf 'It blocks a commit introducing U+2013, U+2014 or U+2015. Override once with --no-verify.\n'
