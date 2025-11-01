/**
 * 视频录制工具类
 * 将接收到的图片帧转换为视频并支持录制功能
 */

export class VideoRecorder {
  constructor(options = {}) {
    this.canvas = null;
    this.ctx = null;
    this.mediaRecorder = null;
    this.recordedChunks = [];
    
    // 录制配置
    this.options = {
      fps: options.fps || 30,
      videoBitsPerSecond: options.videoBitsPerSecond || 2500000,
      mimeType: options.mimeType || 'video/webm;codecs=vp9',
      width: options.width || 1280,
      height: options.height || 720,
      ...options
    };
    
    // 状态管理
    this.isRecording = false;
    this.isPaused = false;
    this.startTime = 0;
    this.pauseTime = 0;
    this.totalPauseTime = 0;
    
    // 帧管理
    this.frameQueue = [];
    this.frameInterval = 1000 / this.options.fps;
    this.lastFrameTime = 0;
    this.frameTimer = null;
    
    // 回调函数
    this.onRecordingStart = null;
    this.onRecordingStop = null;
    this.onRecordingPause = null;
    this.onRecordingResume = null;
    this.onFrameAdded = null;
    this.onError = null;
    
    // 统计信息
    this.stats = {
      totalFrames: 0,
      recordedFrames: 0,
      droppedFrames: 0,
      duration: 0,
      fileSize: 0
    };
  }

  /**
   * 初始化录制canvas
   */
  initCanvas(canvas) {
    this.canvas = canvas || document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    
    // 设置canvas尺寸
    this.canvas.width = this.options.width;
    this.canvas.height = this.options.height;
    
    return this.canvas;
  }

  /**
   * 开始录制
   */
  async startRecording() {
    if (this.isRecording) {
      console.warn('Recording already in progress');
      return false;
    }

    try {
      // 确保canvas已初始化
      if (!this.canvas) {
        this.initCanvas();
      }

      // 重置统计信息
      this.stats = {
        totalFrames: 0,
        recordedFrames: 0,
        droppedFrames: 0,
        duration: 0,
        fileSize: 0
      };

      // 获取canvas流
      const stream = this.canvas.captureStream(this.options.fps);
      
      // 检查浏览器支持的MIME类型
      const mimeType = this.getSupportedMimeType();
      
      // 创建MediaRecorder
      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: mimeType,
        videoBitsPerSecond: this.options.videoBitsPerSecond
      });

      // 设置事件监听
      this.setupMediaRecorderEvents();
      
      // 重置状态
      this.isRecording = true;
      this.isPaused = false;
      this.startTime = Date.now();
      this.totalPauseTime = 0;
      this.recordedChunks = [];
      
      // 开始帧处理(必须在start之前,确保有内容可录)
      this.startFrameProcessing();
      
      // 开始录制 - 使用timeslice确保定期获取数据
      this.mediaRecorder.start(100); // 每100ms触发一次dataavailable事件
      
      console.log('Video recording started');
      this.onRecordingStart?.();
      
      return true;
    } catch (error) {
      console.error('Failed to start recording:', error);
      this.onError?.(error);
      return false;
    }
  }

  /**
   * 停止录制
   */
  stopRecording() {
    if (!this.isRecording) {
      console.warn('No recording in progress');
      return Promise.resolve(null);
    }

    return new Promise((resolve) => {
      // 先停止帧处理
      this.stopFrameProcessing();
      
      // 设置停止回调
      this.mediaRecorder.onstop = () => {
        // 创建视频blob
        const blob = new Blob(this.recordedChunks, {
          type: this.mediaRecorder.mimeType
        });
        
        this.stats.fileSize = blob.size;
        this.stats.duration = Date.now() - this.startTime - this.totalPauseTime;
        
        console.log('Video recording stopped', {
          duration: this.stats.duration,
          frames: this.stats.recordedFrames,
          size: this.stats.fileSize,
          chunks: this.recordedChunks.length,
          mimeType: this.mediaRecorder.mimeType
        });
        
        this.onRecordingStop?.(blob, this.stats);
        resolve(blob);
      };
      
      // 停止录制
      this.mediaRecorder.stop();
      this.isRecording = false;
      this.isPaused = false;
    });
  }

  /**
   * 暂停录制
   */
  pauseRecording() {
    if (!this.isRecording || this.isPaused) {
      console.warn('Cannot pause recording');
      return false;
    }

    this.mediaRecorder.pause();
    this.isPaused = true;
    this.pauseTime = Date.now();
    
    console.log('Video recording paused');
    this.onRecordingPause?.();
    return true;
  }

  /**
   * 继续录制
   */
  resumeRecording() {
    if (!this.isRecording || !this.isPaused) {
      console.warn('Cannot resume recording');
      return false;
    }

    this.mediaRecorder.resume();
    this.isPaused = false;
    this.totalPauseTime += Date.now() - this.pauseTime;
    
    console.log('Video recording resumed');
    this.onRecordingResume?.();
    return true;
  }

  /**
   * 添加帧到录制
   */
  addFrame(imageData) {
    if (!this.isRecording || this.isPaused) {
      return false;
    }

    try {
      // 将帧添加到队列
      this.frameQueue.push({
        imageData,
        timestamp: Date.now()
      });
      
      this.stats.totalFrames++;
      this.onFrameAdded?.(this.stats.totalFrames);
      
      return true;
    } catch (error) {
      console.error('Failed to add frame:', error);
      this.stats.droppedFrames++;
      return false;
    }
  }

  /**
   * 开始帧处理
   */
  startFrameProcessing() {
    this.lastFrameTime = Date.now();
    
    this.frameTimer = setInterval(() => {
      this.processNextFrame();
    }, this.frameInterval);
  }

  /**
   * 停止帧处理
   */
  stopFrameProcessing() {
    if (this.frameTimer) {
      clearInterval(this.frameTimer);
      this.frameTimer = null;
    }
  }

  /**
   * 处理下一帧
   */
  processNextFrame() {
    if (this.frameQueue.length === 0) {
      return;
    }

    const frame = this.frameQueue.shift();
    
    try {
      // 创建图片对象
      const img = new Image();
      img.onload = () => {
        // 如果是第一帧,根据图片实际尺寸调整canvas大小(保持原始尺寸)
        if (this.stats.recordedFrames === 0) {
          this.canvas.width = img.width;
          this.canvas.height = img.height;
          console.log('Video canvas adjusted to original frame size:', img.width, 'x', img.height);
        }
        
        // 清空canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 直接绘制原始尺寸图片(不缩放)
        this.ctx.drawImage(img, 0, 0, img.width, img.height);
        
        this.stats.recordedFrames++;
      };
      
      img.src = frame.imageData;
    } catch (error) {
      console.error('Failed to process frame:', error);
      this.stats.droppedFrames++;
    }
  }

  /**
   * 设置MediaRecorder事件
   */
  setupMediaRecorderEvents() {
    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        this.recordedChunks.push(event.data);
      }
    };

    this.mediaRecorder.onstart = () => {
      console.log('MediaRecorder started');
    };

    this.mediaRecorder.onstop = () => {
      console.log('MediaRecorder stopped');
    };

    this.mediaRecorder.onerror = (event) => {
      console.error('MediaRecorder error:', event.error);
      this.onError?.(event.error);
    };
  }

  /**
   * 获取支持的MIME类型
   */
  getSupportedMimeType() {
    const types = [
      'video/webm;codecs=vp9',
      'video/webm;codecs=vp8',
      'video/webm',
      'video/mp4;codecs=h264',
      'video/mp4'
    ];

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        console.log('Using MIME type:', type);
        return type;
      }
    }

    console.warn('No supported MIME type found, using default');
    return 'video/webm';
  }

  /**
   * 下载录制的视频
   */
  downloadRecording(filename = 'recorded_video') {
    if (this.recordedChunks.length === 0) {
      console.warn('No recorded data available');
      return false;
    }

    const blob = new Blob(this.recordedChunks, {
      type: this.mediaRecorder.mimeType
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    
    // 根据MIME类型确定文件扩展名
    const extension = this.getFileExtension(this.mediaRecorder.mimeType);
    a.download = `${filename}.${extension}`;
    
    document.body.appendChild(a);
    a.click();
    
    // 清理
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);

    return true;
  }

  /**
   * 获取文件扩展名
   */
  getFileExtension(mimeType) {
    const extensions = {
      'video/webm': 'webm',
      'video/mp4': 'mp4',
      'video/ogg': 'ogv'
    };

    for (const [type, ext] of Object.entries(extensions)) {
      if (mimeType.includes(type)) {
        return ext;
      }
    }

    return 'webm'; // 默认扩展名
  }

  /**
   * 获取录制状态
   */
  getRecordingState() {
    return {
      isRecording: this.isRecording,
      isPaused: this.isPaused,
      duration: this.isRecording ? Date.now() - this.startTime - this.totalPauseTime : 0,
      frameQueueSize: this.frameQueue.length,
      stats: { ...this.stats }
    };
  }

  /**
   * 清理资源
   */
  dispose() {
    if (this.isRecording) {
      this.stopRecording();
    }
    
    this.stopFrameProcessing();
    
    this.canvas = null;
    this.ctx = null;
    this.mediaRecorder = null;
    this.recordedChunks = [];
    this.frameQueue = [];
  }

  /**
   * 创建预览视频元素
   */
  createPreviewVideo() {
    if (this.recordedChunks.length === 0) {
      return null;
    }

    const blob = new Blob(this.recordedChunks, {
      type: this.mediaRecorder.mimeType
    });

    const video = document.createElement('video');
    video.src = URL.createObjectURL(blob);
    video.controls = true;
    video.style.maxWidth = '100%';
    
    return video;
  }

  /**
   * 获取录制数据的Blob
   */
  getRecordingBlob() {
    if (this.recordedChunks.length === 0) {
      return null;
    }

    return new Blob(this.recordedChunks, {
      type: this.mediaRecorder.mimeType
    });
  }
}
