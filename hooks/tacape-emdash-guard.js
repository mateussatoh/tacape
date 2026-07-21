#!/usr/bin/env node
// tacape - PreToolUse guard. Denies any Write/Edit/NotebookEdit whose payload contains U+2014.
//
// A prompt rule drifts after enough turns. This does not. The character never reaches disk.
// Escape hatch: TACAPE_ALLOW_EMDASH=1 (for repos that legitimately need it, e.g. quoting a source).

// Escape sequence, not the literal character: this file must survive its own guard.
const EM_DASH = '\u2014';

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { raw += chunk; });
process.stdin.on('end', () => {
  if (process.env.TACAPE_ALLOW_EMDASH === '1') return allow();

  let payload;
  try {
    payload = JSON.parse(raw);
  } catch (e) {
    return allow(); // never block on a parse failure
  }

  const input = payload.tool_input || {};

  // Only the fields that actually carry content to disk.
  const fields = ['content', 'new_string', 'new_source'];
  const offending = fields.filter(
    (f) => typeof input[f] === 'string' && input[f].includes(EM_DASH)
  );

  if (offending.length === 0) return allow();

  const filePath = input.file_path || input.notebook_path || 'the target file';

  deny(
    'Blocked by tacape: the ' + offending.join(' and ') + ' payload contains U+2014 (em dash). ' +
    'House rule bans that character in every written artifact, including ' + filePath + '. ' +
    'Replace each one with a comma, a colon, a period, or a real hyphen, then retry. ' +
    'Do not substitute the "X - Y - Z" dash-parenthetical pattern, it is the same tell.'
  );
});

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
      permissionDecisionReason: reason
    }
  }));
  process.exit(0);
}
