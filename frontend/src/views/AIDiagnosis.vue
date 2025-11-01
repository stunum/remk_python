<template>
  <div class="ai-diagnosis-page">
    <!-- 顶部导航栏 -->
    <div class="diagnosis-header">
      <div class="header-left">
        <el-button icon="ArrowLeft" @click="goBack" type="default">
          返回
        </el-button>
        <div class="page-title">
          <el-icon class="title-icon"><View /></el-icon>
          <span>AI辅助诊断</span>
        </div>
      </div>
      <div class="header-right">
        <el-tag :type="getDiagnosisStatusType(diagnosisStatus)" size="large">
          {{ getDiagnosisStatusText(diagnosisStatus) }}
        </el-tag>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="diagnosis-content">
      <!-- 左侧：患者信息和诊断记录 -->
      <div class="left-panel">
        <!-- 患者基本信息卡片 -->
        <el-card class="patient-info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>患者信息</span>
            </div>
          </template>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">姓名</span>
              <span class="value">{{ patientInfo.patientName || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">患者编号</span>
              <span class="value">{{ patientInfo.patientNumber || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">性别</span>
              <span class="value">{{ getGenderText(patientInfo.gender) }}</span>
            </div>
            <div class="info-item">
              <span class="label">年龄</span>
              <span class="value">{{ patientInfo.age || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">检查类型</span>
              <span class="value">{{ patientInfo.examinationType || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">检查日期</span>
              <span class="value">{{ patientInfo.scheduledDate || '-' }}</span>
            </div>
          </div>
        </el-card>

        <!-- 诊断记录表单 -->
        <el-card class="diagnosis-form-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>诊断记录</span>
              <el-button 
                v-if="diagnosisRecord.id"
                type="danger" 
                size="small"
                @click="deleteDiagnosisRecordConfirm"
                class="delete-btn"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
          <el-form :model="diagnosisRecord" label-width="90px" size="small">
            <el-form-item label="诊断类型">
              <el-select v-model="diagnosisRecord.diagnosis_type" placeholder="请选择">
                <el-option label="初步诊断" value="primary" />
                <el-option label="次要诊断" value="secondary" />
                <el-option label="鉴别诊断" value="differential" />
                <el-option label="最终诊断" value="final" />
              </el-select>
            </el-form-item>
            <el-form-item label="诊断名称">
              <el-input v-model="diagnosisRecord.diagnosis_name" placeholder="请输入诊断名称" />
            </el-form-item>
            <el-form-item label="诊断编码">
              <el-input v-model="diagnosisRecord.diagnosis_code" placeholder="ICD编码(可选)" />
            </el-form-item>
            <el-form-item label="患病侧别">
              <el-select v-model="diagnosisRecord.laterality" placeholder="请选择">
                <el-option label="左眼" value="left" />
                <el-option label="右眼" value="right" />
                <el-option label="双眼" value="bilateral" />
                <el-option label="未指定" value="unspecified" />
              </el-select>
            </el-form-item>
            <el-form-item label="严重程度">
              <el-select v-model="diagnosisRecord.severity" placeholder="请选择">
                <el-option label="轻度" value="mild" />
                <el-option label="中度" value="moderate" />
                <el-option label="重度" value="severe" />
              </el-select>
            </el-form-item>
            <el-form-item label="临床发现">
              <el-input 
                v-model="diagnosisRecord.clinical_findings" 
                type="textarea"
                :rows="2"
                placeholder="请输入临床发现"
              />
            </el-form-item>
            <el-form-item label="诊断描述">
              <el-input 
                v-model="diagnosisRecord.diagnosis_description" 
                type="textarea"
                :rows="3"
                placeholder="请输入诊断描述"
              />
            </el-form-item>
            <el-form-item label="治疗建议">
              <el-input 
                v-model="diagnosisRecord.treatment_recommended" 
                type="textarea"
                :rows="2"
                placeholder="请输入治疗建议"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveDiagnosis" :loading="savingDiagnosis">
                <el-icon><Select /></el-icon>
                {{ diagnosisRecord.id ? '更新诊断' : '保存诊断' }}
              </el-button>
              <el-button @click="resetDiagnosisForm">
                <el-icon><RefreshLeft /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- 右侧：AI诊断结果 -->
      <div class="right-panel">
        <!-- AI诊断图像列表 -->
        <el-card class="ai-diagnosis-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Picture /></el-icon>
              <span>AI诊断结果</span>
              <el-button 
                type="success" 
                size="small"
                :loading="isAnalyzing"
                @click="startBatchAnalysis"
                class="analyze-btn"
              >
                <el-icon><View /></el-icon>
                {{ isAnalyzing ? '分析中...' : '批量分析' }}
              </el-button>
            </div>
          </template>
          
          <div class="diagnosis-images-list">
            <div 
              v-for="(item, index) in aiDiagnosisList" 
              :key="item.id"
              class="diagnosis-image-item"
              :class="{ analyzing: item.analyzing }"
            >
              <!-- 图像预览 -->
              <div class="image-preview" @click="viewFullImage(item)">
                <img :src="item.thumbnail_data || item.image_url" :alt="`图像 ${index + 1}`" />
                <div class="image-overlay">
                  <el-icon class="view-icon"><ZoomIn /></el-icon>
                </div>
                <div class="image-badge" :class="item.eye_side">
                  {{ item.eye_side === 'left' ? '左眼' : '右眼' }}
                </div>
              </div>

              <!-- AI分析结果 -->
              <div class="analysis-result">
                <!-- 加载状态 -->
                <div v-if="item.analyzing" class="analyzing-state">
                  <el-icon class="loading-icon"><Loading /></el-icon>
                  <span>AI分析中...</span>
                </div>

                <!-- 分析完成 -->
                <div v-else-if="item.ai_diagnosis" class="result-content">
                  <!-- 诊断标题 -->
                  <div class="result-header">
                    <div class="diagnosis-title">
                      {{ item.ai_diagnosis.diagnosis_name || '正常' }}
                    </div>
                    <el-progress 
                      :percentage="Math.round(item.ai_diagnosis.confidence_score * 100)"
                      :color="getConfidenceColor(item.ai_diagnosis.confidence_score)"
                      :stroke-width="6"
                    />
                  </div>

                  <!-- 严重程度 -->
                  <div class="severity-level" v-if="item.ai_diagnosis.severity_level">
                    <span class="label">严重程度:</span>
                    <el-tag 
                      :type="getSeverityColorByLevel(item.ai_diagnosis.severity_level)"
                      size="small"
                    >
                      {{ getSeverityLevelText(item.ai_diagnosis.severity_level) }}
                    </el-tag>
                  </div>

                  <!-- 风险评估 -->
                  <div class="risk-assessment" v-if="item.ai_diagnosis.risk_assessment">
                    <div class="section-title">风险评估</div>
                    <div class="risk-text">{{ item.ai_diagnosis.risk_assessment }}</div>
                  </div>

                  <!-- 建议措施 -->
                  <div class="recommended-actions" v-if="item.ai_diagnosis.recommended_actions">
                    <div class="section-title">建议措施</div>
                    <div class="actions-text">{{ item.ai_diagnosis.recommended_actions }}</div>
                  </div>

                  <!-- 操作按钮 -->
                  <div class="result-actions">
                    <el-button size="small" @click="viewDetailedReport(item)">
                      <el-icon><Document /></el-icon>
                      详细报告
                    </el-button>
                    <el-button size="small" type="primary" @click="reanalyze(item)">
                      <el-icon><Refresh /></el-icon>
                      重新分析
                    </el-button>
                  </div>
                </div>

                <!-- 未分析 -->
                <div v-else class="not-analyzed">
                  <el-icon class="info-icon"><InfoFilled /></el-icon>
                  <span>暂未进行AI分析</span>
                  <el-button size="small" type="primary" @click="analyzeImage(item)">
                    立即分析
                  </el-button>
                </div>
              </div>
            </div>

            <el-empty v-if="aiDiagnosisList.length === 0" description="暂无图像数据">
              <el-button type="primary" @click="goBack">返回拍摄</el-button>
            </el-empty>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 图片查看器 -->
    <el-dialog
      v-model="showImageViewer"
      width="80%"
      top="5vh"
    >
      <img :src="viewerImageUrl" class="full-image" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { message, Modal } from 'ant-design-vue';
import { 
  ArrowLeft, View, User, Document, Picture, Delete, 
  ZoomIn, Loading, InfoFilled, Refresh, Select, RefreshLeft 
} from '@element-plus/icons-vue';
import { isResponseSuccess, getResponseMessage } from '@/utils/request';
import * as diagnosisAPI from '@/api/diagnosis';

const router = useRouter();
const route = useRoute();

// 患者信息
const patientInfo = reactive({
  registrationId: null,
  examinationId: null, // 检查记录ID（用于获取AI诊断列表）
  patientName: '',
  patientNumber: '',
  gender: '',
  age: null,
  examinationType: '',
  scheduledDate: '',
  // ... 其他字段
});

// 诊断状态
const diagnosisStatus = ref('in_progress'); // pending, in_progress, completed

// 诊断记录 (一对一关系)
const diagnosisRecord = reactive({
  id: null,
  examination_id: null,
  diagnosis_type: 'primary',
  diagnosis_code: '',
  diagnosis_name: '',
  diagnosis_description: '',
  laterality: '',
  severity: '',
  clinical_findings: '',
  treatment_recommended: '',
  diagnosed_by: null,
  doctor_name: '',
});

const savingDiagnosis = ref(false);

// AI诊断列表
const aiDiagnosisList = ref([]);
const isAnalyzing = ref(false);

// 对话框状态
const showImageViewer = ref(false);
const viewerImageUrl = ref('');

// 返回
const goBack = () => {
  router.go(-1);
};

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 获取性别文本
const getGenderText = (gender) => {
  const map = { male: '男', female: '女', other: '其他' };
  return map[gender] || '-';
};

// 获取诊断状态类型
const getDiagnosisStatusType = (status) => {
  const map = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success'
  };
  return map[status] || 'info';
};

// 获取诊断状态文本
const getDiagnosisStatusText = (status) => {
  const map = {
    pending: '待诊断',
    in_progress: '诊断中',
    completed: '已完成'
  };
  return map[status] || '未知';
};

// 获取诊断类型颜色
const getDiagnosisTypeColor = (type) => {
  const map = {
    primary: 'primary',
    secondary: 'success',
    differential: 'warning',
    final: 'danger'
  };
  return map[type] || '';
};

// 获取诊断类型文本
const getDiagnosisTypeText = (type) => {
  const map = {
    primary: '初步诊断',
    secondary: '次要诊断',
    differential: '鉴别诊断',
    final: '最终诊断'
  };
  return map[type] || type;
};

// 获取侧别文本
const getLateralityText = (laterality) => {
  const map = {
    left: '左眼',
    right: '右眼',
    bilateral: '双眼',
    unspecified: '未指定'
  };
  return map[laterality] || laterality;
};

// 获取严重程度颜色
const getSeverityColor = (severity) => {
  const map = {
    mild: 'success',
    moderate: 'warning',
    severe: 'danger'
  };
  return map[severity] || '';
};

// 获取严重程度文本
const getSeverityText = (severity) => {
  const map = {
    mild: '轻度',
    moderate: '中度',
    severe: '重度'
  };
  return map[severity] || severity;
};

// 获取严重程度级别颜色
const getSeverityColorByLevel = (level) => {
  const map = {
    normal: 'success',
    mild: 'info',
    moderate: 'warning',
    severe: 'danger',
    critical: 'danger'
  };
  return map[level] || '';
};

// 获取严重程度级别文本
const getSeverityLevelText = (level) => {
  const map = {
    normal: '正常',
    mild: '轻度',
    moderate: '中度',
    severe: '重度',
    critical: '危重'
  };
  return map[level] || level;
};

// 获取置信度颜色
const getConfidenceColor = (score) => {
  if (score >= 0.9) return '#67c23a';
  if (score >= 0.7) return '#e6a23c';
  return '#f56c6c';
};

// 保存诊断记录
const saveDiagnosis = async () => {
  if (!diagnosisRecord.diagnosis_name) {
    message.warning('请输入诊断名称');
    return;
  }

  try {
    savingDiagnosis.value = true;

    const data = {
      examination_id: patientInfo.examinationId,
      diagnosis_type: diagnosisRecord.diagnosis_type,
      diagnosis_code: diagnosisRecord.diagnosis_code,
      diagnosis_name: diagnosisRecord.diagnosis_name,
      diagnosis_description: diagnosisRecord.diagnosis_description,
      laterality: diagnosisRecord.laterality,
      severity: diagnosisRecord.severity,
      clinical_findings: diagnosisRecord.clinical_findings,
      treatment_recommended: diagnosisRecord.treatment_recommended,
    };

    const response = await diagnosisAPI.saveDiagnosisRecord(data);

    if (isResponseSuccess(response)) {
      message.success(getResponseMessage(response) || '诊断记录保存成功');
      // 重新加载诊断记录
      await loadDiagnosisRecord();
    } else {
      message.error(getResponseMessage(response) || '保存失败');
    }
  } catch (error) {
    console.error('保存诊断记录失败:', error);
    message.error('保存失败: ' + (error.message || '未知错误'));
  } finally {
    savingDiagnosis.value = false;
  }
};

// 删除诊断记录确认
const deleteDiagnosisRecordConfirm = async () => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这条诊断记录吗？',
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        const response = await diagnosisAPI.deleteDiagnosisRecord(diagnosisRecord.id);
        
        if (isResponseSuccess(response)) {
          message.success(getResponseMessage(response) || '删除成功');
          // 重置表单
          resetDiagnosisForm();
        } else {
          message.error(getResponseMessage(response) || '删除失败');
        }
      } catch (error) {
        console.error('删除诊断记录失败:', error);
        message.error('删除失败: ' + (error.message || '未知错误'));
      }
    }
  });
};

// 重置诊断表单
const resetDiagnosisForm = () => {
  diagnosisRecord.id = null;
  diagnosisRecord.diagnosis_type = 'primary';
  diagnosisRecord.diagnosis_code = '';
  diagnosisRecord.diagnosis_name = '';
  diagnosisRecord.diagnosis_description = '';
  diagnosisRecord.laterality = '';
  diagnosisRecord.severity = '';
  diagnosisRecord.clinical_findings = '';
  diagnosisRecord.treatment_recommended = '';
  diagnosisRecord.diagnosed_by = null;
  diagnosisRecord.doctor_name = '';
};

// 批量分析
const startBatchAnalysis = async () => {
  isAnalyzing.value = true;
  for (const item of aiDiagnosisList.value) {
    if (!item.ai_diagnosis) {
      await analyzeImage(item);
    }
  }
  isAnalyzing.value = false;
  message.success('批量分析完成');
};

// 分析单张图像
const analyzeImage = async (item) => {
  item.analyzing = true;
  console.log('开始AI分析:', item);
  
  try {
    const response = await diagnosisAPI.performAIDiagnosis({
      image_id: item.image_id
    });
    
    if (isResponseSuccess(response)) {
      // 更新AI诊断结果
      item.ai_diagnosis = {
        diagnosis_name: response.data.diagnosis_name,
        confidence_score: response.data.confidence_score,
        severity_level: response.data.severity_level,
        risk_assessment: response.data.risk_assessment,
        recommended_actions: response.data.recommended_actions
      };
      message.success('AI分析完成');
    } else {
      message.error(getResponseMessage(response) || 'AI分析失败');
    }
  } catch (error) {
    console.error('AI分析失败:', error);
    message.error('AI分析失败: ' + (error.message || '未知错误'));
  } finally {
    item.analyzing = false;
  }
};

// 重新分析
const reanalyze = async (item) => {
  item.ai_diagnosis = null;
  await analyzeImage(item);
};

// 查看完整图片
const viewFullImage = (item) => {
  viewerImageUrl.value = item.thumbnail_data || item.image_url;
  showImageViewer.value = true;
};

// 查看详细报告
const viewDetailedReport = (item) => {
  console.log('查看详细报告:', item);
  message.info('详细报告功能开发中...');
};

// 加载诊断记录(单条)
const loadDiagnosisRecord = async () => {
  if (!patientInfo.examinationId) {
    console.warn('没有examination_id,跳过加载诊断记录');
    return;
  }

  try {
    console.log('加载诊断记录,examination_id:', patientInfo.examinationId);
    
    const response = await diagnosisAPI.getDiagnosisRecord(patientInfo.examinationId);
    
    if (isResponseSuccess(response) && response.data) {
      // 加载到表单
      Object.assign(diagnosisRecord, {
        id: response.data.id,
        examination_id: response.data.examination_id,
        diagnosis_type: response.data.diagnosis_type || 'primary',
        diagnosis_code: response.data.diagnosis_code || '',
        diagnosis_name: response.data.diagnosis_name || '',
        diagnosis_description: response.data.diagnosis_description || '',
        laterality: response.data.laterality || '',
        severity: response.data.severity || '',
        clinical_findings: response.data.clinical_findings || '',
        treatment_recommended: response.data.treatment_recommended || '',
        diagnosed_by: response.data.diagnosed_by,
        doctor_name: response.data.doctor_name || '',
      });
      console.log('诊断记录加载成功:', diagnosisRecord);
    } else {
      console.log('暂无诊断记录');
      // 初始化examination_id
      diagnosisRecord.examination_id = patientInfo.registrationId;
    }
  } catch (error) {
    console.error('加载诊断记录失败:', error);
  }
};

// 加载AI诊断数据
const loadAIDiagnosisData = async () => {
  if (!patientInfo.examinationId) {
    console.warn('没有examination_id,跳过加载AI诊断数据');
    return;
  }

  try {
    console.log('加载AI诊断数据,examination_id:', patientInfo.examinationId);
    
    const response = await diagnosisAPI.getAIDiagnoses(patientInfo.examinationId);
    
    if (isResponseSuccess(response)) {
      const diagnoses = response.data || [];
      console.log(`加载了 ${diagnoses.length} 条AI诊断记录`);
      
      // 转换为前端格式
      aiDiagnosisList.value = diagnoses.map(item => ({
        id: item.id,
        image_id: item.image_id,
        eye_side: item.eye_side,
        thumbnail_data: item.thumbnail_data,
        file_path: item.file_path,
        analyzing: false,
        ai_diagnosis: item.ai_model_name ? {
          diagnosis_name: item.diagnosis_result ? JSON.parse(item.diagnosis_result).diagnosis_name : '未知',
          confidence_score: item.confidence_score,
          severity_level: item.severity_level,
          risk_assessment: item.risk_assessment,
          recommended_actions: item.recommended_actions
        } : null
      }));
    } else {
      console.warn('加载AI诊断数据失败:', getResponseMessage(response));
    }
  } catch (error) {
    console.error('加载AI诊断数据失败:', error);
  }
};

// 页面加载
onMounted(async () => {
  // 从路由参数获取患者信息
  if (route.query.patientData) {
    try {
      const data = JSON.parse(route.query.patientData);
      Object.assign(patientInfo, data);
      console.log('✅ 接收到患者信息:', patientInfo);
    } catch (error) {
      console.error('解析患者信息失败:', error);
    }
  } else {
    // 如果没有 patientData，从单独的查询参数获取
    Object.assign(patientInfo, {
      registrationId: route.query.registrationId,
      examinationId: route.query.examinationId, // 检查记录ID
      patientName: route.query.patientName,
      patientNumber: route.query.patientNumber,
      // ... 其他字段可以根据需要添加
    });
    console.log('✅ 从查询参数获取患者信息');
  }
  
  console.log('📋 关键ID信息:', {
    registrationId: patientInfo.registrationId,
    examinationId: patientInfo.examinationId
  });
  
  // 加载数据
  await loadDiagnosisRecord(); // 加载诊断记录(一对一)
  await loadAIDiagnosisData(); // 加载AI诊断数据
});
</script>

<style lang="scss" scoped>
.ai-diagnosis-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
  overflow: hidden;
}

// 顶部导航
.diagnosis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .page-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 20px;
      font-weight: 600;
      color: #303133;
      
      .title-icon {
        font-size: 24px;
        color: #409eff;
      }
    }
  }
}

// 主要内容
.diagnosis-content {
  flex: 1;
  display: flex;
  gap: 16px;
  padding: 16px;
  overflow: hidden;
}

// 左侧面板
.left-panel {
  width: 380px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  
  .patient-info-card {
    flex-shrink: 0;
    
    .info-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      
      .info-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
        
        .label {
          font-size: 12px;
          color: #909399;
        }
        
        .value {
          font-size: 14px;
          color: #303133;
          font-weight: 500;
        }
      }
    }
  }
  
  .diagnosis-form-card {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    
    :deep(.el-card__body) {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
    }
    
    .el-form {
      .el-form-item {
        margin-bottom: 12px;
        
        :deep(.el-select),
        :deep(.el-input) {
          width: 100%;
        }
      }
    }
    
    .delete-btn {
      margin-left: auto;
    }
  }
}

// 右侧面板
.right-panel {
  flex: 1;
  overflow: hidden;
  
  .ai-diagnosis-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    
    :deep(.el-card__body) {
      flex: 1;
      overflow: hidden;
      padding: 0;
    }
    
    .diagnosis-images-list {
      height: 100%;
      overflow-y: auto;
      padding: 16px;
      
      .diagnosis-image-item {
        display: flex;
        gap: 16px;
        padding: 16px;
        margin-bottom: 16px;
        background: #ffffff;
        border: 1px solid #e4e7ed;
        border-radius: 8px;
        transition: all 0.3s;
        
        &:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        &.analyzing {
          border-color: #409eff;
        }
        
        .image-preview {
          position: relative;
          width: 200px;
          height: 200px;
          flex-shrink: 0;
          border-radius: 6px;
          overflow: hidden;
          cursor: pointer;
          
          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }
          
          .image-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s;
            
            .view-icon {
              font-size: 32px;
              color: #ffffff;
            }
          }
          
          &:hover .image-overlay {
            opacity: 1;
          }
          
          .image-badge {
            position: absolute;
            top: 8px;
            left: 8px;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            color: #ffffff;
            
            &.left {
              background: rgba(64, 158, 255, 0.9);
            }
            
            &.right {
              background: rgba(250, 140, 22, 0.9);
            }
          }
        }
        
        .analysis-result {
          flex: 1;
          display: flex;
          flex-direction: column;
          
          .analyzing-state {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 40px 0;
            
            .loading-icon {
              font-size: 24px;
              color: #409eff;
              animation: rotate 1s linear infinite;
            }
            
            span {
              font-size: 14px;
              color: #606266;
            }
          }
          
          .result-content {
            .result-header {
              margin-bottom: 16px;
              
              .diagnosis-title {
                font-size: 18px;
                font-weight: 600;
                color: #303133;
                margin-bottom: 12px;
              }
            }
            
            .severity-level {
              display: flex;
              align-items: center;
              gap: 8px;
              margin-bottom: 12px;
              
              .label {
                font-size: 13px;
                color: #606266;
              }
            }
            
            .risk-assessment,
            .recommended-actions {
              margin-bottom: 12px;
              
              .section-title {
                font-size: 13px;
                font-weight: 600;
                color: #606266;
                margin-bottom: 6px;
              }
              
              .risk-text,
              .actions-text {
                font-size: 13px;
                color: #606266;
                line-height: 1.6;
                padding: 8px 12px;
                background: #f5f7fa;
                border-radius: 4px;
              }
            }
            
            .result-actions {
              display: flex;
              gap: 8px;
              margin-top: auto;
              padding-top: 12px;
            }
          }
          
          .not-analyzed {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 40px 0;
            
            .info-icon {
              font-size: 32px;
              color: #909399;
            }
            
            span {
              font-size: 14px;
              color: #606266;
            }
          }
        }
      }
    }
  }
}

// 卡片头部
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  
  .el-icon {
    font-size: 18px;
    color: #409eff;
  }
  
  .add-btn,
  .analyze-btn {
    margin-left: auto;
  }
}

// 完整图片查看
.full-image {
  width: 100%;
  height: auto;
  display: block;
}

// 动画
@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

