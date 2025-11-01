<template>
  <div class="patient-history">
    <a-card class="main-card" :title="pageTitle">
      <template #extra>
        <a-space>
          <a-button @click="goBack">
            <ArrowLeftOutlined />
            返回
          </a-button>
        </a-space>
      </template>

      <div class="content">
        <div class="left">
          <a-input
            v-model:value="keyword"
            placeholder="搜索就诊记录（类型/医生/备注）"
            allow-clear
            @press-enter="filterRecords"
            class="search-input"
          />
          <div class="record-list-container">
            <a-list
              :data-source="filteredRecords"
              :loading="loading"
              item-layout="horizontal"
              class="record-list"
            >
              <template #renderItem="{ item }">
                <a-list-item
                  :class="['record-item', { active: selectedRecord && selectedRecord.id === item.id }]"
                  @click="selectRecord(item)"
                >
                  <a-list-item-meta>
                    <template #title>
                      <div class="item-title">
                        <span class="type">{{ item.examination_type?.type_name || '未知检查' }}</span>
                        <a-tag size="small" :color="getStatusColor(item.status)">{{ getStatusText(item.status) }}</a-tag>
                      </div>
                    </template>
                    <template #description>
                      <div class="item-desc">
                        <span>{{ formatDateTime(item.examination_date, item.examination_time) }}</span>
                        <span v-if="item.doctor">医生：{{ item.doctor?.full_name }}</span>
                      </div>
                    </template>
                  </a-list-item-meta>
                  <template #actions>
                    <a-button 
                      type="text" 
                      danger 
                      size="small"
                      :icon="h(DeleteOutlined)"
                      @click.stop="confirmDeleteRecord(item)"
                      title="删除记录"
                    />
                  </template>
                </a-list-item>
              </template>
              <template #footer>
                <div v-if="loading && currentPage.value > 1" class="loading-more">
                  <a-spin size="small" /> 加载中...
                </div>
                <div v-else-if="hasMore && !loading" class="load-more">
                  <a-button type="link" @click="loadMore">加载更多</a-button>
                </div>
                <div v-else-if="filteredRecords.length > 0" class="no-more">
                  没有更多记录了
                </div>
              </template>
            </a-list>
          </div>
        </div>
        <div class="right" ref="rightPanel">
          <a-empty v-if="!selectedRecord && !loading" description="请选择左侧就诊记录" />
          <a-skeleton v-else-if="loading" active />
          <div v-else class="detail">
            <!-- 快速导航 -->
            <div v-if="selectedRecord?.fundus_images && selectedRecord.fundus_images.length > 0" style="margin-bottom: 16px;">
              <a-alert 
                message="提示" 
                :description="`本次检查包含${selectedRecord.fundus_images.length}张眼底图像，请向下滚动查看`"
                type="info" 
                show-icon
                closable
              >
                <template #action>
                  <a-button size="small" type="primary" @click="scrollToImages">
                    查看眼底图像
                  </a-button>
                </template>
              </a-alert>
            </div>

            <a-descriptions title="就诊详情" bordered size="middle" :column="2">
              <a-descriptions-item label="患者编号">{{ patient?.patient_id }}</a-descriptions-item>
              <a-descriptions-item label="患者姓名">{{ patient?.name }}</a-descriptions-item>
              <a-descriptions-item label="检查编号">{{ selectedRecord?.examination_number }}</a-descriptions-item>
              <a-descriptions-item label="检查类型">{{ selectedRecord?.examination_type?.type_name }}</a-descriptions-item>
              <a-descriptions-item label="主治医生">{{ selectedRecord?.doctor?.full_name || '-' }}</a-descriptions-item>
              <a-descriptions-item label="检查技师">{{ selectedRecord?.technician?.full_name || '-' }}</a-descriptions-item>
              <a-descriptions-item label="检查日期">{{ selectedRecord?.examination_date }}</a-descriptions-item>
              <a-descriptions-item label="检查时间">{{ selectedRecord?.examination_time || '-' }}</a-descriptions-item>
              <a-descriptions-item label="检查眼别">{{ getEyeSideText(selectedRecord?.eye_side) }}</a-descriptions-item>
              <a-descriptions-item label="状态"> 
                <a-tag :color="getStatusColor(selectedRecord?.status)">{{ getStatusText(selectedRecord?.status) }}</a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="主诉" :span="2">{{ selectedRecord?.chief_complaint || '-' }}</a-descriptions-item>
              <a-descriptions-item label="现病史" :span="2">{{ selectedRecord?.present_illness || '-' }}</a-descriptions-item>
              <a-descriptions-item label="检查所见" :span="2">{{ selectedRecord?.examination_findings || '-' }}</a-descriptions-item>
              <a-descriptions-item label="初步诊断" :span="2">{{ selectedRecord?.preliminary_diagnosis || '-' }}</a-descriptions-item>
              <a-descriptions-item label="建议" :span="2">{{ selectedRecord?.recommendations || '-' }}</a-descriptions-item>
              <a-descriptions-item label="随访日期">{{ selectedRecord?.follow_up_date || '-' }}</a-descriptions-item>
              <a-descriptions-item label="备注">{{ selectedRecord?.notes || '-' }}</a-descriptions-item>
            </a-descriptions>

            <a-divider />

            <!-- 诊断记录 -->
            <div v-if="selectedRecord?.diagnosis_records && selectedRecord.diagnosis_records.length > 0">
              <h3 style="margin-bottom: 16px;">诊断记录</h3>
              <a-collapse v-model:activeKey="activeDiagnosisKeys" style="margin-bottom: 16px;">
                <a-collapse-panel 
                  v-for="diagnosis in selectedRecord.diagnosis_records" 
                  :key="diagnosis.id"
                  :header="`${getDiagnosisTypeText(diagnosis.diagnosis_type)} - ${diagnosis.diagnosis_name}`"
                >
                  <a-descriptions bordered size="small" :column="2">
                    <a-descriptions-item label="诊断类型">{{ getDiagnosisTypeText(diagnosis.diagnosis_type) }}</a-descriptions-item>
                    <a-descriptions-item label="诊断名称">{{ diagnosis.diagnosis_name }}</a-descriptions-item>
                    <a-descriptions-item label="ICD编码">{{ diagnosis.icd_code || '-' }}</a-descriptions-item>
                    <a-descriptions-item label="患病侧别">{{ getLateralityText(diagnosis.laterality) }}</a-descriptions-item>
                    <a-descriptions-item label="严重程度">{{ getSeverityText(diagnosis.severity) }}</a-descriptions-item>
                    <a-descriptions-item label="置信度">{{ getConfidenceLevelText(diagnosis.confidence_level) }}</a-descriptions-item>
                    <a-descriptions-item label="诊断日期" :span="2">{{ diagnosis.diagnosis_date || '-' }}</a-descriptions-item>
                    <a-descriptions-item label="诊断描述" :span="2">{{ diagnosis.diagnosis_description || '-' }}</a-descriptions-item>
                    <a-descriptions-item label="支持证据" :span="2">{{ diagnosis.supporting_evidence || '-' }}</a-descriptions-item>
                    <a-descriptions-item label="鉴别诊断" :span="2">{{ diagnosis.differential_diagnoses || '-' }}</a-descriptions-item>
                    <a-descriptions-item label="治疗计划" :span="2">{{ diagnosis.treatment_plan || '-' }}</a-descriptions-item>
                    <a-descriptions-item label="预后" :span="2">{{ diagnosis.prognosis || '-' }}</a-descriptions-item>
                  </a-descriptions>
                </a-collapse-panel>
              </a-collapse>
              <a-divider />
            </div>

            <!-- 眼底图像 -->
            <div v-if="selectedRecord?.fundus_images && selectedRecord.fundus_images.length > 0" class="images-section">
              <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <h3 style="margin: 0; color: #1890ff; font-weight: bold;">
                  📷 眼底图像 ({{ selectedRecord.fundus_images.length }}张)
                </h3>
              </div>
              
              <!-- 使用Image组件的预览组,支持多图切换 -->
              <a-image-preview-group>
                <div class="image-grid">
                  <div 
                    v-for="image in selectedRecord.fundus_images" 
                    :key="image.id" 
                    class="image-item"
                  >
                    <a-card size="small" hoverable>
                      <template #cover>
                        <div class="image-wrapper">
                          <a-image 
                            v-if="image.thumbnail_data && getImageSrc(image.thumbnail_data)" 
                            :src="getImageSrc(image.thumbnail_data)" 
                            :alt="`${getEyeSideText(image.eye_side)}图像`"
                            class="thumbnail-image"
                            :preview="{
                              maskClassName: 'custom-preview-mask'
                            }"
                            :fallback="'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2YwZjBmMCIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIj7mlKDlg4/plJnor688L3RleHQ+PC9zdmc+'"
                          />
                          <div v-else class="no-image">暂无缩略图</div>
                        </div>
                      </template>
                      <a-card-meta>
                        <template #title>
                          <a-space>
                            <a-tag :color="image.eye_side === 'left' ? 'blue' : 'green'">
                              {{ getEyeSideText(image.eye_side) }}
                            </a-tag>
                            <span v-if="image.is_primary" class="primary-badge">
                              <a-tag color="orange" size="small">主图</a-tag>
                            </span>
                          </a-space>
                        </template>
                        <template #description>
                          <div class="image-info">
                            <div v-if="image.image_type">类型: {{ image.image_type }}</div>
                            <div v-if="image.created_at">{{ formatDateTimeShort(image.created_at) }}</div>
                          </div>
                        </template>
                      </a-card-meta>
                      
                      <!-- AI诊断结果 -->
                      <div v-if="image.ai_diagnoses && image.ai_diagnoses.length > 0" class="ai-results">
                        <a-divider style="margin: 8px 0;" />
                        <div class="ai-result" v-for="ai in image.ai_diagnoses" :key="ai.id">
                          <a-tag color="purple" size="small">AI分析</a-tag>
                          <div class="ai-info">
                            <div v-if="ai.diagnosis_result">
                              结果: {{ parseAIResult(ai.diagnosis_result) }}
                            </div>
                            <div v-if="ai.confidence_score">
                              置信度: {{ (ai.confidence_score * 100).toFixed(1) }}%
                            </div>
                            <div v-if="ai.severity_level">
                              严重程度: {{ ai.severity_level }}
                            </div>
                          </div>
                        </div>
                      </div>
                    </a-card>
                  </div>
                </div>
              </a-image-preview-group>
            </div>
            <a-empty v-else description="暂无图像数据" style="margin: 32px 0;" />
          </div>
        </div>
      </div>
    </a-card>
  </div>
  </template>

<script setup>
import { ref, computed, onMounted, h } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message, Modal } from 'ant-design-vue';
import { ArrowLeftOutlined, DeleteOutlined } from '@ant-design/icons-vue';
import examinationAPI from '@/api/examination';
import patientAPI from '@/api/patient';

const route = useRoute();
const router = useRouter();

const patientId = computed(() => route.params.id || route.query.patient_id);
const keyword = ref('');
const loading = ref(false);
const records = ref([]);
const filteredRecords = computed(() => {
  if (!keyword.value) return records.value;
  const k = keyword.value.toLowerCase();
  return records.value.filter(r =>
    (r.examination_type?.type_name || '').toLowerCase().includes(k) ||
    (r.doctor?.name || '').toLowerCase().includes(k) ||
    (r.notes || '').toLowerCase().includes(k)
  );
});
const selectedRecord = ref(null);
const patient = ref(null);
const activeDiagnosisKeys = ref([]);
const rightPanel = ref(null);

const pageTitle = computed(() => patient.value ? `历史病例 - ${patient.value.name}` : '历史病例');

const goBack = () => {
  router.push('/index/patients');
};

const selectRecord = async (item) => {
  // 先显示基本信息，设置加载状态
  selectedRecord.value = { ...item, loading: true };
  
  // 拉取详情，包含图像、AI、诊断记录
  try {
    const res = await examinationAPI.getExamination(item.id);
    if (res.success || (res.code && res.code >= 200 && res.code < 300)) {
      // 更新详细数据
      selectedRecord.value = { ...res.data, loading: false } || { ...item, loading: false };
      
      // 调试:检查图像数据
      if (selectedRecord.value?.fundus_images?.length > 0) {
        console.log('✅ 眼底图像数据加载成功:', selectedRecord.value.fundus_images.map(img => ({
          id: img.id,
          eye_side: img.eye_side,
          has_thumbnail: !!img.thumbnail_data,
          thumbnail_length: img.thumbnail_data?.length || 0,
          thumbnail_preview: img.thumbnail_data?.substring(0, 50)
        })));
        console.log('📷 请向下滚动查看眼底图像区域');
      } else {
        console.log('⚠️ 该检查记录没有眼底图像数据');
      }
    } else {
      message.error(res.message || '获取就诊记录详情失败');
      selectedRecord.value = { ...item, loading: false };
    }
  } catch (e) {
    console.error('获取检查详情失败:', e);
    message.error('获取就诊记录详情失败');
    selectedRecord.value = { ...item, loading: false };
  }
};

const scrollToImages = () => {
  const imagesSection = document.querySelector('.images-section');
  if (imagesSection && rightPanel.value) {
    // 计算图像区域相对于右侧面板的位置
    const imagesSectionTop = imagesSection.offsetTop;
    // 滚动右侧面板
    rightPanel.value.scrollTo({
      top: imagesSectionTop - 20, // 留20px边距
      behavior: 'smooth'
    });
    message.success('已定位到眼底图像区域');
  }
};

const filterRecords = () => {
  // 依赖 computed 即时过滤，无需额外逻辑
};

// 加载更多记录
const loadMore = () => {
  fetchRecords(true);
};

// 滚动加载
const setupScrollListener = () => {
  const recordListContainer = document.querySelector('.record-list-container');
  if (!recordListContainer) return;
  
  const handleScroll = () => {
    const { scrollTop, scrollHeight, clientHeight } = recordListContainer;
    // 当滚动到距离底部100px时，加载更多
    if (scrollHeight - scrollTop - clientHeight < 100 && hasMore.value && !loading.value) {
      loadMore();
    }
  };
  
  recordListContainer.addEventListener('scroll', handleScroll);
  return () => {
    recordListContainer.removeEventListener('scroll', handleScroll);
  };
};

const formatDateTime = (date, time) => {
  if (!date) return '';
  return time ? `${date} ${time}` : date;
};

const getStatusColor = (status) => {
  const map = {
    present: 'blue',
    absent: 'default',
    in_progress: 'orange',
    completed: 'green',
    cancelled: 'red',
    unsigned: 'purple',
    checked_in: 'geekblue',
    confirmed: 'cyan'
  };
  return map[status] || 'default';
};

const getStatusText = (status) => {
  const map = {
    present: '已签到',
    absent: '未签到',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消',
    unsigned: '未签名',
    checked_in: '已到诊',
    confirmed: '已确认'
  };
  return map[status] || status;
};

const getEyeSideText = (side) => {
  const map = {
    left: '左眼',
    right: '右眼',
    both: '双眼',
    bilateral: '双眼'
  };
  return map[side] || side || '-';
};

const getDiagnosisTypeText = (type) => {
  const map = {
    primary: '初步诊断',
    secondary: '次要诊断',
    differential: '鉴别诊断',
    final: '最终诊断'
  };
  return map[type] || type || '-';
};

const getLateralityText = (laterality) => {
  const map = {
    left: '左眼',
    right: '右眼',
    bilateral: '双眼',
    unspecified: '未指定'
  };
  return map[laterality] || laterality || '-';
};

const getSeverityText = (severity) => {
  const map = {
    mild: '轻度',
    moderate: '中度',
    severe: '重度'
  };
  return map[severity] || severity || '-';
};

const getConfidenceLevelText = (level) => {
  const map = {
    high: '高',
    medium: '中',
    low: '低'
  };
  return map[level] || level || '-';
};

const formatDateTimeShort = (datetime) => {
  if (!datetime) return '-';
  try {
    const date = new Date(datetime);
    return date.toLocaleString('zh-CN', { 
      year: 'numeric', 
      month: '2-digit', 
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return datetime;
  }
};

const parseAIResult = (result) => {
  if (!result) return '-';
  try {
    const parsed = typeof result === 'string' ? JSON.parse(result) : result;
    return parsed.diagnosis_name || parsed.result || JSON.stringify(parsed);
  } catch (e) {
    return result;
  }
};

const getImageSrc = (thumbnailData) => {
  if (!thumbnailData) return '';
  
  // 如果已经是完整的data URL,直接返回
  if (thumbnailData.startsWith('data:')) {
    return thumbnailData;
  }
  
  // 清理可能的空格、换行符等
  const cleanData = thumbnailData.replace(/\s/g, '');
  
  // 验证是否是有效的Base64
  try {
    // 简单验证Base64格式
    if (!/^[A-Za-z0-9+/]*={0,2}$/.test(cleanData)) {
      console.warn('Invalid base64 data detected');
      return '';
    }
    return `data:image/jpeg;base64,${cleanData}`;
  } catch (e) {
    console.error('Error processing image data:', e);
    return '';
  }
};

const fetchPatient = async () => {
  try {
    const res = await patientAPI.getPatient(patientId.value);
    if (res.success || (res.code && res.code >= 200 && res.code < 300)) {
      patient.value = res.data;
    }
  } catch (e) {
    console.error(e);
  }
};

const confirmDeleteRecord = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除检查记录 "${record.examination_type?.type_name || '未知检查'}" 吗？此操作不可撤销。`,
    okText: '确认删除',
    cancelText: '取消',
    okType: 'danger',
    onOk: () => deleteRecord(record.id)
  });
};

const deleteRecord = async (recordId) => {
  try {
    const res = await examinationAPI.deleteExamination(recordId);
    if (res.success || (res.code && res.code >= 200 && res.code < 300)) {
      message.success('删除成功');
      // 从列表中移除已删除的记录
      records.value = records.value.filter(r => r.id !== recordId);
      // 如果删除的是当前选中的记录，清空选中状态
      if (selectedRecord.value && selectedRecord.value.id === recordId) {
        selectedRecord.value = records.value[0] || null;
      }
    } else {
      message.error(res.message || '删除失败');
    }
  } catch (err) {
    console.error('删除检查记录失败:', err);
    message.error('删除失败');
  }
};

// 分页参数
const pageSize = ref(15); // 初始加载15条
const currentPage = ref(1);
const hasMore = ref(true);

const fetchRecords = async (loadMore = false) => {
  if (!patientId.value) return;
  if (!loadMore) {
    loading.value = true;
  }
  
  try {
    const res = await examinationAPI.getExaminations({ 
      patientId: patientId.value, 
      pageSize: loadMore ? 10 : pageSize.value, // 初次加载15条，加载更多时每次10条
      page: loadMore ? currentPage.value + 1 : 1, 
      orderBy: 'created_at', // 按创建时间排序
      order: 'desc', 
      include: 'basic' // 只加载基本信息，减少SQL查询负担
    });
    
    if (res.code && res.code >= 200 && res.code < 300) {
      // 兼容分页结构 PaginationResponse { data, total, ... }
      const arr = Array.isArray(res.data?.data) ? res.data.data : (Array.isArray(res.data) ? res.data : []);
      
      if (loadMore) {
        // 加载更多时，追加数据
        if (arr.length > 0) {
          records.value = [...records.value, ...arr];
          currentPage.value++;
        }
        // 如果返回的数据少于请求的数量，说明没有更多数据了
        hasMore.value = arr.length === 10;
      } else {
        // 首次加载
        records.value = arr;
        currentPage.value = 1;
        hasMore.value = arr.length === pageSize.value;
        
        // 不自动选择第一条记录，等待用户点击
        selectedRecord.value = null;
      }
    } else {
      message.error(res.message || '获取就诊记录失败');
    }
  } catch (err) {
    console.error('获取就诊记录失败:', err);
    message.error('获取就诊记录失败');
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await fetchPatient();
  await fetchRecords();
  
  // 设置滚动监听
  const cleanup = setupScrollListener();
  
  // 组件卸载时清理监听器
  onUnmounted(() => {
    if (cleanup) cleanup();
  });
});
</script>

<style scoped>
.patient-history {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.main-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 确保card body可以flex布局 */
.main-card :deep(.ant-card-body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px;
  min-height: 0;
}

.content {
  flex: 1;
  display: flex;
  gap: 16px;
  min-height: 0;
  overflow: hidden;
}

.left {
  width: 360px;
  min-width: 320px;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.search-input {
  margin-bottom: 12px;
}

.record-list-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  max-height: calc(100vh - 200px); /* 确保有固定高度以启用滚动 */
  /* 美化滚动条 */
  scrollbar-width: thin;
  scrollbar-color: #bfbfbf #f0f0f0;
}

.loading-more, .load-more, .no-more {
  text-align: center;
  padding: 10px 0;
  color: #999;
}

.load-more button {
  padding: 0;
}

/* 左侧列表滚动条样式 */
.record-list::-webkit-scrollbar {
  width: 6px;
}

.record-list::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 3px;
}

.record-list::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 3px;
}

.record-list::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}

.record-item {
  cursor: pointer;
  transition: background 0.2s;
}

.record-item:hover {
  background: #fafafa;
}

.record-item.active {
  background: #e6f7ff;
  border-left: 3px solid #1890ff;
}

/* 删除按钮样式 */
.record-item .ant-btn-text {
  opacity: 0;
  transition: opacity 0.2s;
}

.record-item:hover .ant-btn-text {
  opacity: 1;
}

.record-item .ant-btn-text:hover {
  background-color: rgba(255, 77, 79, 0.1);
}

.right {
  flex: 1;
  min-width: 0;
  min-height: 0;
  height: calc(100vh - 180px); /* 动态高度：视口高度减去头部和padding */
  overflow-y: auto;
  overflow-x: hidden;
  /* 美化滚动条 */
  scrollbar-width: thin;
  scrollbar-color: #bfbfbf #f0f0f0;
  position: relative;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
}

/* Webkit浏览器滚动条样式 */
.right::-webkit-scrollbar {
  width: 8px;
}

.right::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 4px;
}

.right::-webkit-scrollbar-thumb {
  background: #1890ff;
  border-radius: 4px;
  min-height: 20px;
}

.right::-webkit-scrollbar-thumb:hover {
  background: #40a9ff;
}

.detail {
  padding: 16px;
  width: 100%;
}

.images-section {
  background: #f0f7ff;
  padding: 16px;
  border-radius: 8px;
  margin: 16px 0;
  border: 2px dashed #1890ff;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.image-item {
  width: 100%;
}

.image-wrapper {
  width: 100%;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  overflow: hidden;
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: #999;
  font-size: 12px;
}

.image-info {
  font-size: 12px;
  color: #666;
}

.ai-results {
  margin-top: 8px;
}

.ai-result {
  font-size: 12px;
}

.ai-info {
  margin-top: 4px;
  color: #666;
}

.ai-info > div {
  margin: 2px 0;
}

@media (max-width: 992px) {
  .content {
    flex-direction: column;
  }
  .left {
    width: 100%;
    max-width: none;
  }
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>

