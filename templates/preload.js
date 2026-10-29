const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('api', {
  getLogo: () => ipcRenderer.invoke('get-logo'),
  savePdf: (name) => ipcRenderer.invoke('save-pdf', name)
});
