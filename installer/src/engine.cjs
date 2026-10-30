const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const NAMES = ['3BADIOH_P.pak', '3BADIOH_P.utoc', '3BADIOH_P.ucas', 'ZZZ_3BADIOH_Fix_P.pak'];
const STATE = '.exelight7-install.json';
const sha = data => crypto.createHash('sha256').update(data).digest('hex');

async function exists(file) { try { await fs.lstat(file); return true; } catch (e) { if (e.code === 'ENOENT') return false; throw e; } }
async function ordinary(file, directory = false) {
  const s = await fs.lstat(file);
  if (s.isSymbolicLink() || (directory ? !s.isDirectory() : !s.isFile())) throw new Error('المسار يحتوي رابطًا أو نوع ملف غير متوقع. اختر مجلد اللعبة الفعلي.');
}
async function location(selected) {
  let root = await fs.realpath(selected);
  if (path.basename(root).toLowerCase() === 'projectpbz') root = path.dirname(root);
  let current = root;
  for (const part of ['ProjectPBZ', 'Content', 'Paks']) {
    current = path.join(current, part);
    try { await ordinary(current, true); } catch { throw new Error('لم يُعثر على ProjectPBZ/Content/Paks. اختر مجلد اللعبة من «تصفّح الملفات المحلية» في Steam.'); }
  }
  const mods = path.join(current, '~mods');
  if (await exists(mods)) await ordinary(mods, true);
  return { root, mods };
}
async function verifiedPayload(payload) {
  const manifest = JSON.parse(await fs.readFile(path.join(payload, 'manifest.json'), 'utf8'));
  if (manifest.version !== '1.0.0' || manifest.files?.length !== NAMES.length || new Set(manifest.files.map(f => f.name)).size !== NAMES.length) throw new Error('بيانات حزمة التثبيت غير صالحة.');
  for (const f of manifest.files) {
    if (!NAMES.includes(f.name) || !/^[a-f0-9]{64}$/.test(f.sha256)) throw new Error('اسم ملف غير صالح في حزمة التثبيت.');
    const data = await fs.readFile(path.join(payload, f.name));
    if (data.length !== f.size || sha(data) !== f.sha256) throw new Error('ملفات التطبيق ناقصة أو تالفة. أعد تنزيله من صفحة الإصدار.');
  }
  return manifest;
}
async function readState(mods) {
  const target = path.join(mods, STATE);
  if (!await exists(target)) return null;
  await ordinary(target);
  const s = JSON.parse(await fs.readFile(target, 'utf8'));
  if (s.schema !== 1 || typeof s.backup !== 'string' || !/^[a-f0-9-]{36}$/.test(s.backup) || !Array.isArray(s.files) || s.files.length !== 4 || new Set(s.files.map(f => f.name)).size !== 4) throw new Error('سجل التثبيت غير صالح؛ لن يتم تغيير الملفات.');
  for (const f of s.files) if (!NAMES.includes(f.name) || !/^[a-f0-9]{64}$/.test(f.sha256) || (f.previous !== null && !/^[a-f0-9]{64}$/.test(f.previous))) throw new Error('سجل النسخة الاحتياطية غير صالح.');
  return s;
}
async function status(selected) {
  const place = await location(selected);
  const state = await readState(place.mods);
  let changed = false;
  if (state) for (const f of state.files) {
    const p = path.join(place.mods, f.name);
    if (!await exists(p)) { changed = true; continue; }
    await ordinary(p);
    if (sha(await fs.readFile(p)) !== f.sha256) changed = true;
  }
  return { root: place.root, installed: Boolean(state), version: state?.version, changed };
}
async function locked(mods, work) {
  await fs.mkdir(mods, { recursive: true });
  await ordinary(mods, true);
  const p = path.join(mods, '.exelight7.lock');
  let lock;
  try { lock = await fs.open(p, 'wx'); } catch (e) { if (e.code === 'EEXIST') throw new Error('هناك عملية تثبيت أخرى، أو سجل قفل من عملية انقطعت. راجع تعليمات استعادة التثبيت.'); throw e; }
  try { await lock.writeFile(String(process.pid)); return await work(); }
  finally { await lock.close(); await fs.unlink(p); }
}
async function ensureBackupParent(mods) {
  const parent = path.join(mods, '.exelight7-backups');
  if (await exists(parent)) await ordinary(parent, true);
  else await fs.mkdir(parent);
  return parent;
}
async function install(selected, payload, progress = () => {}, hooks = {}) {
  const manifest = await verifiedPayload(payload);
  const { root, mods } = await location(selected);
  return locked(mods, async () => {
    const previousState = await readState(mods);
    if (previousState) {
      const s = await status(root);
      if (s.changed) throw new Error('تغيّرت بعض ملفات التعريب بعد التثبيت. احتفظ بنسخة منها وراجع سجل التثبيت قبل المتابعة.');
      if (previousState.version === manifest.version && previousState.files.every(f => manifest.files.some(m => m.name === f.name && m.sha256 === f.sha256))) return { alreadyInstalled: true, version: manifest.version };
      throw new Error('أزل النسخة المثبّتة من هذا التطبيق قبل تثبيت نسخة مختلفة.');
    }
    const backup = crypto.randomUUID();
    const parent = await ensureBackupParent(mods);
    const backupDir = path.join(parent, backup);
    const stage = path.join(mods, `.exelight7-stage-${backup}`);
    await fs.mkdir(backupDir);
    await fs.mkdir(stage);
    const records = [];
    const written = [];
    let committed = false;
    try {
      for (let i = 0; i < manifest.files.length; i++) {
        const f = manifest.files[i];
        const target = path.join(mods, f.name);
        let previous = null;
        if (await exists(target)) {
          await ordinary(target);
          previous = sha(await fs.readFile(target));
          await fs.copyFile(target, path.join(backupDir, f.name));
          if (sha(await fs.readFile(path.join(backupDir, f.name))) !== previous) throw new Error('تعذّر التحقق من النسخة الاحتياطية.');
        }
        records.push({ ...f, previous });
        await fs.copyFile(path.join(payload, f.name), path.join(stage, f.name));
        if (sha(await fs.readFile(path.join(stage, f.name))) !== f.sha256) throw new Error('تعذّر التحقق من الملف المنسوخ.');
        progress({ percent: (i + 1) * 10, message: 'التحقق من الملفات وحفظ النسخة الاحتياطية…' });
      }
      const state = { schema: 1, version: manifest.version, backup, files: records };
      await fs.writeFile(path.join(backupDir, 'recovery.json'), JSON.stringify(state, null, 2));
      for (let i = 0; i < records.length; i++) {
        const f = records[i];
        if (hooks.beforeCopy) await hooks.beforeCopy(i);
        written.push(f);
        await fs.copyFile(path.join(stage, f.name), path.join(mods, f.name));
        if (sha(await fs.readFile(path.join(mods, f.name))) !== f.sha256) throw new Error('تعذّر التحقق من ملف اللعبة بعد نسخه.');
        progress({ percent: 50 + (i + 1) * 10, message: 'تثبيت التعريب…' });
      }
      await fs.writeFile(path.join(stage, STATE), JSON.stringify(state, null, 2));
      await fs.rename(path.join(stage, STATE), path.join(mods, STATE));
      committed = true;
      progress({ percent: 100, message: 'اكتمل تثبيت التعريب' });
      return { version: manifest.version, backup: backupDir };
    } catch (error) {
      const failures = [];
      for (const f of written.reverse()) {
        try { if (f.previous) await fs.copyFile(path.join(backupDir, f.name), path.join(mods, f.name)); else await fs.rm(path.join(mods, f.name), { force: true }); }
        catch { failures.push(f.name); }
      }
      if (failures.length) throw new Error(`توقّف التثبيت وتعذّرت استعادة بعض الملفات. النسخة الاحتياطية في: ${backupDir}`);
      throw error;
    } finally {
      await fs.rm(stage, { recursive: true, force: true });
      // Keep recovery data after failures or successful installation.
      if (!committed) progress({ percent: 0, message: 'توقّف التثبيت؛ تمت محاولة استعادة الملفات السابقة.' });
    }
  });
}
async function uninstall(selected, progress = () => {}, hooks = {}) {
  const { mods } = await location(selected);
  return locked(mods, async () => {
    const state = await readState(mods);
    if (!state) throw new Error('لا يوجد تثبيت مسجّل بهذا التطبيق. لا تُحذف ملفات التعريب اليدوي تلقائيًا.');
    const parent = await ensureBackupParent(mods);
    const backup = path.join(parent, state.backup);
    await ordinary(backup, true);
    const current = new Map();
    for (const f of state.files) {
      const target = path.join(mods, f.name);
      await ordinary(target);
      const bytes = await fs.readFile(target);
      if (sha(bytes) !== f.sha256) throw new Error(`تغيّر الملف ${f.name} بعد التثبيت. لن يُحذف حفاظًا على تعديلك.`);
      current.set(f.name, bytes);
      if (f.previous) {
        await ordinary(path.join(backup, f.name));
        if (sha(await fs.readFile(path.join(backup, f.name))) !== f.previous) throw new Error('النسخة الاحتياطية غير سليمة. لن تُحذف ملفات التعريب.');
      }
    }
    const changed = [];
    try {
      for (let i = 0; i < state.files.length; i++) {
        const f = state.files[i];
        if (hooks.beforeCopy) await hooks.beforeCopy(i);
        changed.push(f.name);
        if (f.previous) await fs.copyFile(path.join(backup, f.name), path.join(mods, f.name));
        else await fs.unlink(path.join(mods, f.name));
        progress({ percent: (i + 1) * 25, message: 'استعادة الملفات السابقة…' });
      }
      await fs.unlink(path.join(mods, STATE));
    } catch (error) {
      try { for (const name of changed) await fs.writeFile(path.join(mods, name), current.get(name)); }
      catch { throw new Error(`تعذّر إكمال الاستعادة. النسخة الاحتياطية في: ${backup}`); }
      throw error;
    }
    return { restored: state.files.filter(f => f.previous).length, backup };
  });
}
module.exports = { NAMES, location, verifiedPayload, status, install, uninstall, sha };
