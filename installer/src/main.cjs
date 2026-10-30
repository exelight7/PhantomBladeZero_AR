const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('node:path');
const fs = require('node:fs/promises');
const os = require('node:os');
const engine = require('./engine.cjs');
let window, selected = null, busy = false;
const payload = () => app.isPackaged ? path.join(process.resourcesPath, 'payload') : path.join(__dirname, '..', 'payload');
function progress(value) { if (!window.isDestroyed()) window.webContents.send('progress', value); }
function friendly(error) {
  if (error.code === 'EACCES' || error.code === 'EPERM') return 'لا توجد صلاحية للكتابة في مجلد اللعبة. اختر مجلدًا يمكنك تعديله، أو شغّل التطبيق بصلاحية مناسبة.';
  if (error.code === 'ENOSPC') return 'المساحة الحرة غير كافية. أفرغ مساحة للملفات والنسخة الاحتياطية ثم أعد المحاولة.';
  if (error.code === 'ENOENT') return 'أحد الملفات المطلوبة غير موجود. تحقق من مجلد اللعبة وملفات التطبيق.';
  return error.message;
}
function handle(name, fn) { ipcMain.handle(name, async (event, ...args) => {
  if (event.sender !== window.webContents) return { error: 'طلب غير مسموح.' };
  try { return { data: await fn(...args) }; } catch (error) { return { error: friendly(error) }; }
}); }
async function steamCandidates() {
  const bases = process.platform === 'win32'
    ? [path.join(process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)', 'Steam'), path.join(process.env.ProgramFiles || 'C:\\Program Files', 'Steam')]
    : [path.join(os.homedir(), '.steam/steam'), path.join(os.homedir(), '.local/share/Steam'), path.join(os.homedir(), '.var/app/com.valvesoftware.Steam/.local/share/Steam')];
  const libraries = new Set(bases);
  for (const base of bases) {
    try {
      const vdf = await fs.readFile(path.join(base, 'steamapps/libraryfolders.vdf'), 'utf8');
      for (const match of vdf.matchAll(/"path"\s+"([^"\n]+)"/g)) libraries.add(match[1].replace(/\\\\/g, '\\'));
    } catch {}
  }
  const found = new Set();
  for (const library of libraries) {
    const common = path.join(library, 'steamapps/common');
    try { for (const name of await fs.readdir(common)) {
      try { const place = await engine.location(path.join(common, name)); found.add(place.root); } catch {}
    } } catch {}
  }
  return [...found];
}
handle('choose', async () => {
  if (busy) throw new Error('انتظر اكتمال العملية الحالية.');
  const result = await dialog.showOpenDialog(window, { title: 'اختيار مجلد Phantom Blade Zero', properties: ['openDirectory'] });
  if (result.canceled) return null;
  const state = await engine.status(result.filePaths[0]); selected = state.root; return state;
});
handle('detect', async () => {
  if (busy) throw new Error('انتظر اكتمال العملية الحالية.');
  const found = await steamCandidates();
  if (!found.length) throw new Error('لم نعثر على اللعبة في مكتبات Steam. استخدم «اختيار المجلد» لتحديد موقعها يدويًا.');
  if (found.length > 1) throw new Error('عُثر على أكثر من نسخة للعبة. اختر النسخة المطلوبة يدويًا.');
  const state = await engine.status(found[0]); selected = state.root; return state;
});
handle('operate', async action => {
  if (!['install', 'uninstall'].includes(action) || !selected || busy) throw new Error('اختر مجلد اللعبة وانتظر اكتمال أي عملية جارية.');
  busy = true;
  try {
    const result = await dialog.showMessageBox(window, {
      type: 'question', title: action === 'install' ? 'تثبيت التعريب' : 'استعادة الملفات السابقة',
      message: action === 'install' ? 'أغلق اللعبة قبل المتابعة. سيتم نسخ ملفات التعريب وحفظ نسخة احتياطية من الملفات المستبدلة.' : 'ستُزال الملفات التي ثبّتها التطبيق وتُستعاد الملفات السابقة من النسخة الاحتياطية.',
      detail: selected, buttons: ['متابعة', 'إلغاء'], defaultId: 1, cancelId: 1, noLink: true
    });
    if (result.response !== 0) return { canceled: true };
    const value = action === 'install' ? await engine.install(selected, payload(), progress) : await engine.uninstall(selected, progress);
    return { ...value, state: await engine.status(selected) };
  } finally { busy = false; }
});
if (!app.requestSingleInstanceLock()) app.quit();
else {
  app.on('second-instance', () => { if (window) { if (window.isMinimized()) window.restore(); window.focus(); } });
  app.whenReady().then(() => {
    window = new BrowserWindow({ width: 1180, height: 820, minWidth: 920, minHeight: 720, backgroundColor: '#101718', title: 'Phantom Blade Zero — العربية', icon: path.join(__dirname, '../assets/icon.png'), autoHideMenuBar: true, webPreferences: { preload: path.join(__dirname, 'preload.cjs'), contextIsolation: true, nodeIntegration: false, sandbox: true } });
    window.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
    window.webContents.on('will-navigate', event => event.preventDefault());
    window.on('close', event => { if (busy) { event.preventDefault(); progress({ percent: null, message: 'يرجى الانتظار حتى تنتهي العملية قبل إغلاق التطبيق.' }); } });
    window.loadFile(path.join(__dirname, 'index.html'));
  });
  app.on('window-all-closed', () => app.quit());
}
