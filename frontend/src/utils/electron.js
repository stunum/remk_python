/**
 * Electron API 封装
 * 提供统一的接口调用 Electron 功能
 */

/**
 * 检查是否在 Electron 环境中运行
 */
export const isElectron = () => {
  return window.electronAPI?.isElectron || false;
};

/**
 * 应用相关 API
 */
export const electronApp = {
  /**
   * 退出应用
   */
  quit: async () => {
    if (isElectron()) {
      return await window.electronAPI.app.quit();
    }
    console.warn('当前不在 Electron 环境中');
  },

  /**
   * 获取应用版本
   */
  getVersion: async () => {
    if (isElectron()) {
      return await window.electronAPI.app.version();
    }
    return 'Web版本';
  },

  /**
   * 获取应用路径
   * @param {string} name - 路径名称 (home, appData, userData, temp, etc.)
   */
  getPath: async (name) => {
    if (isElectron()) {
      return await window.electronAPI.app.getPath(name);
    }
    return null;
  },
};

/**
 * 对话框 API
 */
export const electronDialog = {
  /**
   * 显示保存对话框
   * @param {Object} options - 对话框选项
   */
  showSaveDialog: async (options) => {
    if (isElectron()) {
      return await window.electronAPI.dialog.showSaveDialog(options);
    }
    console.warn('当前不在 Electron 环境中');
    return { canceled: true };
  },

  /**
   * 显示打开对话框
   * @param {Object} options - 对话框选项
   */
  showOpenDialog: async (options) => {
    if (isElectron()) {
      return await window.electronAPI.dialog.showOpenDialog(options);
    }
    console.warn('当前不在 Electron 环境中');
    return { canceled: true };
  },

  /**
   * 显示消息框
   * @param {Object} options - 对话框选项
   */
  showMessageBox: async (options) => {
    if (isElectron()) {
      return await window.electronAPI.dialog.showMessageBox(options);
    }
    console.warn('当前不在 Electron 环境中');
    // 使用浏览器的 alert/confirm
    if (options.type === 'question') {
      return { response: confirm(options.message) ? 0 : 1 };
    }
    alert(options.message);
    return { response: 0 };
  },
};

/**
 * 窗口控制 API
 */
export const electronWindow = {
  /**
   * 最小化窗口
   */
  minimize: async () => {
    if (isElectron()) {
      return await window.electronAPI.window.minimize();
    }
  },

  /**
   * 最大化/还原窗口
   */
  maximize: async () => {
    if (isElectron()) {
      return await window.electronAPI.window.maximize();
    }
  },

  /**
   * 关闭窗口
   */
  close: async () => {
    if (isElectron()) {
      return await window.electronAPI.window.close();
    }
  },

  /**
   * 检查窗口是否最大化
   */
  isMaximized: async () => {
    if (isElectron()) {
      return await window.electronAPI.window.isMaximized();
    }
    return false;
  },
};

/**
 * 平台信息
 */
export const platform = () => {
  if (isElectron()) {
    return window.electronAPI.platform;
  }
  return navigator.platform;
};

/**
 * 统一导出
 */
export default {
  isElectron,
  app: electronApp,
  dialog: electronDialog,
  window: electronWindow,
  platform,
};

