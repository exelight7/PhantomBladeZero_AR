const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const engine = require('../src/engine.cjs');
async function fixture(t) {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'pbz-test-'));
  t.after(() => fs.rm(dir, { recursive: true, force: true }));
  const game = path.join(dir, 'لعبة بمسافات');
  const mods = path.join(game, 'ProjectPBZ', 'Content', 'Paks', '~mods');
  const payload = path.join(dir, 'payload');
  await fs.mkdir(mods, { recursive: true }); await fs.mkdir(payload);
  const files = [];
  for (const name of engine.NAMES) { const data = Buffer.from(`تعريب ${name}`); await fs.writeFile(path.join(payload, name), data); files.push({ name, sha256: engine.sha(data), size: data.length }); }
  await fs.writeFile(path.join(payload, 'manifest.json'), JSON.stringify({ version: '1.0.0', files }));
  await fs.writeFile(path.join(mods, 'another-mod.pak'), 'unrelated mod');
  return { dir, game, mods, payload, files };
}
test('fresh install, repeated install, and removal preserve unrelated mods', async t => {
  const f = await fixture(t);
  await engine.install(f.game, f.payload);
  assert.equal((await engine.status(f.game)).installed, true);
  for (const file of f.files) assert.equal(engine.sha(await fs.readFile(path.join(f.mods, file.name))), file.sha256);
  const state = await fs.readFile(path.join(f.mods, '.exelight7-install.json'));
  assert.equal((await engine.install(f.game, f.payload)).alreadyInstalled, true);
  assert.deepEqual(await fs.readFile(path.join(f.mods, '.exelight7-install.json')), state);
  await engine.uninstall(f.game);
  assert.equal((await engine.status(f.game)).installed, false);
  for (const name of engine.NAMES) await assert.rejects(fs.stat(path.join(f.mods, name)), { code: 'ENOENT' });
  assert.equal(await fs.readFile(path.join(f.mods, 'another-mod.pak'), 'utf8'), 'unrelated mod');
});
test('existing translation files are restored byte for byte', async t => {
  const f = await fixture(t);
  for (const name of engine.NAMES) await fs.writeFile(path.join(f.mods, name), `previous ${name}`);
  const result = await engine.install(path.join(f.game, 'ProjectPBZ'), f.payload);
  assert.equal(path.dirname(path.dirname(result.backup)), await fs.realpath(f.mods));
  assert.equal((await engine.uninstall(f.game)).restored, 4);
  for (const name of engine.NAMES) assert.equal(await fs.readFile(path.join(f.mods, name), 'utf8'), `previous ${name}`);
});
test('corrupt payload is rejected before changing game files', async t => {
  const f = await fixture(t);
  await fs.writeFile(path.join(f.payload, engine.NAMES[2]), 'corrupt');
  await assert.rejects(engine.install(f.game, f.payload), /ناقصة أو تالفة/);
  assert.deepEqual(await fs.readdir(f.mods), ['another-mod.pak']);
});
test('edited files are never silently deleted or replaced', async t => {
  const f = await fixture(t); await engine.install(f.game, f.payload);
  await fs.writeFile(path.join(f.mods, engine.NAMES[2]), 'user edit');
  assert.equal((await engine.status(f.game)).changed, true);
  await assert.rejects(engine.uninstall(f.game), /تغيّر الملف/);
  await assert.rejects(engine.install(f.game, f.payload), /تغيّرت/);
  assert.equal(await fs.readFile(path.join(f.mods, engine.NAMES[2]), 'utf8'), 'user edit');
  for (const name of engine.NAMES) assert.ok((await fs.stat(path.join(f.mods, name))).isFile());
});
test('failed installation rolls back prior replacements and removes new files', async t => {
  const f = await fixture(t); await fs.writeFile(path.join(f.mods, engine.NAMES[0]), 'previous');
  await assert.rejects(engine.install(f.game, f.payload, () => {}, { beforeCopy: i => { if (i === 2) throw new Error('simulated disk failure'); } }), /simulated disk failure/);
  assert.equal(await fs.readFile(path.join(f.mods, engine.NAMES[0]), 'utf8'), 'previous');
  await assert.rejects(fs.stat(path.join(f.mods, engine.NAMES[1])), { code: 'ENOENT' });
  assert.equal((await engine.status(f.game)).installed, false);
  await engine.install(f.game, f.payload); // Lock released after failure.
});
test('failed removal restores the installed state', async t => {
  const f = await fixture(t); await engine.install(f.game, f.payload);
  await assert.rejects(engine.uninstall(f.game, () => {}, { beforeCopy: i => { if (i === 2) throw new Error('simulated failure'); } }), /simulated failure/);
  assert.equal((await engine.status(f.game)).changed, false);
  assert.equal((await engine.status(f.game)).installed, true);
  await engine.uninstall(f.game);
});
test('corrupt backup blocks removal before any installed file changes', async t => {
  const f = await fixture(t); await fs.writeFile(path.join(f.mods, engine.NAMES[2]), 'previous');
  const result = await engine.install(f.game, f.payload);
  await fs.writeFile(path.join(result.backup, engine.NAMES[2]), 'corrupt');
  await assert.rejects(engine.uninstall(f.game), /النسخة الاحتياطية غير سليمة/);
  assert.equal((await engine.status(f.game)).changed, false);
});
test('wrong game directory is rejected', async t => {
  const f = await fixture(t);
  await assert.rejects(engine.install(f.dir, f.payload), /لم يُعثر/);
});
test('symlinked mod files cannot write outside the game', { skip: process.platform === 'win32' }, async t => {
  const f = await fixture(t); const external = path.join(f.dir, 'valuable');
  await fs.writeFile(external, 'keep');
  await fs.symlink(external, path.join(f.mods, engine.NAMES[0]));
  await assert.rejects(engine.install(f.game, f.payload), /رابطًا/);
  assert.equal(await fs.readFile(external, 'utf8'), 'keep');
});
test('manifest traversal and duplicate filenames are rejected', async t => {
  const f = await fixture(t); const manifest = { version: '1.0.0', files: f.files };
  manifest.files[0].name = '../outside';
  await fs.writeFile(path.join(f.payload, 'manifest.json'), JSON.stringify(manifest));
  await assert.rejects(engine.install(f.game, f.payload), /اسم ملف/);
  manifest.files[0].name = manifest.files[1].name;
  await fs.writeFile(path.join(f.payload, 'manifest.json'), JSON.stringify(manifest));
  await assert.rejects(engine.install(f.game, f.payload), /بيانات حزمة/);
});
test('a concurrent installation lock prevents mutation', async t => {
  const f = await fixture(t); await fs.writeFile(path.join(f.mods, '.exelight7.lock'), 'other process');
  await assert.rejects(engine.install(f.game, f.payload), /عملية تثبيت أخرى/);
  assert.equal(await fs.readFile(path.join(f.mods, '.exelight7.lock'), 'utf8'), 'other process');
});
test('unmanaged manual installations are not removed', async t => {
  const f = await fixture(t); await fs.writeFile(path.join(f.mods, engine.NAMES[0]), 'manual');
  await assert.rejects(engine.uninstall(f.game), /لا يوجد تثبيت/);
  assert.equal(await fs.readFile(path.join(f.mods, engine.NAMES[0]), 'utf8'), 'manual');
});
