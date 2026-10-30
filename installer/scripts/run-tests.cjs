const { spawnSync } = require('node:child_process');
const path = require('node:path');
const result = spawnSync(process.execPath, ['--test', '--test-isolation=none', '--test-reporter=spec', path.join(__dirname, '../test/engine.test.cjs')], { encoding: 'utf8' });
process.stdout.write(result.stdout || ''); process.stderr.write(result.stderr || '');
if (result.status !== 0 && process.env.GITHUB_ACTIONS) {
  const details = ((result.stdout || '') + (result.stderr || '')).replace(/\x1b\[[0-9;]*m/g, '').replace(/%/g, '%25').replace(/\r/g, '%0D').replace(/\n/g, '%0A');
  console.log(`::error title=Installer test failure::${details}`);
}
process.exit(result.status ?? 1);
