<template>
  <div class="patient-management" style="height: 100%;">
    <a-card title="" class="main-card" style="height: 100%;">
      <template #extra>
        <a-space>
          <a-button type="primary" @click="showAddModal">
            <UserAddOutlined />
            添加病人
          </a-button>
          <a-button @click="refreshData">
            <ReloadOutlined />
            刷新
          </a-button>
        </a-space>
      </template>
      
      <!-- 患者列表仅保留搜索，不按检查状态分组 -->
      
      <!-- 搜索区域 -->
      <div class="search-area">
        <a-row :gutter="16">
          <a-col :span="6">
            <a-input
              v-model:value="searchForm.name"
              placeholder="请输入病人姓名"
              @press-enter="handleSearch"
            >
              <template #prefix>
                <SearchOutlined />
              </template>
            </a-input>
          </a-col>
          <a-col :span="6">
            <a-input
              v-model:value="searchForm.patientId"
              placeholder="请输入病人ID"
              @press-enter="handleSearch"
            />
          </a-col>
          <a-col :span="12">
            <a-space>
              <a-button type="primary" @click="handleSearch">
                <SearchOutlined />
                搜索
              </a-button>
              <a-button @click="handleReset">
                重置
              </a-button>
            </a-space>
          </a-col>
        </a-row>
      </div>
      
      <!-- 病人列表表格 -->
      <a-table
        :columns="columns"
        :data-source="filteredPatientList"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        :scroll="{ x: 1200, y: 'calc(100vh - 380px)' }"
        size="middle"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'gender'">
            <a-tag :color="record.gender === 'male' ? 'blue' : record.gender === 'female' ? 'pink' : 'default'">
              {{ record.gender === 'male' ? '男' : record.gender === 'female' ? '女' : '其他' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'birth_date'">
            {{ formatDate(record.birth_date) }}
          </template>
          <template v-else-if="column.key === 'status'">
            <a-tag :color="getPatientStatusColor(record.status)">
              {{ getPatientStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space size="small" style="display: flex; justify-content: center;">
              <a-button type="link" size="small" @click="viewPatientDetail(record)" style="padding: 4px 8px;">
                <EyeOutlined />
                查看
              </a-button>
              <a-button type="link" size="small" @click="viewPatientVisits(record)" style="padding: 4px 8px;">
                <CalendarOutlined />
                记录
              </a-button>
              <a-button type="link" size="small" @click="startNewExamination(record)" style="padding: 4px 8px;">
                <ExperimentOutlined />
                新检查
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
    
    <!-- 患者详情抽屉 -->
    <a-drawer
      v-model:open="drawerVisible"
      :title="isEdit ? '编辑患者信息' : '患者详情'"
      width="600"
      placement="right"
      @close="handleDrawerClose"
    >
      <template #extra>
        <a-space>
          <a-button @click="handleDrawerClose">取消</a-button>
          <a-button v-if="!isEdit" type="primary" @click="startEdit">
            编辑
          </a-button>
          <a-button v-if="isEdit" type="primary" @click="savePatient" :loading="submitLoading">
            保存
          </a-button>
        </a-space>
      </template>

      <a-form
        ref="drawerFormRef"
        :model="selectedPatient"
        :rules="formRules"
        layout="vertical"
        :disabled="!isEdit"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="患者编号" name="patient_id">
              <a-input v-model:value="selectedPatient.patient_id" placeholder="请输入患者编号" disabled />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="姓名" name="name">
              <a-input v-model:value="selectedPatient.name" placeholder="请输入患者姓名" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="性别" name="gender">
              <a-select v-model:value="selectedPatient.gender" placeholder="请选择性别">
                <a-select-option value="male">男</a-select-option>
                <a-select-option value="female">女</a-select-option>
                <a-select-option value="other">其他</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="出生日期" name="birth_date">
              <a-date-picker 
                v-model:value="selectedPatient.birth_date" 
                placeholder="请选择出生日期"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="联系电话" name="phone">
              <a-input v-model:value="selectedPatient.phone" placeholder="请输入联系电话" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="邮箱" name="email">
              <a-input v-model:value="selectedPatient.email" placeholder="请输入邮箱地址" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="地址" name="address">
          <a-textarea v-model:value="selectedPatient.address" placeholder="请输入地址" :rows="2" />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="紧急联系人" name="emergency_contact">
              <a-input v-model:value="selectedPatient.emergency_contact" placeholder="请输入紧急联系人" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="紧急联系电话" name="emergency_phone">
              <a-input v-model:value="selectedPatient.emergency_phone" placeholder="请输入紧急联系电话" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="病史" name="medical_history">
          <a-textarea v-model:value="selectedPatient.medical_history" placeholder="请输入病史" :rows="3" />
        </a-form-item>
        <a-form-item label="过敏史" name="allergies">
          <a-textarea v-model:value="selectedPatient.allergies" placeholder="请输入过敏史" :rows="2" />
        </a-form-item>
        <a-form-item label="当前用药" name="current_medications">
          <a-textarea v-model:value="selectedPatient.current_medications" placeholder="请输入当前用药" :rows="2" />
        </a-form-item>
        <a-form-item label="状态" name="status">
          <a-select v-model:value="selectedPatient.status" placeholder="请选择状态">
            <a-select-option value="active">活跃</a-select-option>
            <a-select-option value="inactive">非活跃</a-select-option>
            <a-select-option value="deceased">已故</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-drawer>

    <!-- 添加病人模态框 -->
    <a-modal
      v-model:open="modalVisible"
      title="添加患者"
      width="600px"
      @ok="handleSubmit"
      @cancel="handleCancel"
    >
      <a-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        layout="vertical"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="编号" name="patient_id">
              <a-input v-model:value="formData.patient_id" placeholder="请输入患者编号" :disabled="isEdit" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="姓名" name="name">
              <a-input v-model:value="formData.name" placeholder="请输入患者姓名" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="性别" name="gender">
              <a-select v-model:value="formData.gender" placeholder="请选择性别">
                <a-select-option value="male">男</a-select-option>
                <a-select-option value="female">女</a-select-option>
                <a-select-option value="other">其他</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="出生日期" name="birth_date">
              <a-date-picker 
                v-model:value="formData.birth_date" 
                placeholder="请选择出生日期"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="联系电话" name="phone">
              <a-input v-model:value="formData.phone" placeholder="请输入联系电话" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="邮箱" name="email">
              <a-input v-model:value="formData.email" placeholder="请输入邮箱地址" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="地址" name="address">
          <a-textarea v-model:value="formData.address" placeholder="请输入地址" :rows="2" />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="紧急联系人" name="emergency_contact">
              <a-input v-model:value="formData.emergency_contact" placeholder="请输入紧急联系人" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="紧急联系电话" name="emergency_phone">
              <a-input v-model:value="formData.emergency_phone" placeholder="请输入紧急联系电话" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="病史" name="medical_history">
          <a-textarea v-model:value="formData.medical_history" placeholder="请输入病史" :rows="2" />
        </a-form-item>
        <a-form-item label="过敏史" name="allergies">
          <a-textarea v-model:value="formData.allergies" placeholder="请输入过敏史" :rows="2" />
        </a-form-item>
        <a-form-item label="当前用药" name="current_medications">
          <a-textarea v-model:value="formData.current_medications" placeholder="请输入当前用药" :rows="2" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import { isResponseSuccess, getResponseMessage } from '@/utils/request';
import { patientAPI, examinationAPI } from '@/api';
import { usePatientStore } from '@/store/modules/patient';
import {
  UserAddOutlined,
  ReloadOutlined,
  SearchOutlined,
  EyeOutlined,
  EditOutlined,
  CameraOutlined,
  UserOutlined,
  CalendarOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  ExperimentOutlined
} from '@ant-design/icons-vue';

const router = useRouter();

// 响应式数据
const loading = ref(false);
const modalVisible = ref(false);
const drawerVisible = ref(false);
const isEdit = ref(false);
const submitLoading = ref(false);
const formRef = ref(null);
const drawerFormRef = ref(null);
// 患者列表不再使用按检查状态切换

// 搜索表单
const searchForm = reactive({
  name: '',
  patientId: ''
});

// 表单数据 - 匹配后端Patient模型
const formData = reactive({
  id: null,
  patient_id: '', // 患者编号
  name: '',
  gender: '',
  birth_date: null, // 出生日期
  phone: '',
  email: '',
  address: '',
  emergency_contact: '',
  emergency_phone: '',
  medical_history: '',
  allergies: '',
  current_medications: ''
});

// 表单验证规则
const formRules = {
  patient_id: [
    { required: true, message: '请输入患者编号', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入患者姓名', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  birth_date: [
    { required: true, message: '请选择出生日期', trigger: 'change' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
};

// 患者数据
const allPatients = ref([]);

// 选中的患者数据（用于Drawer显示）
const selectedPatient = reactive({
  id: null,
  patient_id: '',
  name: '',
  gender: '',
  birth_date: null,
  phone: '',
  email: '',
  address: '',
  emergency_contact: '',
  emergency_phone: '',
  medical_history: '',
  allergies: '',
  current_medications: '',
  status: 'active'
});

// 患者列表直接展示全部（按搜索筛选）
const filteredPatientList = computed(() => allPatients.value);

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
  pageSizeOptions: ['10', '20', '50', '100'],
  showLessItems: false
});

// 表格列配置 - 患者列表
const columns = [
  {
    title: '患者编号',
    dataIndex: 'patient_id',
    key: 'patient_id',
    align: 'center',
    width: 120,
    fixed: 'left'
  },
  {
    title: '姓名',
    dataIndex: 'name',
    key: 'name',
    align: 'center',
    width: 100,
    ellipsis: true
  },
  {
    title: '性别',
    dataIndex: 'gender',
    key: 'gender',
    align: 'center',
    width: 70
  },
  {
    title: '出生日期',
    dataIndex: 'birth_date',
    key: 'birth_date',
    align: 'center',
    width: 110
  },
  {
    title: '联系电话',
    dataIndex: 'phone',
    key: 'phone',
    align: 'center',
    width: 120,
    ellipsis: true
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    align: 'center',
    width: 80
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    align: 'center',
    width: 110
  },
  {
    title: '操作',
    key: 'action',
    align: 'center',
    fixed: 'right',
    width: 240
  }
];

// 方法
const showAddModal = () => {
  isEdit.value = false;
  resetForm();
  modalVisible.value = true;
};

const resetForm = () => {
  Object.assign(formData, {
    id: null,
    patient_id: '',
    name: '',
    gender: '',
    birth_date: null, // 字符串格式 YYYY-MM-DD
    phone: '',
    email: '',
    address: '',
    emergency_contact: '',
    emergency_phone: '',
    medical_history: '',
    allergies: '',
    current_medications: ''
  });
};

const handleSearch = () => {
  pagination.current = 1; // 重置到第一页
  fetchPatients();
};

const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    patientId: ''
  });
  fetchPatients();
};

// 获取患者数据
const fetchPatients = async () => {
  if (loading.value) return; // 防止重复调用
  
  loading.value = true;
  try {
    const params = {
      page: pagination.current,
      pageSize: pagination.pageSize
    };
    
    // 添加搜索参数
    if (searchForm.name) {
      params.name = searchForm.name;
    }
    if (searchForm.patientId) {
      params.patient_id = searchForm.patientId;
    }

    const response = await patientAPI.getPatients(params);
    
    if (isResponseSuccess(response)) {
      // 后端返回格式: { code: 200, msg: 'success', data: { patients: [...], pagination: {...} } }
      const responseData = response.data;
      if (responseData && responseData.patients) {
        allPatients.value = responseData.patients;
        
        // 更新分页信息
        if (responseData.pagination) {
          pagination.total = responseData.pagination.total || 0;
          pagination.current = responseData.pagination.page || 1;
          pagination.pageSize = responseData.pagination.page_size || 10;
        }
      } else {
        allPatients.value = [];
        pagination.total = 0;
      }
    } else {
      console.warn('API调用失败', response);
      message.error(getResponseMessage(response) || '获取数据失败');
    }
  } catch (error) {
    console.error('获取患者数据失败:', error);
    message.error('网络连接失败，请检查网络或稍后重试');
  } finally {
    loading.value = false;
  }
};


const refreshData = () => {
  fetchPatients();
};

const handleTableChange = (pag) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  fetchPatients();
};

const viewPatientDetail = (record) => {
  // 复制患者数据到selectedPatient
  Object.assign(selectedPatient, {
    ...record,
    birth_date: record.birth_date ? formatDateForPicker(record.birth_date) : null
  });
  isEdit.value = false;
  drawerVisible.value = true;
};

const startEdit = () => {
  isEdit.value = true;
};

const savePatient = async () => {
  try {
    await drawerFormRef.value.validate();
    submitLoading.value = true;
    
    // 准备更新数据，只发送需要更新的字段（后端只会更新提供的字段）
    const updateData = {
      name: selectedPatient.name,
      gender: selectedPatient.gender,
      birth_date: formatDateForAPI(selectedPatient.birth_date),
      phone: selectedPatient.phone || null,
      email: selectedPatient.email || null,
      address: selectedPatient.address || null,
      emergency_contact: selectedPatient.emergency_contact || null,
      emergency_phone: selectedPatient.emergency_phone || null,
      medical_history: selectedPatient.medical_history || null,
      allergies: selectedPatient.allergies || null,
      current_medications: selectedPatient.current_medications || null,
      status: selectedPatient.status
    };
    
    const response = await patientAPI.updatePatient(selectedPatient.id, updateData);
    if (isResponseSuccess(response)) {
      message.success(getResponseMessage(response) || '患者信息更新成功');
      isEdit.value = false;
      drawerVisible.value = false;
      fetchPatients(); // 刷新列表
    } else {
      message.error(getResponseMessage(response) || '更新失败');
    }
  } catch (error) {
    console.error('保存患者信息失败:', error);
    message.error('保存失败，请稍后重试');
  } finally {
    submitLoading.value = false;
  }
};

const handleDrawerClose = () => {
  drawerVisible.value = false;
  isEdit.value = false;
};

const viewPatientVisits = (record) => {
  router.push({ name: 'patient-history', params: { id: record.id } });
};

// 开始新检查
const startNewExamination = async (record) => {
  try {
    // 获取患者store
    const patientStore = usePatientStore();
    
    // 显示加载状态
    message.loading('正在创建检查记录...', 0);
    
    // 创建检查记录
    const today = new Date();
    // 设置为当天的开始时间，格式为 YYYY-MM-DDTHH:MM:SSZ
    const examinationDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const examinationData = {
      patient_id: record.id,
      examination_type_id: 1, // 默认检查类型ID为1
      eye_side: 'both', // 默认检查眼别：双眼
      examination_date: examinationDate.toISOString(), // 完整的ISO时间格式
      status: 'in_progress' // 直接设置为检查中状态
    };
    
    console.log('创建检查记录:', examinationData);
    
    const response = await examinationAPI.createExamination(examinationData);
    
    // 关闭加载状态
    message.destroy();
    
    if (isResponseSuccess(response)) {
      // 后端返回格式: { code: 200, msg: 'success', data: {...examination_data...} }
      const examination = response.data;
      console.log('检查记录创建成功:', examination);
      
      message.success('检查记录创建成功');
      
      // 准备患者信息
      const patientInfo = {
        id: record.id,
        patient_id: record.patient_id,
        name: record.name,
        gender: record.gender,
        age: record.age
      };

      // 准备检查记录信息
      const examinationInfo = {
        id: examination.id,
        examination_type_id: examination.examination_type_id || 1,
        examination_type: '眼底检查',
        department: '眼科',
        doctor_id: examination.doctor_id || null,
        doctor_name: '',
        scheduled_date: examinationDate.toISOString().split('T')[0],
        scheduled_time: '',
        priority: 'normal',
        notes: examination.notes || '',
        eye_side: examination.eye_side || 'both'
      };

      // 存储到pinia store
      patientStore.setPatientAndExamination(patientInfo, examinationInfo, true);
      patientStore.saveToLocalStorage();
      
      // 跳转到ViewImages页面，携带检查记录ID
      router.push({
        name: 'view-images',
        query: {
          examinationId: examination.id,
          mode: 'new_examination'
        }
      });
    } else {
      message.error(getResponseMessage(response) || '创建检查记录失败');
    }
  } catch (error) {
    message.destroy();
    console.error('创建检查记录失败:', error);
    message.error('创建检查记录失败: ' + (error.message || '未知错误'));
  }
};

// 不再有状态选项卡
const handleTabChange = () => {};

// 获取患者数量
const getPatientCount = () => allPatients.value.length;

// 获取患者状态颜色
const getPatientStatusColor = (status) => {
  const colors = {
    active: 'green',
    inactive: 'orange',
    deceased: 'red'
  };
  return colors[status] || 'default';
};

// 获取患者状态文本
const getPatientStatusText = (status) => {
  const texts = {
    active: '活跃',
    inactive: '非活跃',
    deceased: '已故'
  };
  return texts[status] || status;
};

// 更新分页信息
const updatePagination = () => {
  pagination.total = filteredPatientList.value.length;
};

const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    
    // 准备提交数据，确保日期格式正确
    const submitData = {
      ...formData,
      birth_date: formatDateForAPI(formData.birth_date)
    };
    
    // 添加新患者
    const response = await patientAPI.createPatient(submitData);
    if (isResponseSuccess(response)) {
      message.success(getResponseMessage(response) || '添加成功');
      modalVisible.value = false;
      fetchPatients(); // 刷新数据
    } else {
      message.error(getResponseMessage(response) || '添加失败');
    }
  } catch (error) {
    console.error('操作失败:', error);
    message.error('操作失败，请稍后重试');
  }
};

const handleCancel = () => {
  modalVisible.value = false;
  resetForm();
};

const formatDate = (date) => {
  if (!date) return '-';
  try {
    const d = new Date(date);
    if (isNaN(d.getTime())) return '-';
    return d.toLocaleDateString('zh-CN');
  } catch (error) {
    return '-';
  }
};

// 格式化日期用于日期选择器（YYYY-MM-DD格式）
const formatDateForPicker = (date) => {
  if (!date) return null;
  try {
    const d = new Date(date);
    if (isNaN(d.getTime())) return null;
    return d.toISOString().split('T')[0]; // 返回 YYYY-MM-DD 格式
  } catch (error) {
    return null;
  }
};

// 格式化日期用于API提交（YYYY-MM-DD格式）
const formatDateForAPI = (date) => {
  if (!date) return null;
  try {
    // 如果已经是字符串格式，直接返回
    if (typeof date === 'string') {
      return date;
    }
    // 如果是Date对象，转换为YYYY-MM-DD格式
    const d = new Date(date);
    if (isNaN(d.getTime())) return null;
    return d.toISOString().split('T')[0];
  } catch (error) {
    return null;
  }
};

// 生命周期
onMounted(() => {
  console.log('病人管理组件已加载');
  // 直接从API获取数据
  fetchPatients();
});
</script>

<style scoped>
.patient-management {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.main-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.main-card :deep(.ant-card-body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  min-height: 0; /* 允许flex子元素收缩 */
}

.main-card :deep(.ant-table-wrapper) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0; /* 允许flex子元素收缩 */
}

.main-card :deep(.ant-table) {
  flex: 1;
  min-height: 0; /* 允许表格内容区域收缩 */
}

.main-card :deep(.ant-table-container) {
  flex: 1;
  min-height: 0;
}

.main-card :deep(.ant-table-body) {
  max-height: calc(100vh - 380px); /* 设置最大高度，为分页器底部空间预留更多 */
  overflow-y: auto; /* 内容超出时滚动 */
}

.main-card :deep(.ant-pagination) {
  margin: 16px 0 24px 0; /* 上边距16px，下边距24px */
  flex-shrink: 0; /* 分页器不收缩，始终可见 */
  text-align: center;
}

.status-tabs {
  margin-bottom: 24px;
}

.status-tabs :deep(.ant-tabs-nav) {
  background: #fafafa;
  padding: 8px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.status-tabs :deep(.ant-tabs-tab .anticon) {
  margin-right: 4px;
}

.search-area {
  margin-bottom: 8px; /* 减少底部边距，为分页器预留更多空间 */
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  flex-shrink: 0; /* 搜索区域不收缩 */
}

/* 表格容器样式 */
.main-card :deep(.ant-table-thead) {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #fff;
}

/* 确保表格在小屏幕上的显示 */
@media (max-width: 1400px) {
  .main-card :deep(.ant-table-body) {
    max-height: calc(100vh - 420px);
  }
}

@media (max-width: 1200px) {
  .main-card :deep(.ant-table-body) {
    max-height: calc(100vh - 470px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .patient-management {
    padding: 16px;
  }
  
  .search-area .ant-col {
    margin-bottom: 16px;
  }
}
</style>
