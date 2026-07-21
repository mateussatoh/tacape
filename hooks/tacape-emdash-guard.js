#!/usr/bin/env node
// tacape - PreToolUse guard against dash-family characters reaching disk.
//
// A prompt rule is advisory and decays over a long session. This does not, and it also catches a
// character arriving from a paste or a generated template, which no prompt rule can.
//
// SCOPE, stated honestly: this covers Write, Edit, NotebookEdit and Bash. It is not a
// filesystem-level guarantee. A write performed by a program the agent launches (a formatter, a
// codegen step, a script) is outside what a PreToolUse hook can observe. The repo-wide invariant
// belongs in CI, which is where tacape checks its own.
//
// Escape hatch: TACAPE_ALLOW_EMDASH=1, for a repo that legitimately needs these characters,
// such as one quoting a source verbatim.

// Escape sequences, never the literal characters: this file must survive its own guard.
const BANNED = {
  '\u2014': 'U+2014 em dash',
  '\u2013': 'U+2013 en dash',
  '\u2015': 'U+2015 horizontal bar',
};
const BANNED_RE = /[\u2013\u2014\u2015]/;

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

  // Walk every string in the payload rather than listing field names. Field lists go stale: they
  // miss an array-of-edits shape, and they miss whatever the next tool version adds.
  const hits = [];
  walk(input, '', hits, 0);
  if (hits.length === 0) return allow();

  const chars = [...new Set(hits.flatMap((h) => h.chars))];
  const where = [...new Set(hits.map((h) => h.path))].slice(0, 5).join(', ');
  const target = input.file_path || input.notebook_path || 'the target';

  deny(
    'Blocked by tacape: ' + chars.join(' and ') + ' found in ' + where + ' (' + target + '). ' +
    'House rule bans the dash family in every written artifact. ' +
    'Replace each one with a comma, a colon, a period, or a real hyphen "-", then retry. ' +
    'Do not swap in another dash-like character, and do not fall back to the "X - Y - Z" ' +
    'dash-parenthetical, which is the same tell in a different costume.'
  );
});

// Collect every banned character with the payload path it sits at, so the deny message points the
// model at the exact field instead of making it re-scan the whole edit.
function walk(node, path, hits, depth) {
  if (depth > 12) return; // cheap guard against pathological nesting

  if (typeof node === 'string') {
    if (BANNED_RE.test(node)) {
      const chars = Object.keys(BANNED).filter((c) => node.includes(c)).map((c) => BANNED[c]);
      hits.push({ path: path || 'input', chars });
    }
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
