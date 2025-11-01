<template>
  <div class="view-images-page">
    <!-- 页面顶部Logo -->
    <div class="page-header">
      <div class="logo-container">
        <img src="/src/assets/images/logo1.png" alt="Logo" class="page-logo" />
      </div>
    </div>

    <!-- 主要内容区域 - 三列布局 -->
    <div class="main-content">
      <!-- 左侧：实时图像显示区域 -->
      <div class="left-panel">
        <div class="image-container" ref="imageContainer">
          <canvas ref="mainCanvas" class="main-canvas" @mousedown="handleMouseDown" @mousemove="handleMouseMove"
            @mouseup="handleMouseUp" @wheel="handleWheel"></canvas>
        </div>
      </div>
      <!-- 中间：图像设置面板 -->
      <div class="center-panel">
        <!-- WebRTC摄像头预览区域 -->
        <div class="camera-preview-section">
          <div class="camera-preview-container">
            <video ref="cameraVideoRef" autoplay playsinline class="camera-preview"
              :class="{ 'mirrored': cameraMirrored }"></video>
            <div v-if="cameraStatus === 'error'" class="camera-error">
              <el-icon>
                <VideoCamera />
              </el-icon>
              <span>摄像头不可用</span>
            </div>
            <div v-if="cameraStatus === 'loading'" class="camera-loading">
              <el-icon class="is-loading">
                <Loading />
              </el-icon>
              <span>正在启动摄像头...</span>
            </div>
          </div>
        </div>
        <div class="patient-info-brief" v-if="patientInfo.patientName || true">
          <el-tooltip placement="bottom" :show-after="500">
            <template #content>
              <div class="patient-tooltip">
                <div>
                  <strong>患者姓名：</strong>{{ patientInfo.patientName }}
                </div>
                <div>
                  <strong>患者编号：</strong>{{ patientInfo.patientNumber }}
                </div>
                <div>
                  <strong>检查类型：</strong>{{ patientInfo.examinationType }}
                </div>
                <div>
                  <strong>眼别：</strong>{{ getEyeSideText(patientInfo.eyeSide) }}
                </div>
                <div><strong>科室：</strong>{{ patientInfo.department }}</div>
                <div v-if="patientInfo.doctorName">
                  <strong>医生：</strong>{{ patientInfo.doctorName }}
                </div>
                <div>
                  <strong>预约日期：</strong>{{ patientInfo.scheduledDate }}
                </div>
                <div v-if="patientInfo.scheduledTime">
                  <strong>预约时间：</strong>{{ patientInfo.scheduledTime }}
                </div>
                <div>
                  <strong>优先级：</strong>{{ getPriorityText(patientInfo.priority) }}
                </div>
              </div>
            </template>
            <div class="patient-brief">
              <span class="patient-name">{{ patientInfo.patientName }}</span>
              <span class="patient-number">{{
                patientInfo.patientNumber
              }}</span>
              <span class="exam-type">{{ patientInfo.examinationType }}</span>
              <span class="eye-side">{{ getEyeSideText(patientInfo.eyeSide) }}</span>
            </div>
          </el-tooltip>
        </div>
        <!-- 控制按钮区域 -->
        <div class="control-buttons">
          <!-- 拍摄模式选择 -->
          <div class="capture-mode-selector">
            <label>拍摄模式：</label>
            <el-radio-group v-model="captureMode" size="large">
              <el-radio-button label="gray">灰度</el-radio-button>
              <el-radio-button label="color">彩图</el-radio-button>
            </el-radio-group>
          </div>

          <div class="button-group">
            <el-button :icon="deviceStatus === 'running' ? 'Link' : 'Connection'"
              :loading="deviceStatus === 'starting' || deviceStatus === 'stopping'" @click="toggleConnection()"
              size="default">
              {{ deviceButtonText }}
            </el-button>
          </div>



          <div class="button-group button-group-row">
            <el-button :type="isRecording ? 'danger' : 'warning'" @click="toggleRecording" size="default"
              :disabled="!hasReceivedFrames">
              <el-icon v-if="isRecording">
                <VideoPause />
              </el-icon>
              <el-icon v-else>
                <VideoPlay />
              </el-icon>
              {{ isRecording ? `录制中 (${recordingCountdown}s)` : "开始录像" }}
            </el-button>
            <el-button @click="captureImage" type="info" size="default" :disabled="!hasReceivedFrames || isCapturing"
              :loading="isCapturing">
              <el-icon>
                <VideoCamera />
              </el-icon>
              {{ isCapturing ? '拍照中...' : '拍照' }}
            </el-button>
          </div>

          <div class="button-group button-group-row">
            <el-button @click="autoFocus" size="default" :disabled="!hasReceivedFrames" class="focus-btn">
              <el-icon>
                <View />
              </el-icon>
              <span>自动对焦</span>
            </el-button>
            <el-button @click="resetDevice" size="default" :disabled="!hasReceivedFrames" class="reset-btn">
              <el-icon>
                <RefreshLeft />
              </el-icon>
              <span>复位</span>
            </el-button>
          </div>
        </div>
        <!-- 图像设置 - 下拉选择模式 -->
        <el-card class="settings-card compact" header="">
          <div class="settings-row">
            <div class="setting-item-inline">
              <label>亮度</label>
              <el-select v-model="brightness" size="small" @change="adjustBrightness" class="setting-select"
                style="background: #505050 !important; border-color: #606060 !important;">
                <el-option :value="-6" label="-6" />
                <el-option :value="-5" label="-5" />
                <el-option :value="-4" label="-4" />
                <el-option :value="-3" label="-3" />
                <el-option :value="-2" label="-2" />
                <el-option :value="-1" label="-1" />
                <el-option :value="0" label="0" />
                <el-option :value="1" label="1" />
                <el-option :value="2" label="2" />
                <el-option :value="3" label="3" />
                <el-option :value="4" label="4" />
                <el-option :value="5" label="5" />
                <el-option :value="6" label="6" />
              </el-select>
            </div>

            <div class="setting-item-inline">
              <label>微调</label>
              <el-select v-model="brightnessFine" size="small" @change="adjustBrightnessFine" class="setting-select"
                style="background: #505050 !important; border-color: #606060 !important;">
                <el-option :value="-6" label="-6.0" />
                <el-option :value="-5" label="-5.0" />
                <el-option :value="-4" label="-4.0" />
                <el-option :value="-3" label="-3.0" />
                <el-option :value="-2" label="-2.0" />
                <el-option :value="-1" label="-1.0" />
                <el-option :value="-0.5" label="-0.5" />
                <el-option :value="0" label="0.0" />
                <el-option :value="0.5" label="0.5" />
                <el-option :value="1" label="1.0" />
                <el-option :value="2" label="2.0" />
                <el-option :value="3" label="3.0" />
                <el-option :value="4" label="4.0" />
                <el-option :value="5" label="5.0" />
                <el-option :value="6" label="6.0" />
              </el-select>
            </div>
          </div>
        </el-card>

        <!-- 功能按钮区域 -->
        <div class="function-buttons-row">
          <el-button @click="openFundusAtlas" size="default" class="atlas-btn">
            <el-icon>
              <View />
            </el-icon>
            <span>眼底图谱</span>
          </el-button>
          <el-button @click="openHistoryExamination" size="default" class="history-btn">
            <el-icon>
              <View />
            </el-icon>
            <span>历史检查</span>
          </el-button>
        </div>

        <!-- 方向控制按钮 -->
        <div class="direction-control">
          <div class="direction-title">拍摄角度</div>
          <div class="direction-grid">
            <div class="direction-row">
              <el-button class="direction-btn direction-top-left" @click="moveDirection('左上')" circle>
                左上
              </el-button>
              <el-button class="direction-btn direction-up" @click="moveDirection('上')" circle>
                上
              </el-button>
              <el-button class="direction-btn direction-top-right" @click="moveDirection('右上')" circle>
                右上
              </el-button>
            </div>
            <div class="direction-row">
              <el-button class="direction-btn direction-left" @click="moveDirection('左')" circle>
                左
              </el-button>
              <el-button class="direction-btn direction-center" @click="moveDirection('中')" circle>
                中
              </el-button>
              <el-button class="direction-btn direction-right" @click="moveDirection('右')" circle>
                右
              </el-button>
            </div>
            <div class="direction-row">
              <el-button class="direction-btn direction-bottom-left" @click="moveDirection('左下')" circle>
                左下
              </el-button>
              <el-button class="direction-btn direction-down" @click="moveDirection('下')" circle>
                下
              </el-button>
              <el-button class="direction-btn direction-bottom-right" @click="moveDirection('右下')" circle>
                右下
              </el-button>
            </div>
          </div>
        </div>

        <!-- AI诊断区域 -->
        <div class="diagnosis-section" :class="{ 'is-disabled': !hasImageForDiagnosis }">
          <!-- 返回按钮 -->
          <el-button @click="goBack" type="default" class="back-btn" size="default">
            返回
          </el-button>

          <!-- <div class="diagnosis-title">AI辅助诊断</div> -->
          <el-button type="primary" :loading="aiDiagnosing" @click="performAIDiagnosisFromPanel"
            :disabled="!hasImageForDiagnosis" class="diagnosis-btn" size="large">
            诊断
          </el-button>
          <div class="diagnosis-hint" v-if="!hasImageForDiagnosis">
            <el-icon>
              <InfoFilled />
            </el-icon>
            <span>请先拍摄照片或者录制视频</span>
          </div>
        </div>
      </div>

      <!-- 右侧：缩略图列表 -->
      <div class="right-panel">
        <div class="thumbnail-header">
        </div>
        <div class="thumbnail-list">
          <!-- 缩略图项目 -->
          <div class="thumbnail-item" v-for="(thumbnail, index) in thumbnails" :key="thumbnail.id || index"
            @click="selectThumbnail(index)" :class="{ active: selectedThumbnailIndex === index }">
            <div class="thumbnail-image">
              <img v-if="thumbnail.src" :src="thumbnail.src" :alt="`缩略图 ${index + 1}`" />
              <div v-else class="thumbnail-placeholder">缩略图</div>

              <!-- 视频标识 -->
              <div v-if="thumbnail.type === 'video'" class="video-badge">
                <el-icon>
                  <VideoPlay />
                </el-icon>
                <span class="video-duration">{{ thumbnail.duration }}s</span>
              </div>

              <!-- 眼别标识 -->
              <div class="eye-side-badge" :class="thumbnail.eyeSide">
                {{ thumbnail.eyeSide === "left" ? "左" : "右" }}
              </div>
            </div>
            <div class="thumbnail-index">{{ index + 1 }}</div>
            <!-- 删除按钮 -->
            <div class="thumbnail-delete" @click.stop="deleteThumbnail(index)">
              <el-icon>
                <Close />
              </el-icon>
            </div>
          </div>

          <!-- 空状态提示 -->
          <div class="empty-thumbnails" v-if="thumbnails.length === 0">
            <div class="empty-icon">📷</div>
            <div class="empty-text">暂无图片</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 连接设置对话框 -->
    <el-dialog v-model="showConnectionSettings" title="连接设置" width="500px">
      <el-form :model="connectionConfig" label-width="120px">
        <el-form-item label="WebSocket URL">
          <el-input v-model="connectionConfig.url" placeholder="ws://localhost:25512/api/stream/ws" />
        </el-form-item>
        <el-form-item label="自动重连">
          <el-switch v-model="connectionConfig.autoReconnect" />
        </el-form-item>
        <el-form-item label="重连间隔(ms)">
          <el-input-number v-model="connectionConfig.reconnectInterval" :min="1000" :max="30000" :step="1000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showConnectionSettings = false">取消</el-button>
        <el-button type="primary" @click="applyConnectionSettings">确定</el-button>
      </template>
    </el-dialog>

    <!-- 文字输入对话框 -->
    <el-dialog v-model="showTextDialog" title="添加文字标注" width="400px">
      <el-input v-model="textAnnotation" type="textarea" :rows="3" placeholder="请输入标注文字"
        @keyup.enter="addTextAnnotation" />
      <template #footer>
        <el-button @click="showTextDialog = false">取消</el-button>
        <el-button type="primary" @click="addTextAnnotation">确定</el-button>
      </template>
    </el-dialog>

    <!-- 图片/视频查看器 -->
    <el-dialog v-model="showImageViewer" :title="thumbnails[selectedThumbnailIndex]?.type === 'video'
      ? '视频预览'
      : '图片预览'
      " width="80%" top="5vh">
      <div class="media-viewer">
        <video v-if="thumbnails[selectedThumbnailIndex]?.type === 'video'" :src="viewerImageUrl" controls autoplay
          class="viewer-video"></video>
        <img v-else :src="viewerImageUrl" class="viewer-image" ref="viewerImage" />
      </div>

      <!-- 操作按钮区 -->
      <template #footer>
        <div class="viewer-actions">
          <div class="left-actions">
            <!-- AI诊断按钮 -->
            <el-button v-if="thumbnails[selectedThumbnailIndex]?.type !== 'video'" type="primary"
              :loading="aiDiagnosing" @click="performAIDiagnosis">
              <el-icon>
                <View />
              </el-icon>
              {{ aiDiagnosing ? "AI诊断中..." : "AI诊断" }}
            </el-button>

            <!-- 刷新按钮 -->
            <el-button @click="refreshViewerImage">
              <el-icon>
                <Refresh />
              </el-icon>
              刷新
            </el-button>
          </div>

          <div class="right-actions">
            <el-button @click="showImageViewer = false">关闭</el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, onActivated, onDeactivated, nextTick } from "vue";
import { useRouter } from "vue-router";
import { message, Modal } from "ant-design-vue";
import { usePatientStore } from "@/store/modules/patient";
import {
  Close,
  VideoPlay,
  VideoPause,
  View,
  RefreshLeft,
  Refresh,
  InfoFilled,
  VideoCamera,
  Loading,
} from "@element-plus/icons-vue";
import { ImageProcessor } from "@/utils/image-processor";
import { VideoRecorder } from "@/utils/video-recorder";
import { isResponseSuccess, getResponseMessage } from "@/utils/request";
import * as imageAPI from "@/api/image";
import * as hardwareAPI from "@/api/hardware";
import { setCameraGain } from "@/api/hardware";
import { configAPI } from '@/api/config';
import workerManager from '@/utils/workerManager';

// 路由
const router = useRouter();

// 页面生命周期钩子 - 自动连接WebSocket
onMounted(() => {
  console.log("页面已挂载，自动连接WebSocket");
  connectWebSocket();
});

// 页面销毁时自动断开WebSocket
onUnmounted(() => {
  console.log("页面已卸载，自动断开WebSocket");
  disconnectWebSocket();
});

// 页面激活时自动连接WebSocket（用于keep-alive场景）
onActivated(() => {
  console.log("页面已激活，自动连接WebSocket");
  connectWebSocket();
});

// 页面失活时自动断开WebSocket（用于keep-alive场景）
onDeactivated(() => {
  console.log("页面已失活，自动断开WebSocket");
  disconnectWebSocket();
});

// WebSocket连接管理函数
const connectWebSocket = () => {
  // 如果已经连接或正在连接中，则直接返回
  if (connectionStatus.value === "connected" || connectionStatus.value === "connecting") {
    console.log("WebSocket 已连接或正在连接中，跳过连接");
    return;
  }
  try {
    console.log("=== 开始连接WebSocket ===");
    console.log("连接URL:", connectionConfig.url);

    websocket = new WebSocket(connectionConfig.url);

    // 设置接收二进制数据类型（ArrayBuffer格式）
    websocket.binaryType = 'arraybuffer';
    console.log("WebSocket binaryType 设置为:", websocket.binaryType);

    websocket.onopen = () => {
      console.log("✅ WebSocket连接成功");
      connectionStatus.value = "connected";
      hasReceivedFrames.value = false;

      // 重置重连计数器
      reconnectAttempts = 0;

      message.success("图像流连接成功");

      // 清除重连定时器
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
    };

    websocket.onmessage = (event) => {
      try {
        // 接收 ArrayBuffer 数据并按照协议解析
        if (event.data instanceof ArrayBuffer) {
          const receiveTime = performance.now(); // 记录接收时间
          console.log("📥 收到 ArrayBuffer 数据，长度:", event.data.byteLength, "接收时间:", receiveTime.toFixed(2));

          // 按照 [4字节长度信息] + [图像数据] 协议解析
          const buffer = new Uint8Array(event.data);

          // 检查数据长度是否足够包含4字节长度头
          if (buffer.length < 4) {
            console.warn("⚠️ 数据长度不足，忽略:", buffer.length);
            return;
          }

          // 读取4字节长度信息（小端序）
          const lengthBytes = new Uint8Array(buffer.buffer, 0, 4);
          const imageLength = (lengthBytes[0]) |
            (lengthBytes[1] << 8) |
            (lengthBytes[2] << 16) |
            (lengthBytes[3] << 24);

          // 验证长度信息是否合理
          if (imageLength <= 0 || imageLength > buffer.length - 4) {
            console.warn("⚠️ 图像长度信息异常:", imageLength, "总长度:", buffer.length);
            return;
          }

          // 提取图像数据（跳过4字节长度头）
          const imageData = buffer.slice(4, 4 + imageLength);

          console.log("📸 解析图像数据 - 长度头:", imageLength, "实际图像长度:", imageData.length);

          // 将解析后的图像数据存储为ArrayBuffer，添加时间戳（自动覆盖旧帧）
          latestFrameBuffer = imageData.buffer;
          latestFrameBuffer.receiveTime = receiveTime;
        } else {
          console.warn("⚠️ 收到非 ArrayBuffer 数据，忽略:", typeof event.data);
        }
      } catch (error) {
        console.error("处理 ArrayBuffer 数据失败:", error);
      }
    };

    websocket.onclose = (event) => {
      console.log("⚠️ WebSocket连接关闭:", {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean
      });

      connectionStatus.value = "disconnected";
      hasReceivedFrames.value = false;

      // 确保设备停止（仅在异常关闭时尝试）
      const shouldStopDevice = event.code !== 1000;
      if (shouldStopDevice) {
        hardwareAPI.stopDevice().catch((e) => console.warn('停止设备失败(可忽略):', e?.message || e));
      }

      // 根据关闭状态码判断是否需要重连
      const shouldReconnect = connectionConfig.autoReconnect &&
        event.code !== 1000 && // 正常关闭
        event.code !== 1001 && // 端点离开
        event.code !== 1005 && // 无状态码
        reconnectAttempts < MAX_RECONNECT_ATTEMPTS; // 未超过最大重连次数

      if (shouldReconnect) {
        reconnectAttempts++;
        console.log(`准备自动重连... (第 ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS} 次)`);
        message.warning(`连接断开，正在尝试重连... (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
        reconnectTimer = setTimeout(() => {
          console.log("执行自动重连");
          connectWebSocket();
        }, connectionConfig.reconnectInterval);
      } else {
        if (event.code === 1000) {
          message.success("连接已正常关闭");
        } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
          message.error(`重连失败，已尝试 ${MAX_RECONNECT_ATTEMPTS} 次，请手动重连`);
        } else {
          message.error(`连接异常关闭 (代码: ${event.code})`);
        }
      }
    };

    websocket.onerror = (error) => {
      console.error("❌ WebSocket连接错误:", error);
      connectionStatus.value = "disconnected";

      // 发生错误时尝试停止设备（防止设备留在运行态）
      hardwareAPI.stopDevice().then(() => {
        deviceStatus.value = "stopped";
      }).catch(() => { });

      // 显示错误信息
      message.error("WebSocket连接错误，请检查网络连接");

      // 如果启用了自动重连且未超过最大重连次数，尝试重连
      if (connectionConfig.autoReconnect && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        console.log(`连接错误，准备自动重连... (第 ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS} 次)`);
        message.warning(`连接错误，正在尝试重连... (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
        reconnectTimer = setTimeout(() => {
          console.log("执行自动重连");
          connectWebSocket();
        }, connectionConfig.reconnectInterval);
      } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        message.error(`重连失败，已尝试 ${MAX_RECONNECT_ATTEMPTS} 次，请手动重连`);
      }
    };

  } catch (error) {
    console.error("创建WebSocket连接失败:", error);
    connectionStatus.value = "disconnected";
    message.error("创建WebSocket连接失败: " + error.message);
  }
};

const disconnectWebSocket = () => {
  // 如果已经断开连接或正在断开中，则直接返回
  if (connectionStatus.value === "disconnected" || !websocket) {
    console.log("WebSocket 已断开或不存在，跳过断开操作");
    return;
  }

  console.log("🔌 开始断开 WebSocket 连接...");

  // 清除重连定时器
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }

  // 关闭 WebSocket 连接
  if (websocket) {
    try {
      // 检查连接状态
      if (websocket.readyState === WebSocket.OPEN || websocket.readyState === WebSocket.CONNECTING) {
        websocket.close(1000, "用户主动断开");
        console.log("✅ WebSocket 连接已关闭");
      } else {
        console.log("WebSocket 连接状态:", websocket.readyState);
      }
    } catch (error) {
      console.error("关闭 WebSocket 时出错:", error);
    } finally {
      websocket = null;
    }
  }

  // 清理帧数据
  latestFrameBuffer = null;
  isProcessing = false;

  // 释放当前帧的 Blob URL
  if (lastFrameBlobUrl) {
    URL.revokeObjectURL(lastFrameBlobUrl);
    lastFrameBlobUrl = null;
  }

  // 更新状态
  connectionStatus.value = "disconnected";
  hasReceivedFrames.value = false;

  // 重置重连计数器
  reconnectAttempts = 0;

  console.log("✅ WebSocket 断开完成");
};

// 响应式数据
const imageContainer = ref(null);
const mainCanvas = ref(null);

// 患者信息
const patientInfo = reactive({
  registrationId: null,
  examinationId: null, // 检查记录ID（用于保存图片和视频）
  registrationNumber: "",
  patientId: null,
  patientName: "",
  patientNumber: "",
  examinationType: "",
  examinationTypeId: null,
  department: "",
  doctorId: null,
  doctorName: "",
  scheduledDate: "",
  scheduledTime: "",
  priority: "",
  notes: "",
  eyeSide: "", // 眼别信息：left(左眼)、right(右眼)、both(双眼)
});

// 连接状态
const connectionStatus = ref("disconnected"); // disconnected, connecting, connected
// 设备状态
const deviceStatus = ref("stopped"); // stopped, starting, running, stopping
const hasReceivedFrames = ref(false); // 是否已接收到图片帧

// 眼睛状态
const eyeSideStatus = ref(""); // 眼睛左右状态：OD(右眼)、OS(左眼)
const eyeSideStatusLoading = ref(false); // 眼睛状态加载中

// 连接配置 - 直接连接第三方 WebSocket 服务
const connectionConfig = reactive({
  url: "ws://localhost:25512/api/stream/ws", // 直接连接第三方服务端口
  autoReconnect: true,
  reconnectInterval: 3000,
});
const showConnectionSettings = ref(false);

// WebSocket连接实例
let websocket = null;
let reconnectTimer = null;

// 高性能渲染相关变量
let latestFrameBuffer = null; // 最新帧的 ArrayBuffer
let isProcessing = false; // 是否正在处理帧
let renderLoopId = null; // 渲染循环 ID

// 重连相关变量
let reconnectAttempts = 0; // 重连尝试次数
const MAX_RECONNECT_ATTEMPTS = 5; // 最大重连次数

// Blob URL 管理（防止内存泄漏）
const blobUrls = ref([]);
let lastFrameBlobUrl = null;
let currentFrameBlob = null; // 当前帧的 Blob 对象

// 高性能渲染循环
const startRenderLoop = () => {
  // 如果渲染循环已经在运行，则不重复启动
  if (renderLoopId) {
    console.log('渲染循环已在运行，不重复启动');
    return;
  }

  // 添加处理超时计时器ID
  let processingTimeoutId = null;

  const renderLoop = async () => {
    // 不再检查连接状态，无论WebSocket是否连接都继续渲染循环

    // 只有在有数据且未在处理时才继续
    if (!isProcessing && latestFrameBuffer && mainCanvas.value) {
      isProcessing = true;
      const buffer = latestFrameBuffer;
      const receiveTime = buffer.receiveTime || performance.now();
      latestFrameBuffer = null; // 立即清除已处理的帧，减少延迟

      // 设置安全超时，确保isProcessing不会永久阻塞渲染循环
      if (processingTimeoutId) {
        clearTimeout(processingTimeoutId);
      }

      processingTimeoutId = setTimeout(() => {
        if (isProcessing) {
          console.warn('⚠️ 渲染处理超时，强制重置处理状态');
          isProcessing = false;
        }
      }, 1000); // 1秒超时保护

      try {
        // 创建 Blob 对象
        const blob = new Blob([buffer], { type: "image/jpeg" });

        // 使用 createImageBitmap 处理图像（高性能异步解码）
        const bitmap = await createImageBitmap(blob);

        // 获取 Canvas 上下文
        const ctx = mainCanvas.value.getContext('2d');
        if (!ctx) {
          throw new Error('无法获取 Canvas 上下文');
        }

        // 计算适合 Canvas 的尺寸
        const canvasWidth = mainCanvas.value.width;
        const canvasHeight = mainCanvas.value.height;
        const imgWidth = bitmap.width;
        const imgHeight = bitmap.height;

        // 计算缩放比例，保持宽高比
        const scaleX = canvasWidth / imgWidth;
        const scaleY = canvasHeight / imgHeight;
        const scale = Math.min(scaleX, scaleY, 1); // 不放大，只缩小

        const drawWidth = imgWidth * scale;
        const drawHeight = imgHeight * scale;
        const drawX = (canvasWidth - drawWidth) / 2;
        const drawY = (canvasHeight - drawHeight) / 2;

        // 清空 Canvas
        ctx.clearRect(0, 0, canvasWidth, canvasHeight);

        // 绘制图像
        ctx.drawImage(bitmap, drawX, drawY, drawWidth, drawHeight);

        // 只在录制时进行base64转换，拍照功能不依赖这些数据
        if (isRecording.value) {
          // 将 ArrayBuffer 转换为 base64 用于录制
          const base64String = btoa(String.fromCharCode(...new Uint8Array(buffer)));
          const dataUrl = `data:image/jpeg;base64,${base64String}`;

          // 更新状态用于录制功能
          currentImage.value = dataUrl;
          currentFrameData = dataUrl;
        }

        imageInfo.value = {
          width: imgWidth,
          height: imgHeight,
          size: buffer.byteLength,
          format: 'JPEG'
        };

        // 标记已接收到帧
        if (!hasReceivedFrames.value) {
          hasReceivedFrames.value = true;
        }

        // 如果正在录制且未暂停，添加帧到录制器
        if (isRecording.value && !isRecordingPaused.value && dataUrl) {
          videoRecorder.addFrame(dataUrl);
        }

        // 释放 bitmap 资源
        bitmap.close();

      } catch (error) {
        console.error('❌ 高性能渲染失败:', error);
      } finally {
        // 清除超时计时器
        if (processingTimeoutId) {
          clearTimeout(processingTimeoutId);
          processingTimeoutId = null;
        }
        isProcessing = false;
      }
    }

    // 无论连接状态如何，都继续渲染循环
    renderLoopId = requestAnimationFrame(renderLoop);
  };

  // 启动渲染循环
  renderLoopId = requestAnimationFrame(renderLoop);
};

// 停止渲染循环
const stopRenderLoop = () => {
  if (renderLoopId) {
    cancelAnimationFrame(renderLoopId);
    renderLoopId = null;
  }
  // 重置处理状态
  isProcessing = false;
  latestFrameBuffer = null;
};

// 清空左侧实时画面
const clearLiveView = () => {
  // 清空Canvas
  if (mainCanvas.value) {
    const ctx = mainCanvas.value.getContext('2d');
    if (ctx) {
      // 完全清除画布内容
      ctx.clearRect(0, 0, mainCanvas.value.width, mainCanvas.value.height);
      // 重置画布变换
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      // 再次清除以确保完全清除
      ctx.clearRect(0, 0, mainCanvas.value.width, mainCanvas.value.height);
    }
  }

  // 重置所有图像相关状态
  currentImage.value = null;
  imageInfo.value = null;
  latestFrameBuffer = null;
  currentFrameData = null;
  currentFrameBlob = null;

  // 如果存在lastFrameBlobUrl，释放它
  if (lastFrameBlobUrl) {
    URL.revokeObjectURL(lastFrameBlobUrl);
    lastFrameBlobUrl = null;
  }
};

// Blob 转 base64 辅助函数
const blobToBase64 = (blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
};

// 添加视频缩略图辅助函数
const addVideoThumbnail = (firstFrame, videoUrl, videoBlob, mediaId = null, eyeSide = null, duration = 10) => {
  addThumbnail(firstFrame, {
    type: "video",
    videoUrl: videoUrl,
    videoBlob: videoBlob,
    duration: duration,
    eyeSide: eyeSide,
    mediaId: mediaId,
    isExisting: mediaId !== null,
  });
};

// 图片状态
const currentImage = ref(null);
const imageInfo = ref(null);
const zoomLevel = ref(1);
const isLoading = ref(false);

// 工具状态
const currentTool = ref("select");
const showSidePanel = ref(true);

// 图片调整
const brightness = ref(0);
const brightnessFine = ref(0);
const contrast = ref(0);

// 标注设置
const annotationColor = ref("#ff0000");
const annotationLineWidth = ref(2);
const annotationFontSize = ref(16);
const showTextDialog = ref(false);
const textAnnotation = ref("");
const pendingTextPosition = ref(null);

// 录制状态
const isRecording = ref(false);
const isRecordingPaused = ref(false);
const recordingDuration = ref(0);
const recordingCountdown = ref(0); // 录像倒计时（秒）
const recordingStats = reactive({
  recordedFrames: 0,
  totalFrames: 0,
  droppedFrames: 0,
});
const hasRecordedVideo = ref(false);

// 历史记录
const canUndo = ref(false);
const canRedo = ref(false);

// 缩略图
const thumbnails = ref([]);
const selectedThumbnailIndex = ref(-1);
const showImageViewer = ref(false);
const viewerImageUrl = ref("");
const viewerImage = ref(null); // 预览图片元素引用

// AI诊断
const aiDiagnosing = ref(false);

// 拍摄模式选择
const captureMode = ref("gray"); // gray: 灰度, color: 彩图

// 拍照状态
const isCapturing = ref(false);

// WebRTC摄像头相关
const cameraVideoRef = ref(null);
const cameraStatus = ref("loading"); // loading, active, error, inactive
const cameraMirrored = ref(false);
let cameraStream = null;

// 鼠标交互
const isDrawing = ref(false);
const drawStartPos = ref({ x: 0, y: 0 });
const drawEndPos = ref({ x: 0, y: 0 });

// 工具类实例
let imageProcessor = null;
let videoRecorder = null;
let recordingTimer = null;

// 导航方法
const goBack = () => {
  // 返回上一个路径，如果没有历史记录则返回主页
  if (window.history.length > 1) {
    router.go(-1);
  } else {
    router.push("/index");
  }
};

// 设备按钮文本
const deviceButtonText = computed(() => {
  switch (deviceStatus.value) {
    case "running":
      return "关闭";
    case "starting":
      return "启动中...";
    case "stopping":
      return "关闭中...";
    default:
      return "启动";
  }
});

// 判断是否有可用于AI诊断的图片
const hasImageForDiagnosis = computed(() => {
  // 1. 检查缩略图列表中是否有图片(不包括视频)
  const hasImageInThumbnails = thumbnails.value.some((t) => t.type === "image");

  // 2. 或者当前有实时图像
  const hasCurrentImage = !!currentImage.value;

  return hasImageInThumbnails || hasCurrentImage;
});

// 摄像头状态文本
const cameraStatusText = computed(() => {
  switch (cameraStatus.value) {
    case "loading":
      return "启动中";
    case "active":
      return "已连接";
    case "error":
      return "连接失败";
    case "inactive":
      return "未连接";
    default:
      return "未知";
  }
});

// WebRTC摄像头方法
const startCamera = async () => {
  try {
    console.log("🎥 启动摄像头预览...");
    cameraStatus.value = "loading";

    // 检查摄像头权限
    const permissions = await navigator.permissions.query({ name: 'camera' });
    console.log('摄像头权限状态:', permissions.state);

    if (permissions.state === 'denied') {
      cameraStatus.value = "error";
      message.error("摄像头权限被拒绝，请在浏览器设置中允许摄像头访问");
      return;
    }

    // 请求摄像头权限并打开默认视频设备
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'user' // 优先使用前置摄像头
      },
      audio: false
    });

    if (cameraVideoRef.value) {
      cameraVideoRef.value.srcObject = cameraStream;
      cameraStatus.value = "active";
      console.log("✅ 摄像头预览启动成功");
    }
  } catch (err) {
    console.error('❌ 无法打开摄像头:', err);
    cameraStatus.value = "error";

    if (err.name === 'NotAllowedError') {
      message.error("摄像头权限被拒绝，请允许摄像头访问");
    } else if (err.name === 'NotFoundError') {
      message.error("未找到摄像头设备，请检查设备连接");
    } else if (err.name === 'NotReadableError') {
      message.error("摄像头被其他应用占用，请关闭其他应用后重试");
    } else {
      message.error("摄像头启动失败: " + err.message);
    }
  }
};

const stopCamera = () => {
  console.log("🛑 关闭摄像头预览...");

  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
  }

  if (cameraVideoRef.value) {
    cameraVideoRef.value.srcObject = null;
  }

  cameraStatus.value = "inactive";
  console.log("✅ 摄像头预览已关闭");
};

const toggleCameraMirror = () => {
  cameraMirrored.value = !cameraMirrored.value;
  console.log("🔄 镜像模式:", cameraMirrored.value ? "开启" : "关闭");
};

// 方法
const initializeComponents = () => {
  console.log("=== 初始化组件 ===");

  // 初始化图片处理器
  imageProcessor = new ImageProcessor();

  // 初始化视频录制器（初始化时使用默认尺寸，录制时会根据实际帧尺寸调整）
  videoRecorder = new VideoRecorder({
    fps: 30,
    width: 1920, // 默认更高的分辨率
    height: 1080,
  });

  videoRecorder.onRecordingStart = () => {
    isRecording.value = true;
    startRecordingTimer();
  };

  videoRecorder.onRecordingStop = (blob, stats) => {
    isRecording.value = false;
    isRecordingPaused.value = false;
    hasRecordedVideo.value = true;
    stopRecordingTimer();
    Object.assign(recordingStats, stats);
    message.success("视频录制完成");
  };

  videoRecorder.onRecordingPause = () => {
    isRecordingPaused.value = true;
  };

  videoRecorder.onRecordingResume = () => {
    isRecordingPaused.value = false;
  };
};

const initializeCanvas = async () => {
  await nextTick();

  if (!mainCanvas.value || !imageContainer.value) {
    // console.warn('Canvas or container not ready, retrying...');
    setTimeout(() => initializeCanvas(), 100);
    return;
  }

  const container = imageContainer.value;

  // 确保容器有尺寸
  if (container.clientWidth === 0 || container.clientHeight === 0) {
    console.warn("Container size is 0, waiting for layout...");
    // 等待布局完成
    setTimeout(() => initializeCanvas(), 100);
    return;
  }

  try {
    // 设置canvas尺寸
    mainCanvas.value.width = container.clientWidth;
    mainCanvas.value.height = container.clientHeight;

    console.log("Canvas initialized:", {
      width: mainCanvas.value.width,
      height: mainCanvas.value.height,
      containerSize: `${container.clientWidth}x${container.clientHeight}`,
    });

    // 确保 imageProcessor 已创建
    if (!imageProcessor) {
      console.error("ImageProcessor not created, cannot initialize canvas");
      return;
    }

    // 初始化图片处理器
    imageProcessor.initCanvas(mainCanvas.value);
    console.log("ImageProcessor initialized successfully");

    // 确保 videoRecorder 已创建
    if (!videoRecorder) {
      console.error("VideoRecorder not created, cannot initialize canvas");
      return;
    }

    // 初始化视频录制器
    videoRecorder.initCanvas();
    console.log("VideoRecorder initialized successfully");
  } catch (error) {
    console.error("Canvas initialization failed:", error);
    console.error("Error details:", {
      error: error.message,
      stack: error.stack,
      canvasExists: !!mainCanvas.value,
      containerExists: !!imageContainer.value,
      imageProcessorExists: !!imageProcessor,
      videoRecorderExists: !!videoRecorder,
    });
  }
};

const toggleConnection = async () => {
  if (deviceStatus.value === "running") {
    console.log("=== 停止设备 ===");
    deviceStatus.value = "stopping";

    try {
      // 停止设备
      console.log("🛑 正在停止设备...");
      await hardwareAPI.stopDevice();
      console.log("✅ 设备已停止");
      message.success("设备已停止");
      deviceStatus.value = "stopped";

      // 停止渲染循环
      stopRenderLoop();

      // 清空左侧实时画面
      clearLiveView();

      // 断开WebSocket连接
      disconnectWebSocket();
    } catch (error) {
      console.error("停止设备失败:", error);
      message.error("停止设备失败: " + (error.message || "未知错误"));
      deviceStatus.value = "running"; // 恢复到运行状态，因为停止失败
    }
  } else {
    console.log("=== 启动设备 ===");
    deviceStatus.value = "starting";

    try {
      // 连接WebSocket
      connectWebSocket();

      // 启动设备
      console.log("🟢 正在启动设备...");
      await hardwareAPI.startDevice();
      console.log("✅ 设备已启动");
      message.success("设备已启动");
      deviceStatus.value = "running";

      // 启动渲染循环
      startRenderLoop();
    } catch (error) {
      console.error("启动设备失败:", error);
      message.error("启动设备失败: " + (error.message || "未知错误"));
      deviceStatus.value = "stopped"; // 恢复到停止状态，因为启动失败

      // 如果启动失败，断开WebSocket连接
      disconnectWebSocket();
      // 停止渲染循环
      stopRenderLoop();

      // 清空左侧实时画面
      clearLiveView();
    }
  }
};


// 当前帧数据用于拍照（从高性能渲染循环中获取）
let currentFrameData = null;

// 图片操作方法
const fitToWindow = () => {
  if (!imageInfo.value) return;
  const container = imageContainer.value;
  const scaleX = container.clientWidth / imageInfo.value.width;
  const scaleY = container.clientHeight / imageInfo.value.height;
  zoomLevel.value = Math.min(scaleX, scaleY, 1);
  imageProcessor.drawImage();
};

const actualSize = () => {
  zoomLevel.value = 1;
  imageProcessor.drawImage();
};

const zoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value * 1.2, 5);
  imageProcessor.scale(1.2);
};

const zoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value / 1.2, 0.1);
  imageProcessor.scale(1 / 1.2);
};

const rotateLeft = () => {
  imageProcessor.rotate(-90);
  updateHistoryState();
};

const rotateRight = () => {
  imageProcessor.rotate(90);
  updateHistoryState();
};

const flipHorizontal = () => {
  imageProcessor.flipHorizontal();
  updateHistoryState();
};

const flipVertical = () => {
  imageProcessor.flipVertical();
  updateHistoryState();
};

// 图片调整方法
const adjustBrightness = async (value) => {
  imageProcessor.adjustBrightness(value);
  updateHistoryState();

  // 调用相机增益API
  try {
    console.log('📷 设置相机亮度:', value);
    const response = await setCameraGain(value, brightnessFine.value);
    if (response.code === 200) {
      console.log('✅ 相机亮度设置成功');
    } else {
      console.warn('⚠️ 相机亮度设置失败:', response.msg);
    }
  } catch (error) {
    console.error('❌ 相机亮度设置失败:', error);
    message.error('设置相机亮度失败: ' + error.message);
  }
};

const adjustBrightnessFine = async (value) => {
  imageProcessor.adjustBrightness(brightness.value + value);
  updateHistoryState();

  // 调用相机增益API
  try {
    console.log('📷 设置相机微调:', value);
    const response = await setCameraGain(brightness.value, value);
    if (response.code === 200) {
      console.log('✅ 相机微调设置成功');
    } else {
      console.warn('⚠️ 相机微调设置失败:', response.msg);
    }
  } catch (error) {
    console.error('❌ 相机微调设置失败:', error);
    message.error('设置相机微调失败: ' + error.message);
  }
};

const adjustContrast = (value) => {
  imageProcessor.adjustContrast(value);
  updateHistoryState();
};

// 工具方法
const setTool = (tool) => {
  currentTool.value = tool;
  if (mainCanvas.value) {
    mainCanvas.value.style.cursor = getCursorForTool(tool);
  }
};

const getCursorForTool = (tool) => {
  const cursors = {
    select: "default",
    text: "text",
    arrow: "crosshair",
    rectangle: "crosshair",
    circle: "crosshair",
  };
  return cursors[tool] || "default";
};

// 鼠标事件处理
const handleMouseDown = (event) => {
  const rect = mainCanvas.value.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;

  drawStartPos.value = { x, y };

  if (currentTool.value === "text") {
    pendingTextPosition.value = { x, y };
    showTextDialog.value = true;
  } else if (currentTool.value !== "select") {
    isDrawing.value = true;
  }
};

const handleMouseMove = (event) => {
  if (!isDrawing.value) return;

  const rect = mainCanvas.value.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;

  drawEndPos.value = { x, y };
};

const handleMouseUp = (event) => {
  if (!isDrawing.value) return;

  const rect = mainCanvas.value.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;

  drawEndPos.value = { x, y };
  isDrawing.value = false;

  // 执行绘制操作
  executeDrawingOperation();
};

const handleWheel = (event) => {
  event.preventDefault();
  const delta = event.deltaY > 0 ? 0.9 : 1.1;
  zoomLevel.value = Math.max(0.1, Math.min(5, zoomLevel.value * delta));
  imageProcessor.scale(delta);
};

const executeDrawingOperation = () => {
  const start = drawStartPos.value;
  const end = drawEndPos.value;

  const options = {
    color: annotationColor.value,
    lineWidth: annotationLineWidth.value,
  };

  switch (currentTool.value) {
    case "arrow":
      imageProcessor.addArrowAnnotation(
        start.x,
        start.y,
        end.x,
        end.y,
        options
      );
      break;
    case "rectangle":
      imageProcessor.addRectangleAnnotation(
        Math.min(start.x, end.x),
        Math.min(start.y, end.y),
        Math.abs(end.x - start.x),
        Math.abs(end.y - start.y),
        {
          strokeColor: annotationColor.value,
          lineWidth: annotationLineWidth.value,
        }
      );
      break;
    case "circle":
      const radius = Math.sqrt(
        Math.pow(end.x - start.x, 2) + Math.pow(end.y - start.y, 2)
      );
      imageProcessor.addCircleAnnotation(start.x, start.y, radius, options);
      break;
  }

  updateHistoryState();
};

const addTextAnnotation = () => {
  if (!textAnnotation.value.trim() || !pendingTextPosition.value) return;

  imageProcessor.addTextAnnotation(
    textAnnotation.value,
    pendingTextPosition.value.x,
    pendingTextPosition.value.y,
    {
      fontSize: annotationFontSize.value,
      color: annotationColor.value,
    }
  );

  textAnnotation.value = "";
  showTextDialog.value = false;
  pendingTextPosition.value = null;
  updateHistoryState();
};

// 录制方法 - 录制5秒视频
const toggleRecording = async () => {
  if (isRecording.value) {
    // 正在录制中，停止录制
    isRecording.value = false;
    recordingCountdown.value = 0;
    return;
  }

  try {
    // 调用眼睛状态方法，它会设置 eyeSideStatus.value
    await getEyeSideStatus();

    // 直接使用 eyeSideStatus.value 的值（数据库使用 'OS'/'OD'）
    const eyeSideForRecording = eyeSideStatus.value;
    console.log("📹 录制使用眼睛状态:", eyeSideForRecording);

    message.info("开始录制5秒视频...");
    isRecording.value = true;
    recordingCountdown.value = 5; // 初始化倒计时为5秒

    // 启动倒计时
    const countdownInterval = setInterval(() => {
      if (recordingCountdown.value > 0) {
        recordingCountdown.value--;
      } else {
        clearInterval(countdownInterval);
      }
    }, 1000);

    // 重新初始化视频录制器
    const recordingStarted = await videoRecorder.startRecording();
    if (!recordingStarted) {
      message.error("启动录制失败");
      isRecording.value = false;
      clearInterval(countdownInterval);
      return;
    }

    console.log(`📹 开始录制5秒视频...`);

    // 录制5秒（通过handleNewFrame自动添加帧）
    const recordingStartTime = Date.now();
    const recordingDuration = 5000; // 5秒

    // 等待5秒后自动停止
    setTimeout(async () => {
      if (isRecording.value) {
        isRecording.value = false;
        recordingCountdown.value = 0;
        clearInterval(countdownInterval);

        // 停止录制并获取视频
        console.log("⏹️  停止录制...");
        const videoBlob = await videoRecorder.stopRecording();

        // 获取实际的视频时长（毫秒转换为秒）
        const actualDuration = Math.round(videoRecorder.getRecordingState().duration / 1000);
        console.log("📊 实际视频时长:", actualDuration, "秒");

        console.log("📦 视频Blob信息:", {
          size: videoBlob?.size,
          type: videoBlob?.type,
          hasContent: videoBlob && videoBlob.size > 0,
        });

        if (videoBlob && videoBlob.size > 0) {
          // 获取当前帧作为封面
          const firstFrame = currentFrameData;

          // 创建视频URL
          const videoUrl = URL.createObjectURL(videoBlob);
          console.log("✅ 视频URL已创建:", videoUrl);

          // 保存到服务器和数据库
          if (patientInfo.registrationId) {
            try {
              // 将Blob转换为base64
              const reader = new FileReader();
              reader.onloadend = async () => {
                try {
                  const videoBase64 = reader.result;

                  // 检测实际的视频格式
                  let fileFormat = "webm"; // 默认

                  // 更准确的MIME类型检测
                  if (videoBlob.type === "video/mp4" || videoBlob.type.includes("mp4")) {
                    fileFormat = "mp4";
                  } else if (videoBlob.type === "video/webm" || videoBlob.type.includes("webm")) {
                    fileFormat = "webm";
                  } else if (videoBlob.type === "video/ogg" || videoBlob.type.includes("ogg")) {
                    fileFormat = "ogv";
                  } else if (videoBlob.type === "video/quicktime" || videoBlob.type.includes("quicktime")) {
                    fileFormat = "mov";
                  }

                  // 如果无法确定格式，根据文件扩展名或内容进一步检测
                  if (fileFormat === "webm") {
                    // 检查文件签名或内容特征
                    const firstBytes = await videoBlob.slice(0, 4).arrayBuffer();
                    const view = new Uint8Array(firstBytes);

                    // WebM文件通常以0x1A45DFA3开头
                    if (view[0] === 0x1A && view[1] === 0x45 && view[2] === 0xDF && view[3] === 0xA3) {
                      fileFormat = "webm";
                    }
                    // MP4文件通常以ftyp开头
                    else if (view[0] === 0x66 && view[1] === 0x74 && view[2] === 0x79 && view[3] === 0x70) {
                      fileFormat = "mp4";
                    }
                  }

                  console.log(
                    "Video format:",
                    fileFormat,
                    "MIME type:",
                    videoBlob.type
                  );

                  const saveData = {
                    examination_id: patientInfo.examinationId, // 检查ID
                    patient_id: patientInfo.registrationId, // 患者ID
                    video_data: videoBase64,
                    cover_image_data: firstFrame,
                    eye_side: eyeSideForRecording,
                    duration: actualDuration,
                    file_format: fileFormat,
                    acquisition_device: "Camera",
                    capture_mode: captureMode.value,
                  };

                  console.log("🎥 保存视频数据:", {
                    examination_id: saveData.examination_id,
                    registration_id: saveData.registration_id,
                    patient_id: saveData.patient_id,
                    eye_side: saveData.eye_side,
                  });

                  const response = await imageAPI.saveVideo(saveData);
                  if (isResponseSuccess(response)) {
                    console.log("视频已保存到数据库:", response.data);

                    // 添加到缩略图列表,包含mediaId用于后续删除
                    addVideoThumbnail(firstFrame, videoUrl, videoBlob, response.data.id, eyeSideForRecording, actualDuration);

                    message.success(
                      getResponseMessage(response) || "录制完成并已保存！"
                    );
                  } else {
                    // 保存失败,仍然添加到缩略图列表但不包含mediaId
                    // addVideoThumbnail(firstFrame, videoUrl, videoBlob, null, null, actualDuration);
                    message.warning("录制完成，但保存到数据库失败");
                  }
                } catch (error) {
                  console.error("保存视频到服务器失败:", error);
                  // 保存失败,仍然添加到缩略图列表但不包含mediaId
                  // addVideoThumbnail(firstFrame, videoUrl, videoBlob, null, null, actualDuration);
                  message.warning("录制完成，但保存到数据库失败");
                }
              };
              reader.readAsDataURL(videoBlob);
            } catch (error) {
              console.error("处理视频数据失败:", error);
              // 处理失败,仍然添加到缩略图列表但不包含mediaId
              addVideoThumbnail(firstFrame, videoUrl, videoBlob, null, null, actualDuration);
              message.success("录制完成（保存失败）");
            }
          } else {
            // 未关联检查记录,添加到缩略图列表但不包含mediaId
            // addVideoThumbnail(firstFrame, videoUrl, videoBlob, null, null, actualDuration);
            message.success("录制完成（未关联检查记录）");
          }
        } else {
          console.error("❌ 录制失败: 视频为空或无效");
          message.error("录制失败：视频内容为空，请重试");
        }
      }
    }, recordingDuration);
  } catch (error) {
    console.error("录制失败:", error);
    message.error("录制失败: " + error.message);
    isRecording.value = false;
    recordingCountdown.value = 0;
  }
};

const startRecordingTimer = () => {
  recordingTimer = setInterval(() => {
    const state = videoRecorder.getRecordingState();
    recordingDuration.value = state.duration;
    Object.assign(recordingStats, state.stats);
  }, 100);
};

const stopRecordingTimer = () => {
  if (recordingTimer) {
    clearInterval(recordingTimer);
    recordingTimer = null;
  }
};

// 历史记录方法
const updateHistoryState = () => {
  const info = imageProcessor.getImageInfo();
  if (info) {
    canUndo.value = info.canUndo;
    canRedo.value = info.canRedo;
  }
};

const undo = () => {
  const action = imageProcessor.undo();
  if (action) {
    message.info(`撤销: ${action}`);
    updateHistoryState();
  }
};

const redo = () => {
  const action = imageProcessor.redo();
  if (action) {
    message.info(`重做: ${action}`);
    updateHistoryState();
  }
};

const reset = async () => {
  try {
    Modal.confirm({
      title: "确认重置",
      content: "确定要重置所有修改吗？",
      onOk() {
        imageProcessor.reset();
        brightness.value = 0;
        contrast.value = 0;
        zoomLevel.value = 1;
        updateHistoryState();
        message.success("已重置");
      },
    });
  } catch {
    // 用户取消
  }
};

// 保存和导出方法
const saveImage = async () => {
  if (!currentImage.value) {
    message.warning("没有可保存的图片");
    return;
  }

  try {
    const defaultFilename = `image_${new Date().getTime()}.png`;
    const result = await ShowSaveFileDialog(defaultFilename);

    if (result.success && result.data) {
      // 获取图片数据并保存
      const dataURL = imageProcessor.getImageDataURL();
      if (dataURL) {
        // 这里需要通过Go后端保存文件
        // 暂时使用浏览器下载
        imageProcessor.downloadImage(result.data);
        message.success("图片已保存");
      }
    }
  } catch (error) {
    console.error("Save image failed:", error);
    message.error("保存图片失败");
  }
};

const exportVideo = () => {
  if (!hasRecordedVideo.value) {
    message.warning("没有可导出的视频");
    return;
  }

  const filename = `video_${new Date().getTime()}`;
  videoRecorder.downloadRecording(filename);
  message.success("视频已导出");
};

// 连接设置方法
const applyConnectionSettings = () => {
  showConnectionSettings.value = false;
  message.success("连接设置已更新");
};

// 工具函数
const formatTime = (ms) => {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes.toString().padStart(2, "0")}:${remainingSeconds
    .toString()
    .padStart(2, "0")}`;
};

const getPriorityText = (priority) => {
  const priorityMap = {
    urgent: "紧急",
    high: "高",
    normal: "普通",
    low: "低",
  };
  return priorityMap[priority] || priority || "-";
};

const getEyeSideText = (eyeSide) => {
  const eyeSideMap = {
    left: "左眼",
    right: "右眼",
    both: "双眼",
  };
  return eyeSideMap[eyeSide] || eyeSide || "-";
};

// 缩略图相关方法
const selectThumbnail = (index) => {
  selectedThumbnailIndex.value = index;
  const thumbnail = thumbnails.value[index];

  if (!thumbnail) {
    console.warn("缩略图不存在:", index);
    return;
  }

  console.log("选中缩略图:", {
    index,
    type: thumbnail.type,
    hasVideoUrl: !!thumbnail.videoUrl,
    hasSrc: !!thumbnail.src,
    hasFullImageUrl: !!thumbnail.fullImageUrl,
    isExisting: thumbnail.isExisting,
  });

  if (thumbnail.type === "video") {
    if (thumbnail.videoUrl) {
      // 视频有URL: 播放视频
      viewerImageUrl.value = thumbnail.videoUrl;
      showImageViewer.value = true;
    } else if (thumbnail.src) {
      // 视频没有URL但有封面: 显示封面图片
      viewerImageUrl.value = thumbnail.src;
      showImageViewer.value = true;
      message.info("暂无法播放已保存的视频,显示封面图片");
    }
  } else if (thumbnail.src) {
    // 图片: 优先使用完整图片URL,否则使用缩略图base64
    viewerImageUrl.value = thumbnail.fullImageUrl || thumbnail.src;
    showImageViewer.value = true;
  } else {
    console.warn("缩略图没有可显示的内容");
    message.warning("缩略图数据不完整");
  }
};

const loadImageFromThumbnail = (thumbnail) => {
  // 这里可以实现从缩略图加载完整图像的逻辑
  console.log("Loading image from thumbnail:", thumbnail);
};

const addThumbnail = (imageData, metadata = {}) => {
  // 添加新的缩略图
  const thumbnail = {
    src: imageData, // 封面图片/缩略图base64
    timestamp: Date.now(),
    id: thumbnails.value.length,
    type: metadata.type || "image", // 'image' 或 'video'
    videoUrl: metadata.videoUrl || null, // 视频URL
    videoBlob: metadata.videoBlob || null, // 视频Blob
    duration: metadata.duration || 0, // 视频时长（秒）
    eyeSide: metadata.eyeSide, // 拍摄模式：gray/color
    mediaId: metadata.mediaId || null, // 数据库中的ID（用于删除）
    isExisting: metadata.isExisting || false, // 是否是已存在的媒体
    fullImageUrl: metadata.fullImageUrl || null, // 完整图片URL（用于查看原图）
  };

  thumbnails.value.push(thumbnail);
  selectedThumbnailIndex.value = thumbnails.value.length - 1;
};

const deleteThumbnail = async (index) => {
  if (index < 0 || index >= thumbnails.value.length) {
    return;
  }

  const thumbnail = thumbnails.value[index];

  // 如果有mediaId,说明是已保存到数据库的媒体,需要调用API删除
  if (thumbnail.mediaId) {
    try {
      // 确认删除
      await Modal.confirm({
        title: "",
        content: `确定要删除这${thumbnail.type === "video" ? "个视频" : "张图片"
          }吗？`,
        okText: "确定",
        cancelText: "取消",
        onOk: async () => {
          try {
            const response = await imageAPI.deleteFundusImage(
              thumbnail.mediaId
            );

            if (isResponseSuccess(response)) {
              // 从缩略图列表中移除
              thumbnails.value.splice(index, 1);

              // 调整选中的索引
              if (selectedThumbnailIndex.value >= thumbnails.value.length) {
                selectedThumbnailIndex.value = thumbnails.value.length - 1;
              } else if (selectedThumbnailIndex.value > index) {
                selectedThumbnailIndex.value--;
              }

              // 如果删除的是当前选中的，且还有其他缩略图，选中相邻的
              if (
                selectedThumbnailIndex.value === index &&
                thumbnails.value.length > 0
              ) {
                selectedThumbnailIndex.value = Math.min(
                  index,
                  thumbnails.value.length - 1
                );
              }

              message.success(getResponseMessage(response) || "删除成功");
            } else {
              message.error(getResponseMessage(response) || "删除失败");
            }
          } catch (error) {
            console.error("删除媒体失败:", error);
            message.error("删除失败: " + (error.message || "未知错误"));
          }
        },
      });
    } catch (error) {
      // 用户取消删除
      console.log("用户取消删除");
    }
  } else {
    // 未保存到数据库的临时缩略图,直接从列表中删除
    thumbnails.value.splice(index, 1);

    // 调整选中的索引
    if (selectedThumbnailIndex.value >= thumbnails.value.length) {
      selectedThumbnailIndex.value = thumbnails.value.length - 1;
    } else if (selectedThumbnailIndex.value > index) {
      selectedThumbnailIndex.value--;
    }

    // 如果删除的是当前选中的，且还有其他缩略图，选中相邻的
    if (selectedThumbnailIndex.value === index && thumbnails.value.length > 0) {
      selectedThumbnailIndex.value = Math.min(
        index,
        thumbnails.value.length - 1
      );
    }

    message.success("删除成功");
  }
};

const handleZoomChange = (value) => {
  // 处理缩放变化
  if (imageProcessor) {
    imageProcessor.setZoom(value);
  }
};

// 自动对焦方法
const autoFocus = async () => {
  try {
    message.loading("正在自动对焦...", 0);
    console.log("执行自动对焦");

    // 发送自动对焦命令到设备
    // 自动对焦功能已移除（直接连接第三方 WebSocket）

    // 模拟对焦过程
    setTimeout(() => {
      message.destroy();
      message.success("自动对焦完成");
    }, 1500);
  } catch (error) {
    message.destroy();
    console.error("自动对焦失败:", error);
    message.error("自动对焦失败");
  }
};

// 复位方法
const resetDevice = async () => {
  try {
    message.loading("正在复位设备...", 0);
    console.log("执行设备复位");

    // 发送复位请求到后端
    const response = await hardwareAPI.resetDevice();
    message.destroy();

    if (isResponseSuccess(response)) {
      console.log("✅ 设备复位成功");
      message.success(getResponseMessage(response) || "设备已复位");
    } else {
      console.error("❌ 设备复位失败:", getResponseMessage(response));
      message.error(getResponseMessage(response) || "设备复位失败");
    }
  } catch (error) {
    message.destroy();
    console.error("设备复位请求失败:", error);
    message.error("设备复位失败: " + (error.message || "未知错误"));
  }
};

// 获取眼睛左右状态方法
const getEyeSideStatus = async () => {
  try {
    eyeSideStatusLoading.value = true;
    console.log("获取眼睛左右状态...");

    // 调用硬件API获取眼睛状态，禁用全局loading
    const response = await hardwareAPI.getEyeSideStatus({ showLoading: false });

    if (isResponseSuccess(response)) {
      console.log("✅ 眼睛状态获取成功:", response.data);

      // 根据响应数据设置眼睛状态
      if (response.data.status === "OD") {
        eyeSideStatus.value = "OD";
        message.success("当前眼睛状态: 右眼");
      } else if (response.data.status === "OS") {
        eyeSideStatus.value = "OS";
        message.success("当前眼睛状态: 左眼");
      } else {
        console.warn("未知的眼睛状态:", response.data);
        eyeSideStatus.value = response.data || "未知";
        message.info(`当前眼睛状态: ${response.data || "未知"}`);
      }
    } else {
      console.error("❌ 眼睛状态获取失败:", response);
      message.error(getResponseMessage(response) || "获取眼睛状态失败");
      eyeSideStatus.value = "";
    }
  } catch (error) {
    console.error("❌ 眼睛状态请求失败:", error);
    message.error("获取眼睛状态失败: " + (error.message || "网络错误"));
    eyeSideStatus.value = "";
  } finally {
    eyeSideStatusLoading.value = false;
  }
};

// 方向控制方法
const moveDirection = async (pos) => {
  try {
    console.log("设置壁纸位置:", pos);
    if (pos === "中") {
      await getEyeSideStatus();
    }
    if (pos === "中" && eyeSideStatus.value === "OD") {
      pos = "右中";
    }
    if (pos === "中" && eyeSideStatus.value === "OS") {
      pos = "左中";
    }
    // 调用壁纸位置设置API
    const response = await hardwareAPI.setWallpaperPosition(pos);

    if (response && response.code === 200) {
      console.log("壁纸位置设置成功:", response);
      message.success(`壁纸位置已设置为: ${pos}`);
    } else {
      console.error("壁纸位置设置失败:", response);
      message.error(response?.msg || "壁纸位置设置失败");
    }
  } catch (error) {
    console.error("方向控制请求失败:", error);
    message.error("方向控制失败: " + (error.message || "网络错误"));
  }
};

// 眼底图谱方法
const openFundusAtlas = () => {
  console.log("打开眼底图谱");
  message.info("眼底图谱功能开发中...");
  // TODO: 实现眼底图谱功能
  // 可以跳转到眼底图谱页面或打开图谱对话框
};

// 历史检查方法
const openHistoryExamination = () => {
  console.log("打开历史检查");
  message.info("历史检查功能开发中...");
  // TODO: 实现历史检查功能
  // 可以跳转到历史检查页面或打开历史记录对话框
};
const getYMD = () => {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}${month}${day}`;
}
// 拍照方法
const captureImage = async () => {
  if (isCapturing.value) return; // 防止重复点击

  try {
    isCapturing.value = true;

    // 调用眼睛状态方法，禁用全局loading
    await getEyeSideStatus();

    // 获取配置，禁用全局loading
    const res = await configAPI.getOtherConfig({ showLoading: false });
    if (res.code != 200) {
      console.error("❌ 获取其他配置失败:", res);
      return;
    }
    const { server, third_party, save_folder_path } = res.data;
    console.log("✅ 获取save_folder_path配置成功:", save_folder_path);
    // 直接使用 eyeSideStatus.value 的值（数据库使用 'OS'/'OD'）
    const eyeSideForCapture = eyeSideStatus.value;
    console.log("📸 拍照使用眼睛状态:", eyeSideForCapture);

    // saveFolderPath/{patient_id}/{年月日}_{examination_id}
    const ymd = getYMD();
    const folderpath = save_folder_path + patientInfo.patientId + "/" + ymd + "_" + patientInfo.examinationId;

    // 硬件拍照，禁用全局loading
    const response = await hardwareAPI.captureImage(captureMode.value, folderpath, { showLoading: false });
    if (!isResponseSuccess(response)) {
      console.error("❌ 拍照失败:", response);
      message.error(getResponseMessage(response) || "拍照失败");
      return;
    }
    // 检查是否有图像数据
    if (!response.data || response.data.length === 0) {
      console.error("❌ 拍照返回空数据");
      message.error("拍照返回空数据");
      return;
    }
    const imageDataInfo = response.data;
    // 保存到服务器和数据库
    try {
      const saveData = {
        examination_id: patientInfo.examinationId, // 检查ID
        patient_id: patientInfo.patientId, // 患者ID，保持字符串类型
        file_dir: folderpath,
        eye_side: eyeSideForCapture,
        image_type: patientInfo.examinationType,
        resolution: imageDataInfo.resolution,
        file_format: imageDataInfo.file_format,
        acquisition_device: "Camera",
        capture_mode: captureMode.value,
      };

      console.log("📸 保存图片数据:", {
        examination_id: saveData.examination_id,
        registration_id: saveData.registration_id,
        eye_side: saveData.eye_side,
      });
      let response;
      if (captureMode.value === "gray") {
        saveData.image_name = imageDataInfo.file[0];
        response = await workerManager.saveImage(saveData, { showLoading: false });

      } else {
        saveData.image_name = imageDataInfo.file;
        response = await workerManager.saveMultiImage(saveData, { showLoading: false });
      }

      if (!isResponseSuccess(response)) {
        // 保存失败
        message.warning("拍照成功，但保存到数据库失败");
      }
      console.log("图片已保存到数据库:", response.data);
      const resImgData = response.data;
      if (captureMode.value === "gray") {
        // 添加到缩略图列表,包含mediaId用于后续删除
        addThumbnail("data:image/jpeg;base64," + resImgData.thumbnailData, {
          type: "image",
          eyeSide: eyeSideForCapture,
          mediaId: response.data.id, // 保存返回的ID
          isExisting: false,
          capture_mode: response.data.capture_mode,
        });
      } else {
        resImgData.images.forEach(element => {
          addThumbnail("data:image/jpeg;base64," + element.thumbnail_data, {
            type: "image",
            eyeSide: eyeSideForCapture,
            mediaId: element.id, // 保存返回的ID
            isExisting: false,
            capture_mode: resImgData.capture_mode,
          });
        });

        try {
          // 停止设备
          await hardwareAPI.stopDevice();
          deviceStatus.value = "stopped";

          // 清空左侧实时画面
          clearLiveView();
        } catch (error) {
          console.error("停止设备失败:", error);
          deviceStatus.value = "running"; // 恢复到运行状态，因为停止失败
        }
      }
      message.success(getResponseMessage(response) || "拍照成功并已保存");

    } catch (error) {
      console.error("保存图片到服务器失败:", error);
      // 保存失败
      message.warning("拍照成功，但保存到数据库失败");
    }

  } catch (error) {
    console.error("拍照失败:", error);
    message.error("拍照失败");
  } finally {
    isCapturing.value = false; // 重置拍照状态
  }
};

// AI诊断方法 - 从预览窗口触发
const performAIDiagnosis = async () => {
  const thumbnail = thumbnails.value[selectedThumbnailIndex.value];

  if (!thumbnail) {
    message.warning("未选择图片");
    return;
  }

  if (thumbnail.type === "video") {
    message.warning("视频暂不支持AI诊断");
    return;
  }

  try {
    aiDiagnosing.value = true;
    message.loading("AI诊断中，请稍候...", 0);

    console.log("开始AI诊断(预览窗口):", {
      mediaId: thumbnail.mediaId,
      eyeSide: thumbnail.eyeSide,
      isExisting: thumbnail.isExisting,
    });

    // TODO: 调用AI诊断API
    // const response = await imageAPI.performAIDiagnosis({
    //   image_id: thumbnail.mediaId,
    //   image_data: thumbnail.src,
    //   eye_side: thumbnail.eyeSide
    // });

    // 模拟AI诊断过程
    await new Promise((resolve) => setTimeout(resolve, 2000));

    message.destroy();

    // TODO: 显示AI诊断结果
    message.success("AI诊断完成！");

    // 可以在这里打开一个新的对话框显示诊断结果
    // showAIDiagnosisResult(response.data);
  } catch (error) {
    message.destroy();
    console.error("AI诊断失败:", error);
    message.error("AI诊断失败: " + (error.message || "未知错误"));
  } finally {
    aiDiagnosing.value = false;
  }
};

// AI诊断方法 - 从中间面板触发 (跳转到诊断界面)
const performAIDiagnosisFromPanel = async () => {
  if (!hasImageForDiagnosis.value) {
    message.warning("请先拍摄照片或录制视频");
    return;
  }

  console.log("跳转到AI诊断界面");
  console.log("患者信息:", patientInfo);
  console.log("缩略图列表:", thumbnails.value.length);

  // 跳转到AI诊断界面,携带患者信息
  router.push({
    path: "/ai-diagnosis",
    query: {
      registrationId: patientInfo.registrationId,
      examinationId: patientInfo.examinationId, // 添加检查ID，用于加载图片
      patientData: JSON.stringify(patientInfo),
    },
  });
};

// 刷新查看器图片
const refreshViewerImage = async () => {
  const thumbnail = thumbnails.value[selectedThumbnailIndex.value];

  if (!thumbnail) {
    message.warning("未选择媒体");
    return;
  }

  try {
    console.log("刷新查看器图片:", {
      index: selectedThumbnailIndex.value,
      mediaId: thumbnail.mediaId,
      type: thumbnail.type,
      isExisting: thumbnail.isExisting,
    });

    if (thumbnail.isExisting && thumbnail.mediaId) {
      // 如果是已保存的媒体，重新从服务器加载
      message.loading("正在刷新...", 0);

      // TODO: 从服务器重新加载图片
      // const response = await imageAPI.getFundusImageById(thumbnail.mediaId);
      // if (isResponseSuccess(response)) {
      //   viewerImageUrl.value = response.data.thumbnail_data;
      //   message.success('刷新成功');
      // }

      // 模拟刷新
      await new Promise((resolve) => setTimeout(resolve, 500));

      message.destroy();

      // 强制刷新图片
      if (viewerImage.value) {
        const currentSrc = viewerImageUrl.value;
        viewerImageUrl.value = "";
        await nextTick();
        viewerImageUrl.value = currentSrc;
      }

      message.success("刷新成功");
    } else {
      // 临时图片，直接刷新显示
      const currentSrc = viewerImageUrl.value;
      viewerImageUrl.value = "";
      await nextTick();
      viewerImageUrl.value = currentSrc;
      message.success("刷新成功");
    }
  } catch (error) {
    message.destroy();
    console.error("刷新失败:", error);
    message.error("刷新失败: " + (error.message || "未知错误"));
  }
};

// 加载已保存的图片和视频
const loadExistingMedia = async () => {
  if (!patientInfo.registrationId) {
    console.log("没有 examination_id,跳过加载已有媒体");
    return;
  }

  try {
    console.log("🔍 加载检查ID的已保存媒体:", patientInfo.registrationId);

    // 调用 API 获取该检查的所有图片和视频
    const response = await imageAPI.getFundusImages({
      examination_id: patientInfo.examinationId || patientInfo.registrationId, // 优先使用examinationId
      page: 1,
      page_size: 100, // 加载所有
    });

    if (isResponseSuccess(response)) {
      const mediaList = response.data.data || [];
      console.log(`✅ 加载了 ${mediaList.length} 个媒体文件`);

      // 遍历并添加到缩略图列表
      for (const media of mediaList) {
        // 使用缩略图base64数据
        const thumbnailSrc = media.thumbnail_data || null;

        if (!thumbnailSrc) {
          console.warn("媒体没有缩略图数据:", media.id);
          continue; // 跳过没有缩略图的项
        }

        // 构建文件URL用于完整图片/视频访问 (暂时不使用,因为需要认证)
        // const fileUrl = `http://localhost:8080/api/images/file/${media.id}`;

        if (media.image_type === "video") {
          // 视频: 使用缩略图base64作为封面
          // 注意: 视频播放暂时使用缩略图,因为文件URL需要认证
          addThumbnail(thumbnailSrc, {
            type: "video",
            videoUrl: null, // 暂时不提供视频URL,因为需要认证token
            duration: media.duration || 10,
            eyeSide: media.eye_side,
            mediaId: media.id,
            isExisting: true, // 标记为已存在的媒体
          });
        } else {
          // 图片: 使用缩略图base64
          // 点击缩略图时直接显示缩略图base64 (已经是完整图片)
          addThumbnail(thumbnailSrc, {
            type: "image",
            fullImageUrl: null, // 不使用文件URL,直接使用base64
            eyeSide: media.eye_side,
            mediaId: media.id,
            isExisting: true,
          });
        }
      }

      // if (mediaList.length > 0) {
      //   message.success(`已加载 ${mediaList.length} 个已保存的图片/视频`);
      // }
    } else {
      console.warn("加载已保存媒体失败:", getResponseMessage(response));
    }
  } catch (error) {
    console.error("加载已保存媒体失败:", error);
  }
};

// 生命周期
onMounted(async () => {
  // 获取患者store
  const patientStore = usePatientStore();

  // 尝试从本地存储初始化store
  patientStore.initializePatientState();

  console.log("🔍 Store初始化后状态:", {
    hasPatientInfo: patientStore.hasPatientInfo,
    currentPatient: patientStore.currentPatient,
    currentExamination: patientStore.currentExamination
  });

  // 首先尝试从pinia store获取患者信息
  let patientDataFromStore = null;
  let examinationDataFromStore = null;

  if (patientStore.hasPatientInfo) {
    patientDataFromStore = patientStore.getCurrentPatient;
    examinationDataFromStore = patientStore.getCurrentExamination;
    console.log("✅ 从pinia store获取患者信息:", patientDataFromStore);
    console.log("✅ 从pinia store获取检查记录信息:", examinationDataFromStore);
    console.log("🔍 患者姓名:", patientDataFromStore?.name);
    console.log("🔍 检查记录ID:", examinationDataFromStore?.id);
    console.log("🔍 眼别信息(store):", examinationDataFromStore?.eye_side);
  } else {
    console.log("❌ pinia store中没有患者信息");
    console.log("🔍 当前store状态:", {
      hasPatientInfo: patientStore.hasPatientInfo,
      currentPatient: patientStore.currentPatient,
      currentExamination: patientStore.currentExamination
    });
  }

  // 如果pinia store中有数据，优先使用
  if (patientDataFromStore && examinationDataFromStore) {
    Object.assign(patientInfo, {
      registrationId: examinationDataFromStore.registration_id,
      examinationId: examinationDataFromStore.id,
      registrationNumber: examinationDataFromStore.registration_number,
      patientId: patientDataFromStore.id,
      patientName: patientDataFromStore.name,
      patientNumber: patientDataFromStore.patient_id,
      examinationType: examinationDataFromStore.examination_type,
      examinationTypeId: examinationDataFromStore.examination_type_id,
      department: examinationDataFromStore.department,
      doctorId: examinationDataFromStore.doctor_id,
      doctorName: examinationDataFromStore.doctor_name,
      scheduledDate: examinationDataFromStore.scheduled_date,
      scheduledTime: examinationDataFromStore.scheduled_time,
      priority: examinationDataFromStore.priority,
      notes: examinationDataFromStore.notes,
      gender: patientDataFromStore.gender,
      age: patientDataFromStore.age,
      eyeSide: examinationDataFromStore.eye_side,
    });
    console.log("✅ 使用pinia store中的患者信息");
  } else {
    // 如果pinia store中没有数据，尝试从URL参数获取
    if (router.currentRoute.value.query.patientData) {
      try {
        const data = JSON.parse(router.currentRoute.value.query.patientData);
        Object.assign(patientInfo, data);
        console.log("✅ 从URL参数获取患者信息:", patientInfo);
      } catch (error) {
        console.error("解析患者信息失败:", error);
      }
    } else {
      // 如果没有完整的患者数据，尝试从单独的查询参数获取
      Object.assign(patientInfo, {
        registrationId: router.currentRoute.value.query.registrationId,
        examinationId: router.currentRoute.value.query.examinationId, // 检查记录ID
        registrationNumber: router.currentRoute.value.query.registrationNumber,
        patientId: router.currentRoute.value.query.patientId,
        patientName: router.currentRoute.value.query.patientName,
        patientNumber: router.currentRoute.value.query.patientNumber,
        examinationType: router.currentRoute.value.query.examinationType,
        examinationTypeId: router.currentRoute.value.query.examinationTypeId,
        department: router.currentRoute.value.query.department,
        doctorId: router.currentRoute.value.query.doctorId,
        doctorName: router.currentRoute.value.query.doctorName,
        scheduledDate: router.currentRoute.value.query.scheduledDate,
        scheduledTime: router.currentRoute.value.query.scheduledTime,
        priority: router.currentRoute.value.query.priority,
        notes: router.currentRoute.value.query.notes,
        gender: router.currentRoute.value.query.gender,
        age: router.currentRoute.value.query.age,
        eyeSide: router.currentRoute.value.query.eyeSide,
      });
      console.log("✅ 从查询参数获取患者信息");
    }
  }

  // 如果URL中有examinationId但没有患者信息，尝试从数据库获取
  if (router.currentRoute.value.query.examinationId && !patientInfo.patientName) {
    try {
      console.log("🔍 从数据库获取检查记录信息:", router.currentRoute.value.query.examinationId);
      const examinationAPI = (await import("@/api/examination")).default;
      const response = await examinationAPI.getExamination(router.currentRoute.value.query.examinationId);

      if (response.success || (response.code && response.code >= 200 && response.code < 300)) {
        const examination = response.data;
        console.log("✅ 从数据库获取检查记录成功:", examination);
        console.log("🔍 数据库眼别信息:", examination.eye_side);

        // 更新患者信息
        Object.assign(patientInfo, {
          examinationId: examination.id,
          examinationType: examination.examination_type?.type_name,
          examinationTypeId: examination.examination_type_id,
          department: examination.department,
          doctorId: examination.doctor_id,
          doctorName: examination.doctor?.full_name,
          scheduledDate: examination.scheduled_date,
          scheduledTime: examination.scheduled_time,
          priority: examination.priority,
          notes: examination.notes,
          eyeSide: examination.eye_side,
        });

        // 如果有患者信息，也更新
        if (examination.patient) {
          Object.assign(patientInfo, {
            patientId: examination.patient.id,
            patientName: examination.patient.name,
            patientNumber: examination.patient.patient_id,
            gender: examination.patient.gender,
            age: examination.patient.age,
          });
        }

        console.log("✅ 患者信息已从数据库更新");
      }
    } catch (error) {
      console.error("从数据库获取检查记录失败:", error);
    }
  }

  console.log("📋 最终患者信息:", patientInfo);
  console.log("📋 关键ID信息:", {
    registrationId: patientInfo.registrationId,
    examinationId: patientInfo.examinationId,
  });
  console.log("🔍 患者姓名:", patientInfo.patientName);
  console.log("🔍 患者编号:", patientInfo.patientNumber);
  console.log("🔍 检查类型:", patientInfo.examinationType);
  console.log("🔍 眼别信息:", patientInfo.eyeSide);

  // 如果是新检查模式，检查记录已在跳转前创建
  if (router.currentRoute.value.query.mode === 'new_examination' || patientStore.isNewExaminationMode) {
    console.log("🆕 新检查模式：检查记录已创建", patientInfo.examinationId);
    message.info("新检查记录已创建，可以开始采集图像");
  }

  initializeComponents();
  await initializeCanvas();

  // 启动摄像头预览
  await startCamera();
  startRenderLoop();

  // 加载已保存的图片和视频（如果有examinationId）
  if (patientInfo.examinationId) {
    await loadExistingMedia();
  }

  // 监听窗口大小变化
  window.addEventListener("resize", () => {
    console.log("Window resized, reinitializing canvas...");
    setTimeout(() => initializeCanvas(), 100);
  });
});

onUnmounted(() => {
  console.log("🗑️ 组件卸载 - 开始清理资源");

  // 1. 自动执行关闭按钮（断开连接）
  console.log("🛑 页面离开，自动执行关闭按钮");
  if (connectionStatus.value === "connected") {
    try {
      // 先请求停止设备
      hardwareAPI.stopDevice().catch((e) => console.warn('停止设备失败(可忽略):', e?.message || e));
      // 再断开WebSocket连接
      disconnectWebSocket();
      // 停止渲染循环
      stopRenderLoop();
      // 清空左侧实时画面
      clearLiveView();

      console.log("✅ 自动关闭连接完成");
    } catch (error) {
      console.error("自动关闭连接失败:", error);
    }
  } else {
    // 即使没有连接，也停止渲染循环并清空左侧实时画面
    stopRenderLoop();
    clearLiveView();
  }

  // 2. 关闭摄像头预览
  stopCamera();

  // 3. 停止所有定时器和循环
  // stopRenderLoop() 已在上方调用，此处不需要重复调用

  if (recordingTimer) {
    clearInterval(recordingTimer);
    recordingTimer = null;
  }

  // 3. 停止录制（如果正在录制）
  if (isRecording.value && videoRecorder) {
    try {
      videoRecorder.stopRecording();
      console.log("录制已停止");
    } catch (error) {
      console.error("停止录制失败:", error);
    }
  }

  // 4. 清理所有 Blob URLs（防止内存泄漏）
  if (lastFrameBlobUrl) {
    URL.revokeObjectURL(lastFrameBlobUrl);
    lastFrameBlobUrl = null;
  }

  // 清理缩略图中的 Blob URLs
  thumbnails.value.forEach(thumbnail => {
    if (thumbnail.videoUrl && thumbnail.videoUrl.startsWith('blob:')) {
      URL.revokeObjectURL(thumbnail.videoUrl);
    }
  });

  // 清理所有 blobUrls 数组中的 URL
  blobUrls.value.forEach(url => {
    if (url && url.startsWith('blob:')) {
      URL.revokeObjectURL(url);
    }
  });
  blobUrls.value = [];

  console.log("🧹 已清理所有 Blob URLs");

  // 5. 清理组件资源
  if (imageProcessor) {
    try {
      imageProcessor.dispose();
      imageProcessor = null;
    } catch (error) {
      console.error("清理 ImageProcessor 失败:", error);
    }
  }

  if (videoRecorder) {
    try {
      videoRecorder.dispose();
      videoRecorder = null;
    } catch (error) {
      console.error("清理 VideoRecorder 失败:", error);
    }
  }

  // 6. 清理事件监听器
  window.removeEventListener("resize", initializeCanvas);

  // 7. 清理变量引用
  latestFrameBuffer = null;
  isProcessing = false;
  currentFrameData = null;
  currentFrameBlob = null;

  console.log("✅ 组件卸载完成，所有资源已清理");
});

// 组件激活时处理
onActivated(() => {
  console.log("🔄 组件激活 - ViewImages");

  // 重新启动摄像头预览
  if (cameraStatus.value === "inactive" || cameraStatus.value === "error") {
    console.log("组件激活，重新启动摄像头...");
    startCamera();
  }

  // 启动渲染循环
  startRenderLoop();
});

// 组件失活时处理
onDeactivated(() => {
  console.log("⏸️ 组件失活 - ViewImages");
  // 暂停录制（如果正在录制）
  if (isRecording.value && videoRecorder) {
    try {
      videoRecorder.pauseRecording();
      console.log("录制已暂停");
    } catch (error) {
      console.error("暂停录制失败:", error);
    }
  }
  try {
    // 先请求停止设备
    hardwareAPI.stopDevice().catch((e) => console.warn('停止设备失败(可忽略):', e?.message || e));
    // 再断开WebSocket连接
    disconnectWebSocket();
    // 停止渲染循环
    stopRenderLoop();
    // 清空左侧实时画面
    clearLiveView();

    console.log("✅ 自动关闭连接完成");
  } catch (error) {
    console.error("自动关闭连接失败:", error);
  }
});
</script>

<style lang="scss" scoped>
.view-images-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #000000; // 纯黑色背景
  color: #ffffff; // 白色文字
}

// 页面顶部Logo区域
.page-header {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000000; // 纯黑色背景
  flex-shrink: 0; // 防止被压缩

  .logo-container {
    display: flex;
    justify-content: center;
    align-items: center;

    .page-logo {
      height: 25px; // 设置logo高度
      width: auto; // 宽度自适应
      max-width: 200px; // 最大宽度限制
      object-fit: contain; // 保持宽高比
      filter: brightness(1.1); // 稍微提高亮度以适应暗色背景
    }
  }
}

// 患者信息样式 - 移到中间面板顶部
.patient-info-brief {
  padding: 0 8px;

  .patient-brief {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    padding: 8px 12px;
    background: #1a1a1a; // 暗灰色背景
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background: #2a2a2a;
    }

    .patient-name {
      color: #e0e0e0; // 柔和浅灰色
      font-weight: 500;
      font-size: 14px;
    }

    .patient-number {
      color: #b0b0b0; // 中等灰色
      font-size: 12px;
      background: #0a0a0a; // 接近黑色
      padding: 2px 6px;
      border-radius: 2px;
    }

    .exam-type {
      color: #66b1ff; // 柔和的蓝色
      font-size: 12px;
      background: rgba(64, 158, 255, 0.15); // 稍微加深背景
      padding: 2px 6px;
      border-radius: 2px;
    }

    .eye-side {
      color: #52c41a; // 柔和的绿色
      font-size: 12px;
      background: rgba(82, 196, 26, 0.15); // 绿色背景
      padding: 2px 6px;
      border-radius: 2px;
    }
  }
}

// 主要内容区域 - 三列布局
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  gap: 1px; // 列之间的间隙

  // 左侧面板 - 实时图像
  .left-panel {
    flex: 2; // 占据更多空间
    display: flex;
    flex-direction: column;
    background: #000000;
    border-right: none; // 移除边框
    // 确保正方形显示区域能够正确显示
    align-items: center;
    justify-content: center;

    .image-container {
      position: relative;
      background: #000000; // 纯黑色背景
      overflow: hidden;
      min-height: 400px; // 确保最小高度
      // 确保正方形显示区域
      aspect-ratio: 1 / 1; // 1:1 宽高比，保持正方形
      width: min(100%, 100vh - 200px); // 确保不超过视窗高度
      height: auto; // 高度由aspect-ratio自动计算
      max-width: 100%;
      max-height: 100%;

      .main-canvas {
        width: 100%;
        height: 100%;
        display: block;
        min-height: 400px; // 确保canvas最小高度
        border: none; // 移除边框
        box-sizing: border-box;
        background-color: #000000; // 黑色背景
        z-index: 1;
        position: relative;
        // 确保canvas也是正方形
        object-fit: contain; // 保持宽高比
      }

      .empty-state {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        @include flex-center;
        background: rgba(0, 0, 0, 0.95); // 纯黑色半透明背景
        color: #ffffff; // 白色文字
        z-index: 2;
      }

      .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.9); // 纯黑色半透明背景
        color: #ffffff; // 白色文字
        @include flex-center;
      }
    }

    .image-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 16px;
      background: #000000;
      color: #ffffff;
      border-top: none; // 移除边框

      .image-label {
        font-size: 14px;
        font-weight: 500;
      }

      .status-info {
        display: flex;
        align-items: center;
        gap: 12px;

        .connection-status {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;

          .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;

            &.disconnected {
              background: #ff4d4f;
            }

            &.connecting {
              background: #faad14;
              animation: pulse 1s infinite;
            }

            &.connected {
              background: #52c41a;
            }
          }

          .status-text {
            color: #cccccc;
          }
        }
      }
    }
  }

  // 中间面板 - 用户信息和图像设置
  .center-panel {
    width: 300px;
    background: #000000; // 纯黑色背景
    border-right: none; // 移除边框
    // padding: $spacing-sm $spacing-md; // 减小上下内边距
    overflow-y: auto;
    @include scrollbar;
    display: flex;
    flex-direction: column;

    // 摄像头预览区域
    .camera-preview-section {
      padding: $spacing-sm;
      border-radius: 6px;
      border: none;

      .camera-preview-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .camera-title {
          color: #e0e0e0;
          font-size: 12px;
          font-weight: 500;
        }

        .camera-status {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 10px;

          .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            display: inline-block;
          }

          &.loading .status-dot {
            background: #faad14;
            animation: pulse 1s infinite;
          }

          &.active .status-dot {
            background: #52c41a;
          }

          &.error .status-dot {
            background: #ff4d4f;
          }

          &.inactive .status-dot {
            background: #808080;
          }

          .status-text {
            color: #b0b0b0;
          }
        }
      }

      .camera-preview-container {
        position: relative;
        width: 100%;
        height: 180px;
        background: #000000;
        border-radius: 4px;
        overflow: hidden;
        // margin-bottom: 8px;

        .camera-preview {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.2s ease;

          &.mirrored {
            transform: scaleX(-1);
          }
        }

        .camera-error,
        .camera-loading {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          background: rgba(0, 0, 0, 0.8);
          color: #b0b0b0;
          font-size: 10px;
          gap: 4px;

          .el-icon {
            font-size: 16px;
          }
        }
      }

      .camera-controls {
        display: flex;
        gap: 6px;

        .el-button {
          flex: 1;
          font-size: 10px;
          padding: 4px 8px;
          min-height: 24px;
        }
      }
    }

    .control-buttons {
      margin-bottom: $spacing-sm; // 减小底部间距
      padding: $spacing-sm; // 减小内边距
      background: #000000;
      border-radius: 6px; // 稍微减小圆角
      border: none; // 移除边框

      .capture-mode-selector {
        margin-bottom: 8px; // 增大间距
        background: #000000;
        border-radius: 6px; // 增大圆角
        display: flex;
        align-items: center;
        gap: 10px; // 增大间距
        // padding: 8px 12px; // 增加内边距

        label {
          color: #a0a0a0; // 柔和中灰色
          font-size: 14px; // 增大字体
          font-weight: 500;
        }

        :deep(.el-radio-group) {
          --el-color-primary: transparent; // 移除默认的主色

          .el-radio-button__inner {
            padding: 8px 16px; // 增大内边距
            font-size: 14px; // 增大字体
            font-weight: 500; // 加粗字体
            min-height: 36px; // 设置最小高度
            display: flex;
            align-items: center;
            justify-content: center;
          }
        }
      }

      .button-group {
        margin-bottom: 6px; // 进一步减小间距

        &:last-child {
          margin-bottom: 0;
        }

        .el-button {
          width: 100%;
          min-height: 36px; // 减小按钮高度
          font-size: 13px; // 减小字体
          font-weight: 500;
        }

        // 横向排列的按钮组
        &.button-group-row {
          display: flex;
          gap: 6px; // 减小间距

          .el-button {
            flex: 1;
            min-height: 32px; // 减小高度
            font-size: 12px; // 减小字体

            .el-icon {
              margin-right: 4px;
            }

            span {
              display: inline-block;
              margin-left: 0;
            }
          }

          // 自动对焦按钮
          .focus-btn {
            background: #505050 !important; // 统一灰色背景
            border-color: #606060 !important; // 统一灰色边框
            color: #ffffff !important; // 白色文字

            &:hover:not(:disabled) {
              background: #5a5a5a !important;
              border-color: #707070 !important;
            }

            &:disabled {
              background: #2a2a2a !important; // 更暗的灰色背景
              border-color: #3a3a3a !important; // 更暗的边框
              color: #808080 !important; // 中灰色文字
            }
          }

          // 复位按钮
          .reset-btn {
            background: #505050 !important; // 统一灰色背景
            border-color: #606060 !important; // 统一灰色边框
            color: #ffffff !important; // 白色文字

            &:hover:not(:disabled) {
              background: #5a5a5a !important;
              border-color: #707070 !important;
            }

            &:disabled {
              background: #2a2a2a !important; // 更暗的灰色背景
              border-color: #3a3a3a !important; // 更暗的边框
              color: #808080 !important; // 中灰色文字
            }
          }
        }
      }
    }

    .el-card {
      margin-bottom: $spacing-sm; // 减小卡片间距

      &.compact {
        background: #000000 !important;
        margin-bottom: $spacing-sm;

        :deep(.el-card__header) {
          padding: 0px 8px; // 减小header内边距
          font-size: 12px;
        }

        :deep(.el-card__body) {
          padding: 0px 8px; // 减小body内边距
        }
      }

      &:last-child {
        margin-bottom: 0;
      }
    }

    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px; // 减小间距

      &:last-child {
        margin-bottom: 0;
      }

      .label {
        color: #cccccc;
        font-size: 11px; // 减小字体
      }

      .value {
        color: #ffffff;
        font-weight: $font-weight-medium;
        font-size: 11px; // 减小字体
      }
    }

    // 设置行 - 横向布局
    .settings-row {
      display: flex;
      gap: 8px;
      align-items: flex-start;

      .setting-item-inline {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 4px;

        label {
          color: #a0a0a0; // 柔和中灰色
          font-size: 11px;
          font-weight: 500;
          white-space: nowrap;
        }

        .setting-select {
          width: 100%;
        }
      }
    }

    .adjustment-item,
    .setting-item {
      margin-bottom: 8px; // 减小间距

      &.compact {
        margin-bottom: 6px; // 紧凑模式更小间距
      }

      &:last-child {
        margin-bottom: 0;
      }

      label {
        display: block;
        margin-bottom: 4px; // 减小间距
        color: #a0a0a0; // 柔和中灰色
        font-size: 11px; // 减小字体
      }

      .setting-value {
        text-align: center;
        margin-top: 2px; // 减小间距
        color: #5fb878; // 柔和绿色（降低亮度）
        font-weight: 600;
        font-size: 11px; // 减小字体
      }
    }
  }

  // 功能按钮区域
  .function-buttons-row {
    color: #808080;
    padding: 0 8px;
    display: flex;
    gap: 6px; // 与button-group-row保持一致
    margin-bottom: 12px;
    justify-content: center; // 居中对齐

    .el-button {
      flex: 1;
      min-height: 32px; // 与button-group-row保持一致
      font-size: 12px; // 与button-group-row保持一致
      font-weight: 500;
      padding: 6px 8px; // 调整内边距
      text-align: center;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px; // 减小图标和文字间距

      .el-icon {
        font-size: 12px; // 与button-group-row保持一致
        margin-right: 4px; // 与button-group-row保持一致
      }

      span {
        white-space: nowrap;
        display: inline-block; // 与button-group-row保持一致
      }

      // 眼底图谱按钮样式
      &.atlas-btn {
        background: #505050 !important;
        border-color: #606060 !important;
        color: #808080 !important;

        &:hover {
          background: #5a5a5a !important;
          border-color: #707070 !important;
          color: #ffffff !important;
        }
      }

      // 历史检查按钮样式
      &.history-btn {
        background: #505050 !important;
        border-color: #606060 !important;
        color: #808080 !important;

        &:hover {
          background: #5a5a5a !important;
          border-color: #707070 !important;
          color: #ffffff !important;
        }
      }
    }
  }

  .direction-control {
    flex-shrink: 0; // 防止被压缩
    padding: 8px; // 减小内边距
    // background: #1a1a1a;
    border-radius: 6px; // 减小圆角
    border: none; // 移除边框
    margin-bottom: 8px; // 减小间距

    .direction-title {
      text-align: center;
      color: #b0b0b0; // 柔和中等灰色
      font-size: 11px; // 减小字体
      font-weight: 500;
      margin-bottom: 6px; // 减小间距
    }

    .direction-grid {
      display: flex;
      flex-direction: column;
      gap: 8px; // 增大间距以适应更大的按钮

      .direction-row {
        display: flex;
        justify-content: center;
        gap: 8px; // 增大间距以适应更大的按钮

        .direction-spacer {
          width: 48px; // 增大宽度以匹配按钮尺寸
        }

        .direction-btn {
          width: 48px; // 增大按钮尺寸
          height: 48px;
          padding: 0;
          background: #505050; // 中灰色背景
          border-color: #606060; // 灰色边框
          color: #ffffff; // 白色文字
          font-size: 16px; // 增大字体
          font-weight: 600; // 加粗字体

          &:hover {
            background: #5a5a5a;
            border-color: #707070;
            color: #ffffff;
            transform: scale(1.05);
          }

          &:active {
            transform: scale(0.95);
          }

          &.direction-center {
            background: #505050; // 统一灰色背景
            border-color: #606060; // 统一灰色边框
            color: #ffffff; // 白色文字

            &:hover {
              background: #5a5a5a;
              border-color: #707070;
              color: #ffffff;
            }
          }

          .el-icon {
            font-size: 18px; // 增大图标尺寸
          }
        }
      }
    }
  }

  .diagnosis-section {
    flex-shrink: 0; // 防止被压缩
    margin-top: auto; // 推到底部
    padding: 10px; // 减小内边距
    // background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 6px; // 减小圆角
    border: none; // 移除边框
    // box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3); // 减小阴影
    transition: all 0.3s ease;

    // 禁用状态 - 整体区域变暗淡
    &.is-disabled {
      background: linear-gradient(135deg,
          rgba(102, 126, 234, 0.2) 0%,
          rgba(118, 75, 162, 0.2) 100%);
      border-color: rgba(124, 58, 237, 0.3);
      box-shadow: 0 2px 6px rgba(102, 126, 234, 0.1);
    }

    .diagnosis-title {
      text-align: center;
      color: #ffffff;
      font-size: 12px; // 减小字体
      font-weight: 600;
      margin-bottom: 6px; // 减小间距
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }

    .back-btn {
      width: 100%;
      height: 40px; // 与诊断按钮相同高度
      margin-bottom: 8px; // 与诊断按钮的间距
      margin-left: 0 !important; // 覆盖Element Plus的默认margin-left
      font-size: 14px; // 与诊断按钮相同字体大小
      font-weight: 600; // 与诊断按钮相同字重
      background: #212121 !important; // 中灰色背景
      border-color: #606060 !important; // 灰色边框
      color: #ffffff !important; // 白色文字
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3); // 与诊断按钮相同阴影
      transition: all 0.3s ease; // 与诊断按钮相同过渡

      &:hover {
        background: #5a5a5a !important;
        border-color: #707070 !important;
        color: #ffffff !important;
        transform: translateY(-2px); // 与诊断按钮相同悬停效果
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
      }

      &:active {
        transform: translateY(0); // 与诊断按钮相同点击效果
      }
    }

    .diagnosis-btn {
      width: 100%;
      height: 40px; // 与返回按钮相同高度
      margin-left: 0 !important; // 覆盖Element Plus的默认margin-left
      font-size: 14px; // 与返回按钮相同字体大小
      font-weight: 600; // 与返回按钮相同字重
      background: #505050 !important; // 中灰色背景
      border-color: #606060 !important; // 灰色边框
      color: #ffffff !important; // 白色文字
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3); // 与返回按钮相同阴影
      transition: all 0.3s ease; // 与返回按钮相同过渡

      &:hover:not(:disabled) {
        background: #5a5a5a !important; // 悬停时稍亮
        border-color: #707070 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
      }

      &:active:not(:disabled) {
        transform: translateY(0);
      }

      // 禁用状态 - 极暗设计
      &:disabled {
        background: #2a2a2a !important; // 更暗的灰色背景
        border-color: #3a3a3a !important; // 更暗的边框
        color: #808080 !important; // 中灰色文字
        cursor: not-allowed;
        transform: none;
        box-shadow: none; // 移除阴影
      }

      &.is-loading {
        background: #505050 !important;
        border-color: #606060 !important;
      }
    }

    .diagnosis-hint {
      margin-top: 6px; // 减小间距
      padding: 6px 10px; // 减小内边距
      background: rgba(255, 255, 255, 0.08); // 更暗的背景
      border-radius: 4px;
      display: flex;
      align-items: center;
      gap: 4px; // 减小间距
      font-size: 10px; // 减小字体
      color: #d0d0d0; // 柔和文字

      .el-icon {
        font-size: 12px; // 减小图标
        color: #fbbf24;
        flex-shrink: 0;
      }

      span {
        flex: 1;
        opacity: 0.9;
        line-height: 1.2; // 减小行高
      }
    }
  }

  // 右侧面板 - 缩略图列表
  .right-panel {
    width: 150px;
    background: #000000;
    display: flex;
    flex-direction: column;

    .thumbnail-header {
      padding: $spacing-sm;
      border-bottom: none; // 移除边框
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #0a0a0a;

      .thumbnail-title {
        color: #ffffff;
        font-size: 14px;
        font-weight: 500;
      }

      .thumbnail-count {
        color: #cccccc;
        font-size: 12px;
      }
    }

    .thumbnail-list {
      flex: 1;
      padding: $spacing-sm;
      overflow-y: auto;
      @include scrollbar;
      display: flex;
      flex-direction: column;
      gap: $spacing-sm;

      .thumbnail-item {
        position: relative;
        cursor: pointer;
        border: 2px solid transparent;
        border-radius: 4px;
        transition: all 0.2s ease;
        background: #0a0a0a;

        &:hover {
          border-color: #555555;
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);

          .thumbnail-delete {
            opacity: 1;
          }
        }

        &.active {
          border-color: #409eff;
          box-shadow: 0 0 0 1px #409eff;
        }

        .thumbnail-image {
          width: 100%;
          height: 100px;
          background: #000000;
          border-radius: 2px;
          overflow: hidden;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;

          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }

          .thumbnail-placeholder {
            color: #666666;
            font-size: 12px;
            text-align: center;
          }

          .video-badge {
            position: absolute;
            bottom: 4px;
            right: 4px;
            background: rgba(0, 0, 0, 0.8);
            color: #ffffff;
            padding: 2px 6px;
            border-radius: 3px;
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 10px;

            .el-icon {
              font-size: 12px;
            }

            .video-duration {
              font-weight: 500;
            }
          }

          .eye-side-badge {
            position: absolute;
            top: 4px;
            left: 4px;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 600;
            color: #ffffff;

            &.left {
              background: rgba(24, 144, 255, 0.9); // 蓝色 - 左眼
            }

            &.right {
              background: rgba(250, 140, 22, 0.9); // 橙色 - 右眼
            }
          }
        }

        .thumbnail-index {
          position: absolute;
          bottom: 4px;
          left: 4px;
          background: rgba(0, 0, 0, 0.7);
          color: #ffffff;
          font-size: 10px;
          padding: 2px 4px;
          border-radius: 2px;
          min-width: 16px;
          text-align: center;
        }

        .thumbnail-delete {
          position: absolute;
          top: 4px;
          right: 4px;
          width: 20px;
          height: 20px;
          background: rgba(255, 77, 79, 0.9);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          opacity: 0;
          transition: all 0.2s ease;
          z-index: 2;

          &:hover {
            background: rgba(255, 77, 79, 1);
            transform: scale(1.1);
          }

          .el-icon {
            color: #ffffff;
            font-size: 12px;
          }
        }
      }

      .empty-thumbnails {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 200px;
        color: #666666;

        .empty-icon {
          font-size: 32px;
          margin-bottom: 8px;
          opacity: 0.5;
        }

        .empty-text {
          font-size: 12px;
          text-align: center;
        }
      }
    }
  }
}

// Element Plus 深色主题覆盖 - 暗光优化（统一灰色风格）
:deep(.el-button) {
  background: #505050 !important; // 中灰色背景（暗光友好）
  border-color: #606060 !important; // 灰色边框
  color: #ffffff !important; // 白色文字
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;

  &:hover {
    background: #5a5a5a !important; // 悬停时稍亮
    border-color: #707070 !important;
    color: #ffffff !important; // 保持白色文字
  }

  &.el-button--primary {
    background: #505050 !important; // 统一灰色背景
    border-color: #606060 !important; // 统一灰色边框
    color: #ffffff !important; // 白色文字

    &:hover {
      background: #5a5a5a !important;
      border-color: #707070 !important;
      color: #ffffff !important;
    }
  }

  &.el-button--success {
    background: #505050 !important; // 统一灰色背景
    border-color: #606060 !important; // 统一灰色边框
    color: #ffffff !important; // 白色文字

    &:hover {
      background: #5a5a5a !important;
      border-color: #707070 !important;
      color: #ffffff !important;
    }
  }

  &.el-button--warning {
    background: #505050 !important; // 统一灰色背景
    border-color: #606060 !important; // 统一灰色边框
    color: #ffffff !important; // 白色文字

    &:hover {
      background: #5a5a5a !important;
      border-color: #707070 !important;
      color: #ffffff !important;
    }
  }

  &.el-button--danger {
    background: #505050 !important; // 统一灰色背景
    border-color: #606060 !important; // 统一灰色边框
    color: #ffffff !important; // 白色文字

    &:hover {
      background: #5a5a5a !important;
      border-color: #707070 !important;
      color: #ffffff !important;
    }
  }

  &.el-button--info {
    background: #505050 !important; // 统一灰色背景
    border-color: #606060 !important; // 统一灰色边框
    color: #ffffff !important; // 白色文字

    &:hover {
      background: #5a5a5a !important;
      border-color: #707070 !important;
      color: #ffffff !important;
    }
  }

  // 禁用状态 - 极暗设计
  &:disabled {
    background: #2a2a2a !important; // 更暗的灰色背景
    border-color: #3a3a3a !important; // 更暗的边框
    color: #808080 !important; // 中灰色文字
    cursor: not-allowed;
  }
}

:deep(.el-card) {
  background: #1a1a1a !important; // 暗灰色背景
  border-color: transparent !important; // 无边框
  color: #d0d0d0 !important; // 柔和浅灰色文字

  .el-card__header {
    background: #0a0a0a !important; // 接近黑色
    border-bottom-color: transparent !important; // 无边框
    color: #e0e0e0 !important; // 柔和文字
  }

  .el-card__body {
    color: #d0d0d0 !important; // 柔和文字
  }
}

:deep(.el-dialog) {
  background: #1a1a1a !important; // 暗灰色背景
  border: none !important; // 无边框

  .el-dialog__header {
    background: #0a0a0a !important; // 接近黑色
    border-bottom: none !important; // 无边框

    .el-dialog__title {
      color: #e0e0e0 !important; // 柔和文字
    }
  }

  .el-dialog__body {
    background: #1a1a1a !important;
    color: #d0d0d0 !important; // 柔和文字
  }

  .el-dialog__footer {
    background: #0a0a0a !important;
    border-top: none !important; // 无边框
  }
}

:deep(.el-input) {
  .el-input__wrapper {
    background: #2a2a2a !important; // 暗灰色背景
    border-color: #3a3a3a !important; // 柔和边框

    .el-input__inner {
      color: #e0e0e0 !important; // 柔和浅灰色文字
      background: transparent !important;

      &::placeholder {
        color: #808080 !important; // 中等灰色占位符
      }
    }

    &:hover {
      border-color: #4a4a4a !important;
    }

    &.is-focus {
      border-color: #4d8fd9 !important; // 柔和蓝色
    }
  }
}

// 下拉选择框样式 - 灰色背景（强制覆盖）
:deep(.el-select) {
  .el-select__wrapper {
    background: #505050 !important; // 中灰色背景
    border-color: #606060 !important; // 灰色边框
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.3) !important; // 内阴影
    transition: all 0.2s ease !important;

    .el-select__input {
      color: #e0e0e0 !important; // 浅灰文字
      font-size: 12px !important;
      font-weight: 500 !important;
      background: transparent !important; // 确保内部背景透明
    }

    .el-select__suffix {
      .el-icon {
        color: #b0b0b0 !important; // 浅灰色图标
      }
    }

    &:hover {
      background: #5a5a5a !important; // 悬停时稍亮
      border-color: #707070 !important;

      .el-select__suffix .el-icon {
        color: #d0d0d0 !important; // 悬停时图标稍亮
      }
    }

    &.is-focus {
      background: #5a5a5a !important;
      border-color: #4d8fd9 !important; // 蓝色焦点
      box-shadow: 0 0 0 1px rgba(77, 143, 217, 0.4) !important;

      .el-select__input {
        color: #f0f0f0 !important; // 焦点时文字更亮
        background: transparent !important;
      }
    }
  }
}

// 强制覆盖所有可能的白色背景
:deep(.el-input__wrapper) {
  background: #505050 !important;
  border-color: #606060 !important;

  .el-input__inner {
    background: transparent !important;
    color: #e0e0e0 !important;
  }
}

// 专门针对 el-select__wrapper 的强制覆盖
:deep(.el-select__wrapper) {
  background: #505050 !important;
  border-color: #606060 !important;

  .el-select__input {
    background: transparent !important;
    color: #e0e0e0 !important;
  }
}

// 全局强制覆盖所有Element Plus下拉框样式
.el-select-dropdown,
.el-popper,
.el-select-dropdown__list,
.el-select-dropdown__item {
  background: #505050 !important;
  color: #909090 !important;
}

// 最强覆盖 - 直接针对设置下拉框
.setting-select {
  .el-select__wrapper {
    background: #505050 !important;
    border-color: #606060 !important;

    .el-select__input {
      background: transparent !important;
      color: #b0b0b0 !important;
    }

    .el-select__suffix .el-icon {
      color: #b0b0b0 !important;
    }
  }
}

// 下拉选项面板 - 极暗优化
:deep(.el-select-dropdown) {
  background: #050505 !important; // 极暗背景（几乎黑色）
  border: 1px solid #1a1a1a !important; // 极暗边框
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.95) !important; // 极深阴影

  .el-scrollbar {
    background: #050505 !important;

    .el-scrollbar__wrap {
      background: #050505 !important;
    }

    .el-scrollbar__bar {
      .el-scrollbar__thumb {
        background: #2a2a2a !important; // 暗灰色滚动条
        border-radius: 4px !important;

        &:hover {
          background: #3a3a3a !important;
        }
      }
    }
  }

  .el-popper__arrow {
    display: none !important; // 隐藏箭头
  }
}

:deep(.el-slider) {
  .el-slider__runway {
    background: #2a2a2a !important; // 暗灰色轨道
  }

  .el-slider__bar {
    background: #4d8fd9 !important; // 柔和蓝色
  }

  .el-slider__button {
    background: #4d8fd9 !important;
    border-color: #4d8fd9 !important;
  }
}

:deep(.el-tooltip__popper) {
  background: #1a1a1a !important; // 暗灰色背景
  border: none !important; // 无边框
  color: #d0d0d0 !important; // 柔和文字

  .el-tooltip__arrow::before {
    background: #1a1a1a !important;
    border-color: transparent !important;
  }
}

:deep(.el-radio-group) {
  .el-radio-button {
    .el-radio-button__inner {
      background: #212121 !important; // 更深的灰色背景（与返回按钮一致）
      border-color: #404040 !important; // 更深的边框
      color: #ffffff !important; // 白色文字

      &:hover {
        color: #ffffff !important; // 保持白色文字
      }
    }

    &.is-active {
      .el-radio-button__inner {
        background: #505050 !important; // 中灰色背景
        border-color: #606060 !important; // 灰色边框
        color: #ffffff !important; // 白色文字
      }
    }
  }
}

// 患者信息工具提示样式
.patient-tooltip {
  div {
    margin-bottom: 4px;
    font-size: 13px;
    line-height: 1.4;
    color: #d0d0d0; // 柔和浅灰色

    &:last-child {
      margin-bottom: 0;
    }

    strong {
      color: #66b1ff; // 柔和蓝色（减少刺眼）
      margin-right: 4px;
    }
  }
}

// 媒体查看器样式
.media-viewer {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000000;
  min-height: 60vh;

  .viewer-image {
    max-width: 100%;
    max-height: 80vh;
    object-fit: contain; // 保持原始比例,不裁剪
    image-rendering: auto; // 使用高质量渲染
  }

  .viewer-video {
    max-width: 100%;
    max-height: 80vh;
    object-fit: contain; // 保持原始比例
  }
}

// 查看器操作按钮样式
.viewer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #0a0a0a; // 接近黑色

  .left-actions,
  .right-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .left-actions {
    flex: 1;

    .el-button {
      &[type="primary"] {
        background: #505050 !important; // 统一灰色背景
        border-color: #606060 !important; // 统一灰色边框
        color: #ffffff !important; // 白色文字

        &:hover:not(:disabled) {
          background: #5a5a5a !important;
          border-color: #707070 !important;
          color: #ffffff !important;
        }

        &:disabled,
        &.is-loading {
          background: #2a2a2a !important; // 更暗的灰色背景
          border-color: #3a3a3a !important; // 更暗的边框
          color: #808080 !important; // 中灰色文字
        }
      }
    }
  }

  .right-actions {
    .el-button {
      min-width: 80px;
    }
  }
}

// 动画
@keyframes pulse {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }
}

// 响应式设计
@include respond-to(lg) {
  .main-content .side-panel {
    width: 250px;
  }
}

@include respond-to(md) {
  .main-content .side-panel {
    display: none;
  }
}
</style>
