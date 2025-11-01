<template>
  <div class="visit-management" style="height: 100%">
    <a-card title="" class="main-card" style="height: 100%">
      <template #extra>
        <a-space>
          <a-button type="primary" @click="showRegistrationModal">
            <PlusOutlined />
            预约挂号
          </a-button>
          <a-button @click="refreshData">
            <ReloadOutlined />
            刷新
          </a-button>
        </a-space>
      </template>

      <!-- 预约挂号弹窗 -->
      <a-modal
        v-model:visible="registrationModalVisible"
        title="预约挂号"
        width="850px"
        :footer="null"
        @cancel="handleRegistrationCancel"
        class="registration-modal"
        :maskClosable="false"
      >
        <a-form
          :model="registrationForm"
          :rules="registrationRules"
          ref="registrationFormRef"
          layout="vertical"
          class="registration-form"
        >
          <!-- 患者信息区域 -->
          <a-card class="form-section" :bordered="false">
            <template #title>
              <div class="section-title"><UserOutlined /> 患者信息</div>
            </template>

            <a-row :gutter="24">
              <a-col :span="16">
                <a-form-item label="患者编号" name="patient_id_input">
                  <a-input-search
                    v-model:value="patientIdInput"
                    placeholder="请输入患者编号"
                    enter-button="查询"
                    @search="searchPatientById"
                    size="large"
                  />
                </a-form-item>
              </a-col>
              <!-- <a-col :span="8">
                <a-form-item>
                  <a-button type="primary" ghost @click="showNewPatientForm" size="large" style="width: 100%">
                    <PlusOutlined /> 新增患者
                  </a-button>
                </a-form-item>
              </a-col> -->
            </a-row>

            <!-- 患者信息展示 -->
            <a-row v-if="selectedPatient" :gutter="24" class="patient-info">
              <a-col :span="24">
                <a-alert
                  :message="'患者信息'"
                  :description="patientInfoText"
                  type="info"
                  show-icon
                  class="patient-info-alert"
                />
              </a-col>
            </a-row>

            <!-- 患者不存在提示 -->
            <a-row v-if="patientNotFound" :gutter="24">
              <a-col :span="24">
                <a-alert
                  message="患者不存在"
                  description="该患者编号不存在，请先进行患者建档"
                  type="warning"
                  show-icon
                />
              </a-col>
            </a-row>
          </a-card>

          <!-- 预约信息区域 -->
          <a-card class="form-section" :bordered="false">
            <template #title>
              <div class="section-title"><CalendarOutlined /> 预约信息</div>
            </template>

            <a-row :gutter="24">
              <a-col :xs="24" :sm="12">
                <a-form-item
                  label="检查类型"
                  name="examination_type_id"
                  required
                >
                  <a-select
                    v-model:value="registrationForm.examination_type_id"
                    placeholder="请选择检查类型"
                    size="large"
                    class="custom-select"
                  >
                    <a-select-option
                      v-for="type in examinationTypes"
                      :key="type.id"
                      :value="type.id"
                    >
                      {{ type.type_name }}
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="12">
                <a-form-item label="科室" name="department" required>
                  <a-select
                    v-model:value="registrationForm.department"
                    placeholder="请选择科室"
                    size="large"
                    class="custom-select"
                  >
                    <a-select-option value="眼科">眼科</a-select-option>
                    <a-select-option value="内科">内科</a-select-option>
                    <a-select-option value="外科">外科</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="24">
              <a-col :xs="24" :sm="12">
                <a-form-item label="医生" name="doctor_id" required>
                  <a-select
                    v-model:value="registrationForm.doctor_id"
                    placeholder="请选择医生"
                    size="large"
                    class="custom-select"
                  >
                    <a-select-option
                      v-for="doctor in doctorList"
                      :key="doctor.id"
                      :value="doctor.id"
                    >
                      {{ doctor.full_name }}
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="12">
                <a-form-item label="检查技师" name="technician_id">
                  <a-select
                    v-model:value="registrationForm.technician_id"
                    placeholder="请选择检查技师"
                    size="large"
                    class="custom-select"
                    allow-clear
                  >
                    <a-select-option
                      v-for="technician in technicianList"
                      :key="technician.id"
                      :value="technician.id"
                    >
                      {{ technician.full_name }}
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="24">
              <a-col :xs="24" :sm="12">
                <a-form-item label="检查眼别" name="eye_side">
                  <a-select
                    v-model:value="registrationForm.eye_side"
                    placeholder="请选择检查眼别"
                    size="large"
                    class="custom-select"
                    allow-clear
                  >
                    <a-select-option value="left">左眼</a-select-option>
                    <a-select-option value="right">右眼</a-select-option>
                    <a-select-option value="both">双眼</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="12">
                <a-form-item label="挂号类型" name="registration_type" required>
                  <a-select
                    v-model:value="registrationForm.registration_type"
                    placeholder="请选择挂号类型"
                    size="large"
                    class="custom-select"
                  >
                    <a-select-option value="normal">普通</a-select-option>
                    <a-select-option value="appointment">预约</a-select-option>
                    <a-select-option value="emergency">急诊</a-select-option>
                    <a-select-option value="followup">复诊</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="24">
              <a-col :xs="24" :sm="12">
                <a-form-item label="预约日期" name="scheduled_date" required>
                  <a-date-picker
                    v-model:value="registrationForm.scheduled_date"
                    style="width: 100%"
                    placeholder="请选择预约日期"
                    size="large"
                    class="custom-date-picker"
                    :disabledDate="disabledDate"
                  />
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="12">
                <a-form-item label="预约时间" name="scheduled_time" required>
                  <a-time-picker
                    v-model:value="registrationForm.scheduled_time"
                    format="HH:mm"
                    style="width: 100%"
                    placeholder="请选择预约时间"
                    size="large"
                    class="custom-time-picker"
                    :minute-step="5"
                    :hour-step="1"
                  />
                </a-form-item>
              </a-col>
            </a-row>

            <a-row :gutter="24">
              <a-col :xs="24" :sm="12">
                <a-form-item label="优先级" name="priority">
                  <a-select
                    v-model:value="registrationForm.priority"
                    placeholder="请选择优先级"
                    size="large"
                    class="custom-select"
                  >
                    <a-select-option value="normal">普通</a-select-option>
                    <a-select-option value="low">低</a-select-option>
                    <a-select-option value="high">高</a-select-option>
                    <a-select-option value="urgent">紧急</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :xs="24" :sm="12">
                <a-form-item label="缴费状态" name="payment_status">
                  <a-select
                    v-model:value="registrationForm.payment_status"
                    placeholder="请选择缴费状态"
                    size="large"
                    class="custom-select"
                  >
                    <a-select-option value="unpaid">未缴费</a-select-option>
                    <a-select-option value="paid">已缴费</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>
          </a-card>

          <!-- 备注信息区域 -->
          <a-card class="form-section" :bordered="false">
            <template #title>
              <div class="section-title"><FileTextOutlined /> 备注信息</div>
            </template>

            <a-form-item label="主诉" name="chief_complaint">
              <a-textarea
                v-model:value="registrationForm.chief_complaint"
                placeholder="请输入主诉"
                :rows="2"
                class="custom-textarea"
              />
            </a-form-item>

            <a-form-item label="备注" name="notes">
              <a-textarea
                v-model:value="registrationForm.notes"
                placeholder="请输入备注"
                :rows="2"
                class="custom-textarea"
              />
            </a-form-item>
          </a-card>

          <!-- 操作按钮 -->
          <div
            class="form-actions"
            style="width: 100%; display: flex; justify-content: space-between"
          >
            <a-button
              type="primary"
              size="large"
              @click="submitRegistration"
              class="submit-btn"
            >
              <CheckOutlined /> 提交预约
            </a-button>
            <a-button
              size="large"
              @click="handleRegistrationCancel"
              class="cancel-btn"
            >
              <CloseOutlined /> 取消
            </a-button>
          </div>
        </a-form>
      </a-modal>

      <!-- 状态选项卡 -->
      <a-tabs
        v-model:activeKey="activeTab"
        @change="handleTabChange"
        class="status-tabs"
      >
        <a-tab-pane key="queue" tab="排队叫号">
          <template #tab>
            <span>
              <BellOutlined />
              排队叫号 ({{ getTabCount("queue") }})
            </span>
          </template>
        </a-tab-pane>
        <a-tab-pane key="in_progress" tab="进行中">
          <template #tab>
            <span>
              <PlayCircleOutlined />
              进行中 ({{ getTabCount("in_progress") }})
            </span>
          </template>
        </a-tab-pane>
        <a-tab-pane key="completed" tab="已完成">
          <template #tab>
            <span>
              <CheckCircleOutlined />
              已完成 ({{ getTabCount("completed") }})
            </span>
          </template>
        </a-tab-pane>
        <a-tab-pane key="all" tab="全部">
          <template #tab>
            <span>
              <UserOutlined />
              全部 ({{ getTabCount("all") }})
            </span>
          </template>
        </a-tab-pane>
      </a-tabs>

      <!-- 搜索区域 -->
      <div class="search-area">
        <a-row :gutter="16">
          <a-col :span="8">
            <a-input
              v-model:value="searchForm.keyword"
              placeholder="姓名/患者编号"
              @press-enter="handleSearch"
            >
              <template #prefix>
                <SearchOutlined />
              </template>
            </a-input>
          </a-col>
          <a-col :span="8" v-if="activeTab !== 'queue'">
            <a-date-picker
              v-model:value="searchForm.date"
              style="width: 100%"
              placeholder="预约日期"
              @change="handleSearch"
            />
          </a-col>
          <a-col :span="activeTab !== 'queue' ? 8 : 16">
            <a-space>
              <a-button type="primary" @click="handleSearch">
                <SearchOutlined />
                搜索
              </a-button>
              <a-button @click="handleReset">重置</a-button>
            </a-space>
          </a-col>
        </a-row>
      </div>

      <!-- 就诊列表表格 -->
      <a-table
        :columns="getColumns()"
        :data-source="visitList"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        :scroll="{ x: 1200, y: 'calc(100vh - 420px)' }"
        size="middle"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <!-- 挂号状态 -->
            <a-tag
              :color="getRegistrationStatusColor(record.registration_status)"
            >
              {{ getRegistrationStatusText(record.registration_status) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'registration_status'">
            <!-- 挂号状态 -->
            <a-tag
              :color="getRegistrationStatusColor(record.registration_status)"
            >
              {{ getRegistrationStatusText(record.registration_status) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'examination_status'">
            <!-- 检查状态 -->
            <a-tag
              v-if="record.examination_status"
              :color="getExaminationStatusColor(record.examination_status)"
            >
              {{ getExaminationStatusText(record.examination_status) }}
            </a-tag>
            <span v-else>-</span>
          </template>
          <template v-else-if="column.key === 'priority'">
            <a-tag :color="getPriorityColor(record.priority)">
              {{ getPriorityText(record.priority) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'registration_type'">
            <a-tag>
              {{ getRegistrationTypeText(record.registration_type) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'payment_status'">
            <a-tag :color="getPaymentStatusColor(record.payment_status)">
              {{ getPaymentStatusText(record.payment_status) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'scheduled_date'">
            {{
              record.scheduled_date
                ? dayjs(record.scheduled_date).format("YYYY-MM-DD")
                : "-"
            }}
          </template>
          <template v-else-if="column.key === 'scheduled_time'">
            {{ record.scheduled_time || "-" }}
          </template>
          <template v-else-if="column.key === 'examination_date'">
            {{
              record.examination_date
                ? dayjs(record.examination_date).format("YYYY-MM-DD")
                : "-"
            }}
          </template>
          <template v-else-if="column.key === 'examination_time'">
            {{ record.examination_time || "-" }}
          </template>
          <template v-else-if="column.key === 'eye_side'">
            {{ getEyeSideText(record.eye_side) }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button
                type="link"
                size="small"
                @click="viewRegistration(record)"
              >
                <EyeOutlined />
                详情
              </a-button>
              <!-- 队列：未签到可签到/取消；已签到可检查/取消；已取消仅详情 -->
              <a-button
                type="link"
                size="small"
                @click="markCheckedIn(record)"
                v-if="
                  activeTab === 'queue' &&
                  record.registration_status === 'unsigned'
                "
                >签到</a-button
              >
              <a-button
                type="link"
                size="small"
                @click="startExamination(record)"
                v-if="
                  (activeTab === 'queue' &&
                    record.registration_status === 'checked_in') ||
                  activeTab === 'in_progress'
                "
                >检查</a-button
              >
              <a-button
                type="link"
                size="small"
                danger
                @click="cancelRegistration(record)"
                v-if="
                  activeTab === 'queue' &&
                  (record.registration_status === 'unsigned' ||
                    record.registration_status === 'checked_in')
                "
                >取消</a-button
              >
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { message } from "ant-design-vue";
import request, {
  isResponseSuccess,
  getResponseMessage,
} from "@/utils/request";
import {
  registrationAPI,
  patientAPI,
  doctorAPI,
  examinationTypeAPI,
} from "@/api";
import visitManagementAPI from "@/api/visitManagement";
import { usePatientStore } from "@/store/modules/patient";
import dayjs from "dayjs";
import {
  ReloadOutlined,
  SearchOutlined,
  UserOutlined,
  BellOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  EyeOutlined,
  PlusOutlined,
  CalendarOutlined,
  FileTextOutlined,
  CheckOutlined,
  CloseOutlined,
} from "@ant-design/icons-vue";

// 预约挂号相关数据
const registrationModalVisible = ref(false);
const registrationFormRef = ref(null);
const patientList = ref([]);
const doctorList = ref([]);
const technicianList = ref([]); // 技师列表
const examinationTypes = ref([]);

// 日期禁用函数
const disabledDate = (current) => {
  // 禁用过去的日期
  return current && current < dayjs().startOf("day");
};

const registrationForm = reactive({
  patient_id: null,
  examination_type_id: null,
  department: "眼科",
  doctor_id: null,
  technician_id: null, // 检查技师
  eye_side: null, // 检查眼别
  registration_type: "normal",
  scheduled_date: null,
  scheduled_time: null,
  priority: "normal",
  payment_status: "unpaid",
  chief_complaint: "",
  notes: "",
});

const registrationRules = {
  patient_id: [{ required: true, message: "请选择患者", trigger: "change" }],
  examination_type_id: [
    { required: true, message: "请选择检查类型", trigger: "change" },
  ],
  department: [{ required: true, message: "请选择科室", trigger: "change" }],
  doctor_id: [{ required: true, message: "请选择医生", trigger: "change" }],
  scheduled_date: [
    { required: true, message: "请选择预约日期", trigger: "change" },
  ],
  scheduled_time: [
    { required: true, message: "请选择预约时间", trigger: "change" },
  ],
};

// 预约挂号相关方法
const showRegistrationModal = async () => {
  registrationModalVisible.value = true;

  // 清理患者信息，避免上次数据影响下一次挂号
  patientIdInput.value = "";
  selectedPatient.value = null;
  patientNotFound.value = false;
  registrationForm.patient_id = null;

  await Promise.all([
    fetchPatients(),
    fetchDoctors(),
    fetchTechnicians(),
    fetchExaminationTypes(),
  ]);
};

const handleRegistrationCancel = () => {
  registrationModalVisible.value = false;
  registrationFormRef.value?.resetFields();

  // 清理患者信息
  patientIdInput.value = "";
  selectedPatient.value = null;
  patientNotFound.value = false;
};

const fetchPatients = async () => {
  try {
    const response = await patientAPI.getPatients();
    if (isResponseSuccess(response)) {
      patientList.value = response.data;
    }
  } catch (error) {
    console.error("获取患者列表失败:", error);
    message.error("获取患者列表失败");
  }
};

const fetchDoctors = async () => {
  try {
    const response = await doctorAPI.getDoctors();
    if (isResponseSuccess(response)) {
      // 处理嵌套数据结构
      doctorList.value = response.data?.data || response.data || [];
      console.log("医生列表:", doctorList.value);
    }
  } catch (error) {
    console.error("获取医生列表失败:", error);
    message.error("获取医生列表失败");
  }
};

// 获取技师列表（包括doctor和technician两种用户类型）
const fetchTechnicians = async () => {
  try {
    // 直接调用用户API，查询doctor和technician两种角色
    const response = await request({
      url: "/users",
      method: "get",
      params: {
        roles: "doctor,technician", // 查询多个角色
        page: 1,
        page_size: 100,
        status: "active",
        order_by: "full_name",
        order: "asc",
      },
    });
    if (isResponseSuccess(response)) {
      // 处理嵌套数据结构
      technicianList.value = response.data?.data || response.data || [];
      console.log("技师列表（doctor + technician）:", technicianList.value);
    }
  } catch (error) {
    console.error("获取技师列表失败:", error);
    message.error("获取技师列表失败");
  }
};

const fetchExaminationTypes = async () => {
  try {
    const response = await examinationTypeAPI.getExaminationTypes();
    if (isResponseSuccess(response)) {
      // 处理嵌套数据结构
      examinationTypes.value = response.data?.data || response.data || [];
      console.log("检查类型列表:", examinationTypes.value);
    }
  } catch (error) {
    console.error("获取检查类型列表失败:", error);
    message.error("获取检查类型列表失败");
  }
};

// 患者ID输入和查询相关
const patientIdInput = ref("");
const selectedPatient = ref(null);
const patientNotFound = ref(false);

// 患者信息文本展示
const patientInfoText = computed(() => {
  if (!selectedPatient.value) return "";
  const patient = selectedPatient.value;
  const gender =
    patient.gender === "male"
      ? "男"
      : patient.gender === "female"
      ? "女"
      : "其他";
  const age = patient.birth_date
    ? dayjs().diff(dayjs(patient.birth_date), "year")
    : "未知";
  return `编号: ${patient.patient_id} | 姓名: ${patient.name} | 年龄: ${age}岁 | 性别: ${gender}`;
});

// 通过患者ID查询患者
const searchPatientById = async (patientId) => {
  if (!patientId) {
    message.warning("请输入患者编号");
    return;
  }

  try {
    patientNotFound.value = false;
    selectedPatient.value = null;

    // 查询患者信息
    const response = await patientAPI.getPatients({
      search: patientId,
    });

    if (
      isResponseSuccess(response) &&
      response.data &&
      response.data.data &&
      response.data.data.length > 0
    ) {
      // 查找匹配的患者（精确匹配patient_id）
      const patient = response.data.data.find(
        (p) => p.patient_id === patientId
      );

      if (patient) {
        selectedPatient.value = patient;
        registrationForm.patient_id = patient.id; // 设置表单中的患者ID
        message.success("已找到患者信息");
      } else {
        patientNotFound.value = true;
        registrationForm.patient_id = null;
      }
    } else {
      patientNotFound.value = true;
      registrationForm.patient_id = null;
    }
  } catch (error) {
    console.error("查询患者信息失败:", error);
    message.error("查询患者信息失败");
    patientNotFound.value = true;
    registrationForm.patient_id = null;
  }
};

// const showNewPatientForm = () => {
//   // 这里可以实现跳转到新增患者页面或弹出新增患者的模态框
//   message.info('新增患者功能将在后续版本中实现');
// };

const submitRegistration = () => {
  // 先检查患者ID是否已设置
  if (!registrationForm.patient_id) {
    message.error("请先查询并选择患者");
    return;
  }

  // 检查其他必填字段
  if (!registrationForm.examination_type_id) {
    message.error("请选择检查类型");
    return;
  }

  if (!registrationForm.doctor_id) {
    message.error("请选择医生");
    return;
  }

  registrationFormRef.value
    .validate()
    .then(async () => {
      try {
        // 获取当前日期，用于默认值
        const today = dayjs().format("YYYY-MM-DD");
        const now = dayjs().format("HH:mm:ss");

        // 格式化日期和时间 - 确保使用正确的格式
        const formattedDate = registrationForm.scheduled_date
          ? dayjs(registrationForm.scheduled_date).format("YYYY-MM-DD")
          : today;
        const formattedTime = registrationForm.scheduled_time
          ? dayjs(registrationForm.scheduled_time).format("HH:mm:ss")
          : now;

        // 构建请求数据 - 确保所有字段类型正确
        const registrationData = {
          patient_id: parseInt(registrationForm.patient_id, 10),
          examination_type_id: parseInt(
            registrationForm.examination_type_id,
            10
          ),
          department: registrationForm.department || "眼科",
          doctor_id: parseInt(registrationForm.doctor_id, 10),
          technician_id: registrationForm.technician_id
            ? parseInt(registrationForm.technician_id, 10)
            : null, // 检查技师（可选）
          eye_side: registrationForm.eye_side || null, // 检查眼别（可选）
          registration_type: registrationForm.registration_type || "normal",
          scheduled_date: formattedDate,
          scheduled_time: formattedTime,
          priority: registrationForm.priority || "normal",
          payment_status: registrationForm.payment_status || "unpaid",
          chief_complaint: registrationForm.chief_complaint || "",
          notes: registrationForm.notes || "",
          status: "unsigned", // 使用后端默认值
          registration_date: today,
          registration_time: now,
        };

        console.log(
          "提交的预约数据:",
          JSON.stringify(registrationData, null, 2)
        );

        try {
          const response = await registrationAPI.createRegistration(
            registrationData
          );
          console.log("API响应:", response);

          if (isResponseSuccess(response)) {
            message.success("预约挂号成功");
            handleRegistrationCancel();
            refreshData(); // 刷新列表数据
          } else {
            console.error("预约失败响应:", response);
            message.error(getResponseMessage(response) || "预约挂号失败");
          }
        } catch (apiError) {
          console.error("API调用错误:", apiError);
          if (apiError.response) {
            console.error("错误响应数据:", apiError.response.data);
            console.error("错误状态码:", apiError.response.status);
            message.error(
              `预约挂号失败: ${apiError.response.data?.msg || "未知错误"}`
            );
          } else {
            message.error("预约挂号失败，网络错误");
          }
        }
      } catch (error) {
        console.error("预约挂号处理失败:", error);
        message.error("预约挂号失败，请稍后重试");
      }
    })
    .catch((error) => {
      console.log("表单验证失败", error);
      // 显示具体的验证错误信息
      if (error.errorFields) {
        error.errorFields.forEach((field) => {
          message.error(`${field.name}: ${field.errors.join(", ")}`);
        });
      }
    });
};
const route = useRoute();
const router = useRouter();
const loading = ref(false);
const activeTab = ref("queue");

const searchForm = reactive({
  keyword: "",
  date: null,
  patientId: route.query.patient_id || "", // 从路由参数获取患者ID
});

const visitList = ref([]);

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) =>
    `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
  pageSizeOptions: ["10", "20", "50", "100"],
  showLessItems: false,
});

const getColumns = () => {
  // 根据不同标签页返回不同的列定义
  if (activeTab.value === "queue") {
    // 排队叫号标签页
    return [
      {
        title: "患者编号",
        dataIndex: ["patient", "patient_id"],
        key: "patient_id",
        align: "center",
        width: 110,
      },
      {
        title: "患者姓名",
        dataIndex: ["patient", "name"],
        key: "name",
        align: "center",
        width: 120,
        ellipsis: true,
      },
      {
        title: "检查类型",
        dataIndex: ["examination_type", "type_name"],
        key: "type_name",
        align: "center",
        width: 140,
        ellipsis: true,
      },
      {
        title: "科室",
        dataIndex: "department",
        key: "department",
        align: "center",
        width: 100,
      },
      {
        title: "队列号",
        dataIndex: "queue_number",
        key: "queue_number",
        align: "center",
        width: 90,
      },
      {
        title: "优先级",
        dataIndex: "priority",
        key: "priority",
        align: "center",
        width: 90,
      },
      {
        title: "挂号类型",
        dataIndex: "registration_type",
        key: "registration_type",
        align: "center",
        width: 110,
      },
      {
        title: "挂号状态",
        dataIndex: "registration_status",
        key: "registration_status",
        align: "center",
        width: 100,
      },
      {
        title: "缴费状态",
        dataIndex: "payment_status",
        key: "payment_status",
        align: "center",
        width: 100,
      },
      {
        title: "操作",
        key: "action",
        align: "center",
        fixed: "right",
        width: 180,
      },
    ];
  } else if (activeTab.value === "in_progress") {
    // 进行中标签页
    return [
      {
        title: "患者编号",
        dataIndex: ["patient", "patient_id"],
        key: "patient_id",
        align: "center",
        width: 110,
      },
      {
        title: "患者姓名",
        dataIndex: ["patient", "name"],
        key: "name",
        align: "center",
        width: 120,
        ellipsis: true,
      },
      {
        title: "检查类型",
        dataIndex: ["examination_type", "type_name"],
        key: "type_name",
        align: "center",
        width: 140,
        ellipsis: true,
      },
      {
        title: "主治医生",
        dataIndex: ["doctor", "full_name"],
        key: "doctor_name",
        align: "center",
        width: 120,
        ellipsis: true,
      },
      {
        title: "检查技师",
        dataIndex: ["technician", "full_name"],
        key: "technician_name",
        align: "center",
        width: 120,
        ellipsis: true,
      },
      {
        title: "检查眼别",
        dataIndex: "eye_side",
        key: "eye_side",
        align: "center",
        width: 90,
      },
      {
        title: "检查状态",
        dataIndex: "examination_status",
        key: "examination_status",
        align: "center",
        width: 100,
      },
      {
        title: "操作",
        key: "action",
        align: "center",
        fixed: "right",
        width: 140,
      },
    ];
  } else if (activeTab.value === "completed") {
    // 已完成标签页
    return [
      {
        title: "患者编号",
        dataIndex: ["patient", "patient_id"],
        key: "patient_id",
        align: "center",
        width: 110,
      },
      {
        title: "患者姓名",
        dataIndex: ["patient", "name"],
        key: "name",
        align: "center",
        width: 120,
        ellipsis: true,
      },
      {
        title: "检查类型",
        dataIndex: ["examination_type", "type_name"],
        key: "type_name",
        align: "center",
        width: 140,
        ellipsis: true,
      },
      {
        title: "主治医生",
        dataIndex: ["doctor", "full_name"],
        key: "doctor_name",
        align: "center",
        width: 120,
        ellipsis: true,
      },
      {
        title: "检查技师",
        dataIndex: ["technician", "full_name"],
        key: "technician_name",
        align: "center",
        width: 120,
        ellipsis: true,
      },
      {
        title: "检查眼别",
        dataIndex: "eye_side",
        key: "eye_side",
        align: "center",
        width: 90,
      },
      {
        title: "检查状态",
        dataIndex: "examination_status",
        key: "examination_status",
        align: "center",
        width: 100,
      },
      {
        title: "操作",
        key: "action",
        align: "center",
        fixed: "right",
        width: 140,
      },
    ];
  } else {
    // 全部标签页
    return [
      {
        title: "患者编号",
        dataIndex: ["patient", "patient_id"],
        key: "patient_id",
        align: "center",
        width: 110,
      },
      {
        title: "患者姓名",
        dataIndex: ["patient", "name"],
        key: "name",
        align: "center",
        width: 120,
        ellipsis: true,
      },
      {
        title: "检查类型",
        dataIndex: ["examination_type", "type_name"],
        key: "type_name",
        align: "center",
        width: 140,
        ellipsis: true,
      },
      {
        title: "预约日期",
        dataIndex: "scheduled_date",
        key: "scheduled_date",
        align: "center",
        width: 110,
      },
      {
        title: "预约时间",
        dataIndex: "scheduled_time",
        key: "scheduled_time",
        align: "center",
        width: 90,
      },
      {
        title: "检查日期",
        dataIndex: "examination_date",
        key: "examination_date",
        align: "center",
        width: 110,
      },
      {
        title: "检查时间",
        dataIndex: "examination_time",
        key: "examination_time",
        align: "center",
        width: 90,
      },
      {
        title: "主治医生",
        dataIndex: ["doctor", "full_name"],
        key: "doctor_name",
        align: "center",
        width: 120,
        ellipsis: true,
      },
      {
        title: "检查技师",
        dataIndex: ["technician", "full_name"],
        key: "technician_name",
        align: "center",
        width: 120,
        ellipsis: true,
      },
      {
        title: "检查眼别",
        dataIndex: "eye_side",
        key: "eye_side",
        align: "center",
        width: 90,
      },
      {
        title: "检查状态",
        dataIndex: "examination_status",
        key: "examination_status",
        align: "center",
        width: 100,
      },
      {
        title: "挂号类型",
        dataIndex: "registration_type",
        key: "registration_type",
        align: "center",
        width: 110,
      },
      {
        title: "挂号状态",
        dataIndex: "registration_status",
        key: "registration_status",
        align: "center",
        width: 100,
      },
      {
        title: "缴费状态",
        dataIndex: "payment_status",
        key: "payment_status",
        align: "center",
        width: 100,
      },
      {
        title: "操作",
        key: "action",
        align: "center",
        fixed: "right",
        width: 140,
      },
    ];
  }
};

const getQueueStatuses = () => ["checked_in", "unsigned", "cancelled"];

const fetchRegistrations = async () => {
  if (loading.value) return;
  loading.value = true;
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      search: searchForm.keyword,
    };

    // 根据不同标签页设置不同的type参数
    if (activeTab.value === "queue") {
      // 排队叫号：当天的挂号，按scheduled_time排序
      params.type = "queue";
    } else if (activeTab.value === "in_progress") {
      // 进行中：当天、已签到、检查状态为pending或in_progress
      params.type = "in_progress";
    } else if (activeTab.value === "completed") {
      // 已完成：检查状态为completed
      params.type = "completed";
    } else {
      // 全部：所有数据
      params.type = "all";
    }

    // 使用新的就诊管理API
    const resp = await visitManagementAPI.getVisitManagementList(params);
    if (isResponseSuccess(resp)) {
      visitList.value = resp.data.data || [];
      pagination.total = resp.data.total || 0;
      pagination.current = resp.data.page || 1;
      pagination.pageSize = resp.data.page_size || 10;
    } else {
      message.error(resp?.message || "获取就诊数据失败");
    }
  } catch (e) {
    console.error(e);
    message.error("网络错误");
  } finally {
    loading.value = false;
  }
};

const refreshData = () => fetchRegistrations();
const handleTabChange = () => {
  pagination.current = 1;
  if (activeTab.value === "queue") {
    searchForm.date = null;
  }
  fetchRegistrations();
};
const handleSearch = () => {
  pagination.current = 1;
  fetchRegistrations();
};
const handleReset = () => {
  searchForm.keyword = "";
  if (activeTab.value !== "queue") {
    searchForm.date = null;
  }
  fetchRegistrations();
};
const handleTableChange = (pag) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  fetchRegistrations();
};

// 挂号状态：unsigned, checked_in, cancelled
const getRegistrationStatusColor = (status) =>
  ({
    unsigned: "default",
    checked_in: "blue",
    cancelled: "red",
  }[status] || "default");

const getRegistrationStatusText = (status) =>
  ({
    unsigned: "未签到",
    checked_in: "已签到",
    cancelled: "已取消",
  }[status] || status);

// 检查状态：pending, in_progress, completed, cancelled
const getExaminationStatusColor = (status) =>
  ({
    pending: "orange",
    in_progress: "processing",
    completed: "success",
    cancelled: "error",
  }[status] || "default");

const getExaminationStatusText = (status) =>
  ({
    pending: "待检查",
    in_progress: "检查中",
    completed: "已完成",
    cancelled: "已取消",
  }[status] || status);

const getPriorityText = (p) =>
  ({
    urgent: "紧急",
    high: "高",
    normal: "普通",
    low: "低",
  }[p] ||
  p ||
  "-");

// 检查眼别文本转换
const getEyeSideText = (eyeSide) =>
  ({
    left: "左眼",
    right: "右眼",
    both: "双眼"
  }[eyeSide] ||
  eyeSide ||
  "-");

const getPriorityColor = (p) =>
  ({
    urgent: "red",
    high: "volcano",
    normal: "blue",
    low: "default",
  }[p] || "default");

const getRegistrationTypeText = (t) =>
  ({
    emergency: "急诊",
    appointment: "预约",
    normal: "普通",
    followup: "复诊",
  }[t] ||
  t ||
  "-");

const getPaymentStatusText = (s) =>
  ({
    unpaid: "未缴费",
    paid: "已缴费",
    refunded: "已退费",
  }[s] ||
  s ||
  "-");

const getPaymentStatusColor = (s) =>
  ({
    unpaid: "default",
    paid: "green",
    refunded: "gold",
  }[s] || "default");

const formatDateTime = (d, t) => {
  const date = d ? new Date(d) : null;
  return `${date ? date.toLocaleDateString("zh-CN") : "-"} ${t || ""}`.trim();
};

const viewRegistration = (record) => {
  // 查看就诊详情
  message.info(`查看就诊: ${record.registration_number}`);
  // 这里可以实现跳转到详情页或打开详情弹窗
};

const markCheckedIn = async (record) => {
  try {
    const resp = await registrationAPI.updateRegistrationStatus(
      record.registration_id,
      "checked_in"
    );
    if (isResponseSuccess(resp)) {
      message.success(getResponseMessage(resp) || "已签到");
      fetchRegistrations();
    } else {
      message.error(getResponseMessage(resp) || "操作失败");
    }
  } catch (e) {
    console.error(e);
    message.error("操作失败");
  }
};

const cancelRegistration = async (record) => {
  try {
    const resp = await registrationAPI.updateRegistrationStatus(
      record.registration_id,
      "cancelled"
    );
    if (isResponseSuccess(resp)) {
      message.success(getResponseMessage(resp) || "已取消");
      fetchRegistrations();
    } else {
      message.error(getResponseMessage(resp) || "操作失败");
    }
  } catch (e) {
    console.error(e);
    message.error("操作失败");
  }
};

const startExamination = async (record) => {
  try {
    // 获取患者store
    const patientStore = usePatientStore();
    
    let examinationId = record.examination_id;
    let examinationData = null;
    
    // 如果没有检查记录，先创建检查记录
    if (!examinationId) {
      console.log("检查记录不存在，正在创建检查记录...");
      
      const examinationAPI = (await import("@/api/examination")).default;
      
      // 创建检查记录
      const today = new Date();
      const examinationDate = new Date(today.getFullYear(), today.getMonth(), today.getDate());
      const examinationCreateData = {
        patient_id: record.patient?.id,
        examination_type_id: record.examination_type?.id || 1,
        eye_side: record.eye_side || 'both',
        examination_date: examinationDate.toISOString(),
        status: 'in_progress' // 直接设置为检查中状态
      };
      
      console.log('创建检查记录:', examinationCreateData);
      
      const createResponse = await examinationAPI.createExamination(examinationCreateData);
      
      if (isResponseSuccess(createResponse)) {
        examinationId = createResponse.data.id;
        examinationData = createResponse.data;
        console.log('检查记录创建成功:', examinationId);
        message.success('检查记录创建成功');
      } else {
        message.error(getResponseMessage(createResponse) || '创建检查记录失败');
        return;
      }
    } else {
      // 如果有检查记录，更新状态为"检查中"
      const examinationAPI = (await import("@/api/examination")).default;
      const resp = await examinationAPI.updateExaminationStatus(
        examinationId,
        "in_progress"
      );
      if (!isResponseSuccess(resp)) {
        message.error(resp?.message || "更新检查状态失败");
        return;
      }
      message.success(getResponseMessage(resp) || "开始检查");
    }

    // 准备患者信息
    const patientInfo = {
      id: record.patient?.id,
      patient_id: record.patient?.patient_id,
      name: record.patient?.name,
      gender: record.patient?.gender,
      age: record.patient?.age
    };

    // 准备检查记录信息
    const examinationInfo = {
      id: examinationId,
      examination_type_id: record.examination_type?.id,
      examination_type: record.examination_type?.type_name,
      department: record.department,
      doctor_id: record.doctor?.id,
      doctor_name: record.doctor?.full_name,
      scheduled_date: record.scheduled_date,
      scheduled_time: record.scheduled_time,
      priority: record.priority,
      notes: record.notes,
      registration_id: record.registration_id,
      registration_number: record.registration_number,
      eye_side: record.eye_side || 'both'
    };

    // 存储到pinia store
    patientStore.setPatientAndExamination(patientInfo, examinationInfo, true);
    patientStore.saveToLocalStorage();

    // 跳转到ViewImages页面，携带examination_id
    await router.push({
      name: "view-images",
      query: {
        examinationId: examinationId,
        mode: 'new_examination'
      },
    });
  } catch (e) {
    console.error("开始检查失败:", e);
    message.error("开始检查失败: " + (e.message || "未知错误"));
  }
};

onMounted(() => {
  fetchRegistrations();
});
</script>

<style scoped>
.visit-management {
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

/* 预约挂号弹窗样式 */
.registration-modal {
  :deep(.ant-modal-content) {
    border-radius: 12px;
    overflow: hidden;
  }

  :deep(.ant-modal-header) {
    background: #1890ff;
    padding: 16px 24px;

    .ant-modal-title {
      color: white;
      font-size: 18px;
      font-weight: 600;
    }
  }

  :deep(.ant-modal-body) {
    padding: 24px;
    max-height: 70vh;
    overflow-y: auto;
  }

  :deep(.ant-modal-footer) {
    border-top: 1px solid #f0f0f0;
    padding: 16px 24px;
  }
}

/* 表单区域样式 */
.form-section {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);

  .section-title {
    display: flex;
    align-items: center;
    font-weight: 600;
    font-size: 16px;

    .anticon {
      margin-right: 8px;
      color: #1890ff;
    }
  }
}

/* 表单元素样式 */
.custom-select,
.custom-date-picker,
.custom-time-picker,
.custom-textarea {
  width: 100%;

  &:hover {
    border-color: #40a9ff;
  }

  &:focus,
  &-focused {
    border-color: #1890ff;
    box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
  }
}

.patient-info {
  margin-top: 16px;
  margin-bottom: 16px;

  .patient-info-alert {
    border-radius: 8px;
  }
}

/* 按钮样式 */
.registration-form {
  .ant-btn {
    height: 40px;
    border-radius: 6px;
    font-weight: 500;

    &-primary {
      background: #1890ff;
      border-color: #1890ff;

      &:hover {
        background: #40a9ff;
        border-color: #40a9ff;
      }
    }
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .registration-modal {
    :deep(.ant-modal-body) {
      padding: 16px;
    }
  }

  .form-section {
    margin-bottom: 16px;
  }

  .custom-select,
  .custom-date-picker,
  .custom-time-picker {
    font-size: 14px;
  }
}

@media (max-width: 576px) {
  .registration-modal {
    :deep(.ant-modal-body) {
      padding: 12px;
      max-height: 80vh;
    }

    :deep(.ant-modal-header) {
      padding: 12px 16px;

      .ant-modal-title {
        font-size: 16px;
      }
    }
  }

  .form-footer {
    flex-direction: column;

    .ant-btn {
      width: 100%;
      margin-bottom: 8px;
    }
  }
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
  max-height: calc(100vh - 420px); /* 设置最大高度，为选项卡预留更多空间 */
  overflow-y: auto; /* 内容超出时滚动 */
}

.main-card :deep(.ant-pagination) {
  margin: 16px 0 24px 0; /* 上边距16px，下边距24px */
  flex-shrink: 0; /* 分页器不收缩，始终可见 */
  text-align: center;
}

.status-tabs {
  margin-bottom: 8px; /* 与搜索区域保持一致，减少底部边距 */
  flex-shrink: 0; /* 选项卡不收缩 */
}

.status-tabs :deep(.ant-tabs-nav) {
  background: #fafafa;
  padding: 8px 16px;
  border-radius: 8px;
  margin-bottom: 0;
}

.search-area {
  margin-bottom: 8px; /* 减少底部边距，为分页器预留更多空间 */
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  flex-shrink: 0; /* 搜索区域不收缩 */
}

/* 表格头部固定 */
.main-card :deep(.ant-table-thead) {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #fff;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .main-card :deep(.ant-table-body) {
    max-height: calc(100vh - 460px);
  }
}

@media (max-width: 1200px) {
  .main-card :deep(.ant-table-body) {
    max-height: calc(100vh - 500px);
  }
}

@media (max-width: 768px) {
  .visit-management {
    padding: 16px;
  }
}
</style>
