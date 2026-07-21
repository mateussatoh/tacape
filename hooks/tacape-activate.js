#!/usr/bin/env node
// tacape - SessionStart activation hook.
//
// 1. Resolves the active level (env > mode file > default "full")
// 2. Writes the flag file the statusline reads
// 3. Emits skills/tacape/SKILL.md as SessionStart context, filtered to the active level
//
// SKILL.md is the single source of truth. Editing it propagates here with no duplication.

const fs = require('fs');
const path = require('path');
const os = require('os');

const LEVELS = new Set(['lite', 'full', 'ultra']);
const DEFAULT_LEVEL = 'full';

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const modePath = path.join(claudeDir, '.tacape-mode');

// Returns the source too: an env override is documented as per-session, so it must never be
// written back to the mode file. One `TACAPE_LEVEL=ultra claude` would otherwise change the
// user's default for every future session.
function readLevel() {
  const fromEnv = (process.env.TACAPE_LEVEL || '').trim().toLowerCase();
  if (fromEnv === 'off' || LEVELS.has(fromEnv)) return { level: fromEnv, source: 'env' };

  try {
    const fromFile = fs.readFileSync(modePath, 'utf8').trim().toLowerCase();
    if (fromFile === 'off' || LEVELS.has(fromFile)) return { level: fromFile, source: 'file' };
  } catch (e) { /* no mode file yet */ }

  return { level: DEFAULT_LEVEL, source: 'default' };
}

const { level, source } = readLevel();

if (level === 'off') {
  process.stdout.write('');
  process.exit(0);
}

// Persist the resolved level so the statusline and the next session agree, but never persist an
// env override: it is documented as lasting one session.
// Symlink-safe: never follow a symlink out of the config dir.
if (source !== 'env') {
  try {
    if (!fs.existsSync(modePath) || !fs.lstatSync(modePath).isSymbolicLink()) {
      fs.writeFileSync(modePath, level, 'utf8');
    }
  } catch (e) { /* non-fatal, never block session start */ }
}

let body = '';
try {
  const raw = fs.readFileSync(
    path.join(__dirname, '..', 'skills', 'tacape', 'SKILL.md'),
    'utf8'
  );
  body = raw.replace(/^---[\s\S]*?---\s*/, '');
} catch (e) {
  process.stdout.write(
    'TACAPE ACTIVE - level: ' + level + '\n\n' +
    'Terse output. Lead with the next action. Number multi-step work. End with one concrete ' +
    'next step. Drop articles, filler, hedging, preamble and closers. Zero U+2014 em dash ' +
    'anywhere. Plain full sentences for security warnings and irreversible actions. ' +
    'Off only on "stop tacape" or "normal mode".'
  );
  process.exit(0);
}

// Keep only the active level's intensity row and its matching example line.
const filtered = body.split('\n').filter((line) => {
  const row = line.match(/^\|\s*\*\*(\S+?)\*\*\s*\|/);
  if (row) return row[1] === level;

  const example = line.match(/^- (\S+?):\s/);
  if (example && LEVELS.has(example[1])) return example[1] === level;

  return true;
});

let output = 'TACAPE ACTIVE - level: ' + level + '\n\n' + filtered.join('\n');

// Offer the statusline once, when no statusline is configured at all.
// Never overwrite an existing one: the user may have built their own.
try {
  const settingsPath = path.join(claudeDir, 'settings.json');
  const settings = fs.existsSync(settingsPath)
    ? JSON.parse(fs.readFileSync(settingsPath, 'utf8'))
    : {};

  if (!settings.statusLine) {
    const script = path.join(__dirname, 'tacape-statusline.sh');
    const command = 'bash "' + script + '"';
    output +=
      '\n\nSTATUSLINE AVAILABLE: tacape ships a statusline showing the active level, the ' +
      'directory, the git branch and the model. No statusline is configured yet. To enable it, ' +
      'add this to ' + settingsPath + ': "statusLine": { "type": "command", "command": ' +
      JSON.stringify(command) + ' }. Offer this to the user once, then drop it.';
  }
} catch (e) { /* never block session start over the statusline */ }

process.stdout.write(output);
