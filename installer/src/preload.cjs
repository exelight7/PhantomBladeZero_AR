const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('installer', {
  choose: () => ipcRenderer.invoke('choose'),
  detect: () => ipcRenderer.invoke('detect'),
  operate: action => ipcRenderer.invoke('operate', action),
  onProgress: callback => { ipcRenderer.on('progress', (_event, value) => callback(value)); }
});
