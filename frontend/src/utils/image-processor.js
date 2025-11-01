/**
 * 图片处理工具类
 * 提供缩放、旋转、翻转、裁剪、标记等功能
 */

export class ImageProcessor {
  constructor() {
    this.canvas = null;
    this.ctx = null;
    this.originalImage = null;
    this.currentImage = null;
    this.history = [];
    this.historyIndex = -1;
    this.maxHistorySize = 20;
  }

  /**
   * 初始化canvas
   */
  initCanvas(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.ctx.imageSmoothingEnabled = true;
    this.ctx.imageSmoothingQuality = 'high';
  }

  /**
   * 加载图片
   */
  async loadImage(src, skipHistory = false, isStreaming = false) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      
      img.onload = () => {
        this.originalImage = img;
        
        // 性能优化：流媒体模式下跳过图像克隆
        if (isStreaming) {
          this.currentImage = img; // 直接使用原图，避免克隆开销
        } else {
          this.currentImage = this.cloneImage(img);
        }
        
        // 性能优化：流媒体模式下跳过历史记录
        if (!skipHistory) {
          this.saveToHistory('加载图片');
        }
        
        // 立即绘制图片
        this.drawImage(this.currentImage, false); // 流媒体模式不显示调试网格
        
        resolve(img);
      };
      
      img.onerror = (error) => {
        reject(error);
      };
      
      img.src = src;
    });
  }

  /**
   * 克隆图片到canvas
   */
  cloneImage(img) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = img.width || img.naturalWidth;
    canvas.height = img.height || img.naturalHeight;
    
    if (img instanceof HTMLImageElement) {
      ctx.drawImage(img, 0, 0);
    } else if (img instanceof HTMLCanvasElement) {
      ctx.drawImage(img, 0, 0);
    }
    
    return canvas;
  }

  /**
   * 绘制图片到主canvas
   */
  drawImage(img = this.currentImage, showDebugGrid = false) {
    if (!this.canvas || !img) {
      return;
    }
    
    // 清空canvas
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // 性能优化：只在需要时绘制调试网格
    if (showDebugGrid) {
      // 绘制测试背景
      this.ctx.fillStyle = '#f0f0f0';
      this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
      
      // 绘制网格
      this.ctx.strokeStyle = '#e0e0e0';
      this.ctx.lineWidth = 1;
      for (let x = 0; x < this.canvas.width; x += 50) {
        this.ctx.beginPath();
        this.ctx.moveTo(x, 0);
        this.ctx.lineTo(x, this.canvas.height);
        this.ctx.stroke();
      }
      for (let y = 0; y < this.canvas.height; y += 50) {
        this.ctx.beginPath();
        this.ctx.moveTo(0, y);
        this.ctx.lineTo(this.canvas.width, y);
        this.ctx.stroke();
      }
    }
    
    // 计算适配尺寸（用于显示）
    // 注意：这里的缩放仅用于显示效果，不影响保存的原始图片数据
    const scale = this.calculateFitScale(img, this.canvas);
    const drawWidth = img.width * scale;
    const drawHeight = img.height * scale;
    const x = (this.canvas.width - drawWidth) / 2;
    const y = (this.canvas.height - drawHeight) / 2;
    
    // 绘制图片（使用高质量渲染）
    this.ctx.imageSmoothingEnabled = true;
    this.ctx.imageSmoothingQuality = 'high';
    this.ctx.drawImage(img, x, y, drawWidth, drawHeight);
  }

  /**
   * 计算适配缩放比例
   */
  calculateFitScale(img, container) {
    if (container.width <= 0 || container.height <= 0) {
      console.warn('Container has invalid size:', container.width, container.height);
      return 1; // 返回默认缩放比例
    }
    
    const scaleX = container.width / img.width;
    const scaleY = container.height / img.height;
    const scale = Math.min(scaleX, scaleY);
    
    // 确保最小缩放比例，避免图片太小看不见
    return Math.max(scale, 0.1);
  }

  /**
   * 缩放图片
   */
  scale(factor) {
    if (!this.currentImage) return;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = this.currentImage.width * factor;
    canvas.height = this.currentImage.height * factor;
    
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(this.currentImage, 0, 0, canvas.width, canvas.height);
    
    this.currentImage = canvas;
    this.drawImage();
    this.saveToHistory(`缩放 ${(factor * 100).toFixed(0)}%`);
  }

  /**
   * 旋转图片
   */
  rotate(angle) {
    if (!this.currentImage) return;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // 计算旋转后的尺寸
    const rad = (angle * Math.PI) / 180;
    const sin = Math.abs(Math.sin(rad));
    const cos = Math.abs(Math.cos(rad));
    
    canvas.width = this.currentImage.width * cos + this.currentImage.height * sin;
    canvas.height = this.currentImage.width * sin + this.currentImage.height * cos;
    
    // 设置旋转中心
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.rotate(rad);
    
    // 绘制图片
    ctx.drawImage(
      this.currentImage,
      -this.currentImage.width / 2,
      -this.currentImage.height / 2
    );
    
    this.currentImage = canvas;
    this.drawImage();
    this.saveToHistory(`旋转 ${angle}°`);
  }

  /**
   * 水平翻转
   */
  flipHorizontal() {
    if (!this.currentImage) return;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = this.currentImage.width;
    canvas.height = this.currentImage.height;
    
    ctx.scale(-1, 1);
    ctx.drawImage(this.currentImage, -canvas.width, 0);
    
    this.currentImage = canvas;
    this.drawImage();
    this.saveToHistory('水平翻转');
  }

  /**
   * 垂直翻转
   */
  flipVertical() {
    if (!this.currentImage) return;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = this.currentImage.width;
    canvas.height = this.currentImage.height;
    
    ctx.scale(1, -1);
    ctx.drawImage(this.currentImage, 0, -canvas.height);
    
    this.currentImage = canvas;
    this.drawImage();
    this.saveToHistory('垂直翻转');
  }

  /**
   * 裁剪图片
   */
  crop(x, y, width, height) {
    if (!this.currentImage) return;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = width;
    canvas.height = height;
    
    ctx.drawImage(
      this.currentImage,
      x, y, width, height,
      0, 0, width, height
    );
    
    this.currentImage = canvas;
    this.drawImage();
    this.saveToHistory('裁剪');
  }

  /**
   * 调整亮度
   */
  adjustBrightness(value) {
    if (!this.currentImage) return;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = this.currentImage.width;
    canvas.height = this.currentImage.height;
    
    ctx.filter = `brightness(${100 + value}%)`;
    ctx.drawImage(this.currentImage, 0, 0);
    
    this.currentImage = canvas;
    this.drawImage();
    this.saveToHistory(`亮度 ${value > 0 ? '+' : ''}${value}`);
  }

  /**
   * 调整对比度
   */
  adjustContrast(value) {
    if (!this.currentImage) return;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = this.currentImage.width;
    canvas.height = this.currentImage.height;
    
    ctx.filter = `contrast(${100 + value}%)`;
    ctx.drawImage(this.currentImage, 0, 0);
    
    this.currentImage = canvas;
    this.drawImage();
    this.saveToHistory(`对比度 ${value > 0 ? '+' : ''}${value}`);
  }

  /**
   * 添加文字标记
   */
  addTextAnnotation(text, x, y, options = {}) {
    if (!this.canvas) return;
    
    const {
      fontSize = 16,
      fontFamily = 'Arial',
      color = '#ff0000',
      backgroundColor = 'rgba(255, 255, 255, 0.8)',
      padding = 4
    } = options;
    
    this.ctx.font = `${fontSize}px ${fontFamily}`;
    this.ctx.textBaseline = 'top';
    
    // 测量文字尺寸
    const metrics = this.ctx.measureText(text);
    const textWidth = metrics.width;
    const textHeight = fontSize;
    
    // 绘制背景
    if (backgroundColor) {
      this.ctx.fillStyle = backgroundColor;
      this.ctx.fillRect(
        x - padding,
        y - padding,
        textWidth + padding * 2,
        textHeight + padding * 2
      );
    }
    
    // 绘制文字
    this.ctx.fillStyle = color;
    this.ctx.fillText(text, x, y);
    
    this.saveToHistory(`添加文字: ${text}`);
  }

  /**
   * 添加箭头标记
   */
  addArrowAnnotation(startX, startY, endX, endY, options = {}) {
    if (!this.canvas) return;
    
    const {
      color = '#ff0000',
      lineWidth = 2,
      arrowSize = 10
    } = options;
    
    this.ctx.strokeStyle = color;
    this.ctx.fillStyle = color;
    this.ctx.lineWidth = lineWidth;
    
    // 绘制线条
    this.ctx.beginPath();
    this.ctx.moveTo(startX, startY);
    this.ctx.lineTo(endX, endY);
    this.ctx.stroke();
    
    // 计算箭头角度
    const angle = Math.atan2(endY - startY, endX - startX);
    
    // 绘制箭头
    this.ctx.beginPath();
    this.ctx.moveTo(endX, endY);
    this.ctx.lineTo(
      endX - arrowSize * Math.cos(angle - Math.PI / 6),
      endY - arrowSize * Math.sin(angle - Math.PI / 6)
    );
    this.ctx.lineTo(
      endX - arrowSize * Math.cos(angle + Math.PI / 6),
      endY - arrowSize * Math.sin(angle + Math.PI / 6)
    );
    this.ctx.closePath();
    this.ctx.fill();
    
    this.saveToHistory('添加箭头');
  }

  /**
   * 添加矩形标记
   */
  addRectangleAnnotation(x, y, width, height, options = {}) {
    if (!this.canvas) return;
    
    const {
      strokeColor = '#ff0000',
      fillColor = 'transparent',
      lineWidth = 2
    } = options;
    
    this.ctx.strokeStyle = strokeColor;
    this.ctx.lineWidth = lineWidth;
    
    if (fillColor !== 'transparent') {
      this.ctx.fillStyle = fillColor;
      this.ctx.fillRect(x, y, width, height);
    }
    
    this.ctx.strokeRect(x, y, width, height);
    this.saveToHistory('添加矩形');
  }

  /**
   * 添加圆形标记
   */
  addCircleAnnotation(centerX, centerY, radius, options = {}) {
    if (!this.canvas) return;
    
    const {
      strokeColor = '#ff0000',
      fillColor = 'transparent',
      lineWidth = 2
    } = options;
    
    this.ctx.strokeStyle = strokeColor;
    this.ctx.lineWidth = lineWidth;
    
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    
    if (fillColor !== 'transparent') {
      this.ctx.fillStyle = fillColor;
      this.ctx.fill();
    }
    
    this.ctx.stroke();
    this.saveToHistory('添加圆形');
  }

  /**
   * 保存到历史记录
   */
  saveToHistory(action) {
    // 清除当前位置之后的历史
    this.history = this.history.slice(0, this.historyIndex + 1);
    
    // 添加新的历史记录
    this.history.push({
      action,
      imageData: this.currentImage ? this.currentImage.toDataURL() : null,
      timestamp: Date.now()
    });
    
    // 限制历史记录大小
    if (this.history.length > this.maxHistorySize) {
      this.history.shift();
    } else {
      this.historyIndex++;
    }
  }

  /**
   * 撤销
   */
  undo() {
    if (this.historyIndex > 0) {
      this.historyIndex--;
      const historyItem = this.history[this.historyIndex];
      if (historyItem.imageData) {
        this.loadImage(historyItem.imageData).then(() => {
          this.drawImage();
        });
      }
      return historyItem.action;
    }
    return null;
  }

  /**
   * 重做
   */
  redo() {
    if (this.historyIndex < this.history.length - 1) {
      this.historyIndex++;
      const historyItem = this.history[this.historyIndex];
      if (historyItem.imageData) {
        this.loadImage(historyItem.imageData).then(() => {
          this.drawImage();
        });
      }
      return historyItem.action;
    }
    return null;
  }

  /**
   * 重置到原始图片
   */
  reset() {
    if (this.originalImage) {
      this.currentImage = this.cloneImage(this.originalImage);
      this.drawImage();
      this.saveToHistory('重置');
    }
  }

  /**
   * 获取当前图片的DataURL
   */
  getImageDataURL(format = 'image/png', quality = 1.0) {
    if (!this.currentImage) return null;
    
    // 如果是 Canvas，直接调用 toDataURL
    if (this.currentImage instanceof HTMLCanvasElement) {
      return this.currentImage.toDataURL(format, quality);
    }
    
    // 如果是 Image 对象，需要先转换为 Canvas
    if (this.currentImage instanceof HTMLImageElement) {
      const canvas = this.cloneImage(this.currentImage);
      return canvas.toDataURL(format, quality);
    }
    
    return null;
  }

  /**
   * 获取当前图片的Blob
   */
  async getImageBlob(format = 'image/png', quality = 1.0) {
    if (!this.currentImage) return null;
    
    // 如果是 Canvas，直接调用 toBlob
    if (this.currentImage instanceof HTMLCanvasElement) {
      return new Promise(resolve => {
        this.currentImage.toBlob(resolve, format, quality);
      });
    }
    
    // 如果是 Image 对象，需要先转换为 Canvas
    if (this.currentImage instanceof HTMLImageElement) {
      const canvas = this.cloneImage(this.currentImage);
      return new Promise(resolve => {
        canvas.toBlob(resolve, format, quality);
      });
    }
    
    return null;
  }

  /**
   * 下载图片
   */
  async downloadImage(filename = 'processed_image.png', format = 'image/png', quality = 1.0) {
    const dataURL = this.getImageDataURL(format, quality);
    if (!dataURL) return;
    
    const link = document.createElement('a');
    link.download = filename;
    link.href = dataURL;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * 获取图片信息
   */
  getImageInfo() {
    if (!this.currentImage) return null;
    
    // 确定图片格式
    let format = 'Unknown';
    let width = 0;
    let height = 0;
    
    if (this.currentImage instanceof HTMLCanvasElement) {
      format = 'Canvas';
      width = this.currentImage.width;
      height = this.currentImage.height;
    } else if (this.currentImage instanceof HTMLImageElement) {
      format = 'Image';
      width = this.currentImage.naturalWidth || this.currentImage.width;
      height = this.currentImage.naturalHeight || this.currentImage.height;
    }
    
    return {
      width: width,
      height: height,
      size: this.getImageDataURL()?.length || 0,
      format: format,
      hasHistory: this.history.length > 1,
      canUndo: this.historyIndex > 0,
      canRedo: this.historyIndex < this.history.length - 1
    };
  }

  /**
   * 清理资源
   */
  dispose() {
    this.canvas = null;
    this.ctx = null;
    this.originalImage = null;
    this.currentImage = null;
    this.history = [];
    this.historyIndex = -1;
  }
}
