// Run with Electron under Xvfb, or --ozone-platform=headless in a cloud machine.
const { app, BrowserWindow, dialog } = require('electron');
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const assert = require('node:assert/strict');
let temp;
const timeout = setTimeout(() => { console.error('UI smoke test timed out'); app.exit(1); }, 45000);
async function poll(window, expression) {
  for (let i = 0; i < 200; i++) {
    if (await window.webContents.executeJavaScript(expression)) return;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error(`UI did not reach expected state: ${expression}`);
}
(async () => {
  temp = await fs.mkdtemp(path.join(os.tmpdir(), 'pbz-ui-'));
  app.setPath('userData', path.join(temp, 'profile'));
  const game = path.join(temp, 'Phantom Blade Zero');
  const mods = path.join(game, 'ProjectPBZ/Content/Paks/~mods');
  await fs.mkdir(mods, { recursive: true });
  await fs.writeFile(path.join(mods, 'untouched.pak'), 'another mod');
  dialog.showOpenDialog = async () => ({ canceled: false, filePaths: [game] });
  dialog.showMessageBox = async () => ({ response: 0 });
  app.on('browser-window-created', (_event, window) => {
    window.webContents.once('did-finish-load', async () => {
      try {
        assert.equal(await window.webContents.executeJavaScript('typeof window.installer.choose'), 'function');
        assert.equal(await window.webContents.executeJavaScript("document.querySelector('#install').disabled"), true);
        const capture = process.env.PBZ_SCREENSHOT || path.join(temp, 'installer.png');
        await fs.writeFile(capture, (await window.webContents.capturePage()).toPNG());
        console.log(`Screenshot: ${capture}`);
        await window.webContents.executeJavaScript("document.querySelector('#choose').click()");
        await poll(window, "!document.querySelector('#install').disabled");
        await window.webContents.executeJavaScript("document.querySelector('#install').click()");
        await poll(window, "!document.querySelector('#success').hidden && !document.querySelector('#uninstall').disabled");
        const record = JSON.parse(await fs.readFile(path.join(mods, '.exelight7-install.json')));
        assert.equal(record.files.length, 4);
        await window.webContents.executeJavaScript("document.querySelector('#uninstall').click()");
        await poll(window, "!document.querySelector('#install').disabled && document.querySelector('#uninstall').disabled");
        assert.equal(await fs.readFile(path.join(mods, 'untouched.pak'), 'utf8'), 'another mod');
        for (const f of record.files) await assert.rejects(fs.stat(path.join(mods, f.name)), { code: 'ENOENT' });
        console.log('PASS: isolated preload bridge, folder selection, real payload installation, removal, unrelated mod preservation');
        clearTimeout(timeout); await fs.rm(temp, { recursive: true, force: true }); app.exit(0);
      } catch (error) { console.error(error); clearTimeout(timeout); app.exit(1); }
    });
  });
  require('../src/main.cjs');
})().catch(error => { console.error(error); clearTimeout(timeout); app.exit(1); });
