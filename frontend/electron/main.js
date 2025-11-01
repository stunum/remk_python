/**
 * Electron 主进程
 * 负责创建窗口、管理应用生命周期
 */

import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 开发环境判断
const isDevelopment = process.env.NODE_ENV === 'development';

// 主窗口引用
let mainWindow = null;

/**
 * 创建主窗口
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 768,
    title: '瑞尔明康眼底检查系统',
    icon: join(__dirname, '../build/icon.png'),
    webPreferences: {
      preload: join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true,
      // 允许使用本地资源
      allowRunningInsecureContent: false,
    },
    // 窗口样式
    frame: true,
    backgroundColor: '#ffffff',
    show: false, // 先隐藏，等待加载完成
  });

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.focus();
  });

  // 加载应用
  if (isDevelopment) {
    // 开发环境：加载 Vite 开发服务器
    mainWindow.loadURL('http://localhost:5173');
    // 打开开发者工具
    mainWindow.webContents.openDevTools();
  } else {
    // 生产环境：加载打包后的文件
    mainWindow.loadFile(join(__dirname, '../dist/index.html'));
  }

  // 窗口关闭事件
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // 处理外部链接（在默认浏览器中打开）
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http://') || url.startsWith('https://')) {
      require('electron').shell.openExternal(url);
    }
    return { action: 'deny' };
  });
}

/**
 * 应用启动
 */
app.whenReady().then(() => {
  createWindow();

  // macOS 特性：点击 Dock 图标时重新创建窗口
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

/**
 * 所有窗口关闭时退出应用（macOS 除外）
 */
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

/**
 * 应用退出前的清理工作
 */
app.on('before-quit', () => {
  console.log('应用即将退出，执行清理工作...');
  // 在这里可以执行清理操作，比如保存状态、关闭连接等
});

/**
 * IPC 通信处理
 */

// 退出应用
ipcMain.handle('app:quit', () => {
  app.quit();
});

// 获取应用版本
ipcMain.handle('app:version', () => {
  return app.getVersion();
});

// 获取应用路径
ipcMain.handle('app:path', (event, name) => {
  return app.getPath(name);
});

// 显示保存对话框
ipcMain.handle('dialog:showSaveDialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result;
});

// 显示打开对话框
ipcMain.handle('dialog:showOpenDialog', async (event, options) => {
  const result = await dialog.openDialog(mainWindow, options);
  return result;
});

// 显示消息框
ipcMain.handle('dialog:showMessageBox', async (event, options) => {
  const result = await dialog.showMessageBox(mainWindow, options);
  return result;
});

// 最小化窗口
ipcMain.handle('window:minimize', () => {
  if (mainWindow) {
    mainWindow.minimize();
  }
});

// 最大化/还原窗口
ipcMain.handle('window:maximize', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
});

// 关闭窗口
ipcMain.handle('window:close', () => {
  if (mainWindow) {
    mainWindow.close();
  }
});

// 检查窗口是否最大化
ipcMain.handle('window:isMaximized', () => {
  return mainWindow ? mainWindow.isMaximized() : false;
});

/**
 * 错误处理
 */
process.on('uncaughtException', (error) => {
  console.error('未捕获的异常:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('未处理的 Promise 拒绝:', promise, '原因:', reason);
});

/**
 * 日志输出
 */
console.log('Electron 应用启动');
console.log('Node 版本:', process.versions.node);
console.log('Electron 版本:', process.versions.electron);
console.log('Chrome 版本:', process.versions.chrome);
console.log('应用版本:', app.getVersion());
console.log('开发模式:', isDevelopment);

