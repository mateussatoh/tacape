#!/usr/bin/env node
// tacape - PreToolUse guard against the em dash reaching prose on disk.
//
// A prompt rule is advisory and decays over a long session. This does not, and it also catches a
// character arriving from a paste or a generated template, which no prompt rule can.
//
// SCOPE, stated honestly: this covers Write, Edit and NotebookEdit. It is not a filesystem-level
// guarantee. A write by a program the agent launches (a formatter, a codegen step, a shell
// redirect) is outside what this can observe.
//
// TARGET, narrowed deliberately. The complaint this exists to answer is that machine-written prose
// reads as machine-written, and the em dash is the strongest single tell. So the guard bans U+2014
// only, in prose and UI copy only.
//
// The en dash U+2013 was dropped: it is correct in a numeric range (2020-2024 written properly) and
// carries none of the tell. The horizontal bar U+2015 was dropped for the same reason, it is not a
// thing a model reaches for. Banning them made the guard fire on writes that were never the problem.
//
// Non-prose files are skipped entirely. A test fixture, a JSON manifest or a parser that handles the
// character is doing legitimate work with it, and a guard aimed at how text READS has no business
// in a file nobody reads as text.
//
// Bash was deliberately REMOVED from the matcher after being added. Matching the character in a
// command string cannot distinguish writing it from searching for it or deleting it, so it denied
// `grep -rn "<char>" .` and `sed -i "s/<char>/,/g" f.md`: the two commands you most need in a repo
// that bans the character. A guard that blocks the fix is worse than no guard. Bash writes are
// caught at the next layer instead, by hooks/pre-commit and by CI, which see the result rather
// than the intent and therefore have no false positives.
//
// Escape hatch: TACAPE_ALLOW_EMDASH=1, for a repo that legitimately needs the character,
// such as one quoting a source verbatim.

// Escape sequence, never the literal character: this file must survive its own guard.
const BANNED_RE = /\u2014/;

// Extensions whose contents a human reads as prose or as UI copy. Everything else is skipped.
// Component extensions are in because that is where UI strings live; a false positive there costs
// one retry, while missing it ships the tell to the screen.
const PROSE_FILE = /\.(md|mdx|markdown|txt|rst|html?|jsx|tsx|vue|svelte|astro)$/i;

// Keys naming what is being REPLACED, not what gets written. Flagging these would block the one
// edit that removes an existing em dash, which is the opposite of the point.
const REPLACED_KEYS = new Set(['old_string', 'old_source']);

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { raw += chunk; });
process.stdin.on('end', () => {
  if (process.env.TACAPE_ALLOW_EMDASH === '1') return allow();

  let payload;
  try {
    payload = JSON.parse(raw);
  } catch (e) {
    return allow(); // fail open: never block a write because the hook could not parse its input
  }

  const input = payload && payload.tool_input;
  if (!input || typeof input !== 'object') return allow();

  // Gate on the target path before reading a single string. A file whose extension says nobody
  // reads it as prose is none of this guard's business, whatever it contains.
  const target = input.file_path || input.notebook_path;
  if (typeof target !== 'string' || !PROSE_FILE.test(target)) return allow();

  // Walk every string in the payload rather than listing field names. Field lists go stale: they
  // miss an array-of-edits shape, and they miss whatever the next tool version adds.
  const hits = [];
  walk(input, '', hits, 0);
  if (hits.length === 0) return allow();

  const where = [...new Set(hits)].slice(0, 5).join(', ');

  deny(
    'Blocked by tacape: U+2014 em dash found in ' + where + ' (' + target + '). ' +
    'The em dash is the strongest single tell that prose was machine-written, so it is banned ' +
    'in prose and UI copy. Replace each one with a comma, a colon, a period, or a real hyphen "-", ' +
    'then retry. Do not swap in another dash-like character, and do not fall back to the ' +
    '"X - Y - Z" dash-parenthetical, which is the same tell in a different costume.'
  );
});

// Collect the payload path of every string carrying the character, so the deny message points the
// model at the exact field instead of making it re-scan the whole edit.
function walk(node, path, hits, depth) {
  if (depth > 12) return; // cheap guard against pathological nesting

  if (typeof node === 'string') {
    if (BANNED_RE.test(node)) hits.push(path || 'input');
    return;
  }

  if (Array.isArray(node)) {
    node.forEach((v, i) => walk(v, path + '[' + i + ']', hits, depth + 1));
    return;
  }

  if (node && typeof node === 'object') {
    for (const key of Object.keys(node)) {
      if (REPLACED_KEYS.has(key)) continue;
      walk(node[key], path ? path + '.' + key : key, hits, depth + 1);
    }
  }
}

// Emit nothing: the tool call falls through to normal permission handling.
// Returning permissionDecision "allow" here would auto-approve every write in the session.
function allow() {
  process.exit(0);
}

function deny(reason) {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: reason,
    },
  }));
  process.exit(0);
}
