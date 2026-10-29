const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

const MIME = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', svg: 'image/svg+xml', webp: 'image/webp' };

// Folders searched for logo.png / logo.jpg / logo.svg, in order:
// next to the portable .exe, next to the installed app, then the app's data folder.
function logoDirs() {
  const dirs = [];
  if (process.env.PORTABLE_EXECUTABLE_DIR) dirs.push(process.env.PORTABLE_EXECUTABLE_DIR);
  dirs.push(app.isPackaged ? path.dirname(process.execPath) : __dirname);
  dirs.push(app.getPath('userData'));
  return dirs;
}

function findLogo() {
  for (const dir of logoDirs()) {
    for (const ext of Object.keys(MIME)) {
      const f = path.join(dir, 'logo.' + ext);
      try {
        if (fs.existsSync(f)) {
          return 'data:' + MIME[ext] + ';base64,' + fs.readFileSync(f).toString('base64');
        }
      } catch (e) { /* try next */ }
    }
  }
  return null;
}

let win;
function createWindow() {
  Menu.setApplicationMenu(null);
  win = new BrowserWindow({
    width: 1360, height: 900, title: 'Safari Invoice',
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true, nodeIntegration: false }
  });
  win.loadFile('index.html');
}

ipcMain.handle('get-logo', () => findLogo());

ipcMain.handle('save-pdf', async (_e, name) => {
  const safe = String(name || 'invoice').replace(/[^\w.-]+/g, '_');
  const res = await dialog.showSaveDialog(win, {
    defaultPath: path.join(app.getPath('documents'), safe + '.pdf'),
    filters: [{ name: 'PDF', extensions: ['pdf'] }]
  });
  if (res.canceled || !res.filePath) return { ok: false };
  const data = await win.webContents.printToPDF({
    pageSize: 'A4', printBackground: true,
    margins: { top: 0, bottom: 0, left: 0, right: 0 }
  });
  fs.writeFileSync(res.filePath, data);
  return { ok: true, path: res.filePath };
});

app.whenReady().then(createWindow);
app.on('window-all-closed', () => app.quit());
