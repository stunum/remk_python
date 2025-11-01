/**
 * Electron 预加载脚本
 * 在渲染进程中暴露安全的 API
 */

import { contextBridge, ipcRenderer } from 'electron';

/**
 * 暴露给渲染进程的 API
 */
contextBridge.exposeInMainWorld('electronAPI', {
  // 应用相关
  app: {
    quit: () => ipcRenderer.invoke('app:quit'),
    version: () => ipcRenderer.invoke('app:version'),
    getPath: (name) => ipcRenderer.invoke('app:path', name),
  },

  // 对话框
  dialog: {
    showSaveDialog: (options) => ipcRenderer.invoke('dialog:showSaveDialog', options),
    showOpenDialog: (options) => ipcRenderer.invoke('dialog:showOpenDialog', options),
    showMessageBox: (options) => ipcRenderer.invoke('dialog:showMessageBox', options),
  },

  // 窗口控制
  window: {
    minimize: () => ipcRenderer.invoke('window:minimize'),
    maximize: () => ipcRenderer.invoke('window:maximize'),
    close: () => ipcRenderer.invoke('window:close'),
    isMaximized: () => ipcRenderer.invoke('window:isMaximized'),
  },

  // 环境信息
  platform: process.platform,
  isElectron: true,
});

/**
 * 日志输出
 */
console.log('Electron 预加载脚本已加载');
console.log('Platform:', process.platform);
console.log('Node 版本:', process.versions.node);
console.log('Electron 版本:', process.versions.electron);

