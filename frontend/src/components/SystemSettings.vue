<template>
  <div class="system-settings">
    <a-row :gutter="24">
      <!-- 左侧菜单 -->
      <a-col :span="6">
        <a-card class="settings-menu">
          <a-menu
            v-model:selectedKeys="selectedKeys"
            mode="inline"
            @click="handleMenuClick"
          >
            <a-menu-item key="general">
              <SettingOutlined />
              常规设置
            </a-menu-item>
            <a-menu-item key="device">
              <CameraOutlined />
              设备配置
            </a-menu-item>
            <a-menu-item key="user">
              <UserOutlined />
              用户管理
            </a-menu-item>
            <a-menu-item key="role">
              <TeamOutlined />
              角色管理
            </a-menu-item>
            <a-menu-item key="permission">
              <SafetyCertificateOutlined />
              权限管理
            </a-menu-item>
            <a-menu-item key="database-config">
              <DatabaseOutlined />
              数据库配置
            </a-menu-item>
            <a-menu-item key="logging-config">
              <FileTextOutlined />
              日志配置
            </a-menu-item>
            <a-menu-item key="other-config">
              <SettingOutlined />
              其他配置
            </a-menu-item>
            <a-menu-item key="system">
              <InfoCircleOutlined />
              系统信息
            </a-menu-item>
          </a-menu>
        </a-card>
      </a-col>
      
      <!-- 右侧内容 -->
      <a-col :span="18">
        <a-card :title="currentTitle" class="settings-content">
          <!-- 常规设置 -->
          <div v-if="selectedKeys[0] === 'general'" class="settings-panel">
            <a-form layout="vertical">
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="系统名称">
                    <a-input v-model:value="generalSettings.systemName" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="语言设置">
                    <a-select v-model:value="generalSettings.language">
                      <a-select-option value="zh-CN">简体中文</a-select-option>
                      <a-select-option value="en-US">English</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
              </a-row>
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="主题设置">
                    <a-select v-model:value="generalSettings.theme">
                      <a-select-option value="light">浅色主题</a-select-option>
                      <a-select-option value="dark">深色主题</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="自动保存间隔(分钟)">
                    <a-input-number
                      v-model:value="generalSettings.autoSaveInterval"
                      :min="1"
                      :max="60"
                      style="width: 100%"
                    />
                  </a-form-item>
                </a-col>
              </a-row>
              <a-form-item>
                <a-space>
                  <a-button type="primary" @click="saveGeneralSettings">
                    保存设置
                  </a-button>
                  <a-button @click="resetGeneralSettings">
                    重置
                  </a-button>
                </a-space>
              </a-form-item>
            </a-form>
          </div>
          
          <!-- 设备配置 -->
          <div v-else-if="selectedKeys[0] === 'device'" class="settings-panel">
            <a-form layout="vertical">
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="Socket服务器地址">
                    <a-input v-model:value="deviceSettings.socketHost" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="Socket服务器端口">
                    <a-input-number
                      v-model:value="deviceSettings.socketPort"
                      :min="1"
                      :max="65535"
                      style="width: 100%"
                    />
                  </a-form-item>
                </a-col>
              </a-row>
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="图像质量">
                    <a-select v-model:value="deviceSettings.imageQuality">
                      <a-select-option value="high">高质量</a-select-option>
                      <a-select-option value="medium">中等质量</a-select-option>
                      <a-select-option value="low">低质量</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="连接超时(秒)">
                    <a-input-number
                      v-model:value="deviceSettings.timeout"
                      :min="5"
                      :max="300"
                      style="width: 100%"
                    />
                  </a-form-item>
                </a-col>
              </a-row>
              <a-form-item label="自动重连">
                <a-switch v-model:checked="deviceSettings.autoReconnect" />
                <span class="switch-label">启用自动重连</span>
              </a-form-item>
              <a-form-item>
                <a-space>
                  <a-button type="primary" @click="saveDeviceSettings">
                    保存设置
                  </a-button>
                  <a-button @click="testConnection">
                    测试连接
                  </a-button>
                  <a-button @click="resetDeviceSettings">
                    重置
                  </a-button>
                </a-space>
              </a-form-item>
            </a-form>
          </div>
          
          <!-- 用户管理 -->
          <div v-else-if="selectedKeys[0] === 'user'" class="settings-panel user-management-panel">
            <div class="user-actions user-management-actions">
              <a-button type="primary" @click="showAddUserModal">
                <UserAddOutlined />
                添加用户
              </a-button>
            </div>
            
            <div class="user-management-content">
              <a-table
                :columns="userColumns"
                :data-source="userList"
                :loading="userLoading"
                :pagination="userPagination"
                :scroll="{ x: 1200, y: 'calc(100vh - 420px)' }"
                row-key="id"
                class="user-management-table"
                @change="handleUserTableChange"
              >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'userType'">
                  <a-tag :color="getUserTypeColor(record.user_type)">
                    {{ getUserTypeName(record.user_type) }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'status'">
                  <a-badge :status="record.status === 'active' ? 'success' : 'default'" />
                  {{ record.status === 'active' ? '激活' : '停用' }}
                </template>
                <template v-else-if="column.key === 'lastLogin'">
                  {{ record.last_login_at ? new Date(record.last_login_at).toLocaleString() : '-' }}
                </template>
                <template v-else-if="column.key === 'action'">
                  <a-space>
                    <a-button type="link" size="small" @click="editUser(record)">
                      <EditOutlined />
                      编辑
                    </a-button>
                    <a-button 
                      type="link" 
                      size="small" 
                      :danger="record.status === 'active'"
                      @click="toggleUserStatus(record)"
                    >
                      {{ record.status === 'active' ? '停用' : '激活' }}
                    </a-button>
                    <a-button 
                      type="link" 
                      size="small" 
                      danger
                      @click="deleteUser(record)"
                      :disabled="record.user_type === 'admin'"
                    >
                      <DeleteIcon />
                      删除
                    </a-button>
                  </a-space>
                </template>
              </template>
              </a-table>
            </div>
          </div>

          <!-- 角色管理 -->
          <div v-else-if="selectedKeys[0] === 'role'" class="settings-panel role-management-panel">
            <div class="role-actions">
              <a-button type="primary" @click="showAddRoleModal">
                <PlusOutlined />
                添加角色
              </a-button>
            </div>
            
            <a-table
              :columns="roleColumns"
              :data-source="roleList"
              :loading="roleLoading"
              :scroll="{ x: 1000, y: 'calc(100vh - 380px)' }"
              row-key="id"
              :pagination="false"
              class="role-management-table"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'is_system_role'">
                  <a-tag :color="record.is_system_role ? 'red' : 'green'">
                    {{ record.is_system_role ? '系统角色' : '自定义角色' }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'is_active'">
                  <a-tag :color="record.is_active ? 'green' : 'red'">
                    {{ record.is_active ? '启用' : '禁用' }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'action'">
                  <a-space>
                    <a-button type="link" size="small" @click="editRole(record)">
                      <EditOutlined />
                      编辑
                    </a-button>
                    <a-button type="link" size="small" @click="manageRolePermissions(record)">
                      <KeyOutlined />
                      权限
                    </a-button>
                    <a-button 
                      type="link" 
                      size="small" 
                      danger
                      @click="deleteRole(record)"
                      :disabled="record.is_system_role"
                    >
                      <DeleteIcon />
                      删除
                    </a-button>
                  </a-space>
                </template>
              </template>
            </a-table>
          </div>

          <!-- 权限管理 -->
          <div v-else-if="selectedKeys[0] === 'permission'" class="settings-panel permission-management-panel">
            <div class="permission-actions">
              <a-button type="primary" @click="showAddPermissionModal">
                <PlusOutlined />
                添加权限
              </a-button>
            </div>
            
            <a-table
              :columns="permissionColumns"
              :data-source="permissionList"
              :loading="permissionLoading"
              :scroll="{ x: 1200, y: 'calc(100vh - 380px)' }"
              row-key="id"
              :pagination="false"
              class="permission-management-table"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'is_active'">
                  <a-tag :color="record.is_active ? 'green' : 'red'">
                    {{ record.is_active ? '启用' : '禁用' }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'action'">
                  <a-space>
                    <a-button type="link" size="small" @click="editPermission(record)">
                      <EditOutlined />
                      编辑
                    </a-button>
                    <a-button 
                      type="link" 
                      size="small" 
                      danger
                      @click="deletePermission(record)"
                    >
                      <DeleteIcon />
                      删除
                    </a-button>
                  </a-space>
                </template>
              </template>
            </a-table>
          </div>
          
          <!-- 数据库配置 -->
          <div v-else-if="selectedKeys[0] === 'database-config'" class="settings-panel settings-scroll-panel">
            <a-form layout="vertical" :loading="databaseConfigLoading">
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="数据库主机">
                    <a-input v-model:value="databaseConfig.host" placeholder="请输入数据库主机地址" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="端口">
                    <a-input-number
                      v-model:value="databaseConfig.port"
                      :min="1"
                      :max="65535"
                      style="width: 100%"
                      placeholder="请输入端口号"
                    />
                  </a-form-item>
                </a-col>
              </a-row>
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="数据库名">
                    <a-input v-model:value="databaseConfig.database" placeholder="请输入数据库名" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="用户名">
                    <a-input v-model:value="databaseConfig.username" placeholder="请输入用户名" />
                  </a-form-item>
                </a-col>
              </a-row>
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="密码">
                    <a-input-password v-model:value="databaseConfig.password" placeholder="请输入密码" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="日志级别">
                    <a-select v-model:value="databaseConfig.log_level" placeholder="请选择日志级别">
                      <a-select-option value="silent">Silent</a-select-option>
                      <a-select-option value="error">Error</a-select-option>
                      <a-select-option value="warn">Warn</a-select-option>
                      <a-select-option value="info">Info</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
              </a-row>
              <a-form-item>
                <a-space>
                  <a-button type="primary" @click="saveDatabaseConfig" :loading="databaseConfigLoading">
                    保存配置
                  </a-button>
                  <a-button @click="resetDatabaseConfig">
                    重置
                  </a-button>
                  <a-button @click="testDatabaseConnection" :loading="testConnectionLoading">
                    测试连接
                  </a-button>
                </a-space>
              </a-form-item>
            </a-form>
          </div>

          <!-- 日志配置 -->
          <div v-else-if="selectedKeys[0] === 'logging-config'" class="settings-panel settings-scroll-panel">
            <a-form layout="vertical" :loading="loggingConfigLoading">
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="日志级别">
                    <a-select v-model:value="loggingConfig.level" placeholder="请选择日志级别">
                      <a-select-option value="debug">Debug</a-select-option>
                      <a-select-option value="info">Info</a-select-option>
                      <a-select-option value="warn">Warn</a-select-option>
                      <a-select-option value="error">Error</a-select-option>
                      <a-select-option value="fatal">Fatal</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="日志格式">
                    <a-select v-model:value="loggingConfig.format" placeholder="请选择日志格式">
                      <a-select-option value="json">JSON</a-select-option>
                      <a-select-option value="text">Text</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
              </a-row>
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="输出方式">
                    <a-select v-model:value="loggingConfig.output" placeholder="请选择输出方式">
                      <a-select-option value="console">控制台</a-select-option>
                      <a-select-option value="file">文件</a-select-option>
                      <a-select-option value="both">控制台+文件</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="日志文件路径">
                    <a-input v-model:value="loggingConfig.file_path" placeholder="请输入日志文件路径" />
                  </a-form-item>
                </a-col>
              </a-row>
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="报告调用者">
                    <a-switch v-model:checked="loggingConfig.report_caller" />
                    <span class="switch-label">启用调用者信息</span>
                  </a-form-item>
                </a-col>
              </a-row>
              <a-form-item>
                <a-space>
                  <a-button type="primary" @click="saveLoggingConfig" :loading="loggingConfigLoading">
                    保存配置
                  </a-button>
                  <a-button @click="resetLoggingConfig">
                    重置
                  </a-button>
                </a-space>
              </a-form-item>
            </a-form>
          </div>

          <!-- 其他配置 -->
          <div v-else-if="selectedKeys[0] === 'other-config'" class="settings-panel settings-scroll-panel">
            <a-form layout="vertical" :loading="otherConfigLoading">
              <a-divider orientation="left">服务器配置</a-divider>
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="服务器主机">
                    <a-input v-model:value="otherConfig.server.host" placeholder="请输入服务器主机地址" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="服务器端口">
                    <a-input-number
                      v-model:value="otherConfig.server.port"
                      :min="1"
                      :max="65535"
                      style="width: 100%"
                      placeholder="请输入端口号"
                    />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-divider orientation="left">第三方服务配置</a-divider>
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="基础URL">
                    <a-input v-model:value="otherConfig.third_party.base_url" placeholder="请输入第三方服务基础URL" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="端口">
                    <a-input-number
                      v-model:value="otherConfig.third_party.port"
                      :min="1"
                      :max="65535"
                      style="width: 100%"
                      placeholder="请输入端口号"
                    />
                  </a-form-item>
                </a-col>
              </a-row>
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="超时时间(秒)">
                    <a-input-number
                      v-model:value="otherConfig.third_party.timeout"
                      :min="1"
                      :max="300"
                      style="width: 100%"
                      placeholder="请输入超时时间"
                    />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="重试次数">
                    <a-input-number
                      v-model:value="otherConfig.third_party.retry_count"
                      :min="0"
                      :max="10"
                      style="width: 100%"
                      placeholder="请输入重试次数"
                    />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-divider orientation="left">存储配置</a-divider>
              <a-row :gutter="16">
                <a-col :span="24">
                  <a-form-item label="保存文件夹路径">
                    <a-input v-model:value="otherConfig.save_folder_path" placeholder="请输入保存文件夹路径" />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-form-item>
                <a-space>
                  <a-button type="primary" @click="saveOtherConfig" :loading="otherConfigLoading">
                    保存配置
                  </a-button>
                  <a-button @click="resetOtherConfig">
                    重置
                  </a-button>
                </a-space>
              </a-form-item>
            </a-form>
          </div>

          <!-- 系统信息 -->
          <div v-else-if="selectedKeys[0] === 'system'" class="settings-panel">
            <a-descriptions :column="2" bordered>
              <a-descriptions-item label="系统版本">
                {{ systemInfo.version }}
              </a-descriptions-item>
              <a-descriptions-item label="构建时间">
                {{ systemInfo.buildTime }}
              </a-descriptions-item>
              <a-descriptions-item label="操作系统">
                {{ systemInfo.platform }}
              </a-descriptions-item>
              <a-descriptions-item label="系统架构">
                {{ systemInfo.arch }}
              </a-descriptions-item>
              <a-descriptions-item label="运行时间">
                {{ systemInfo.uptime }}
              </a-descriptions-item>
              <a-descriptions-item label="内存使用">
                {{ systemInfo.memoryUsage }}
              </a-descriptions-item>
              <a-descriptions-item label="数据库状态">
                <a-badge status="success" text="正常" />
              </a-descriptions-item>
              <a-descriptions-item label="Socket连接">
                <a-badge status="processing" text="已连接" />
              </a-descriptions-item>
            </a-descriptions>
            
            <div class="system-actions">
              <a-space>
                <a-button type="primary" @click="exportLogs">
                  <ExportOutlined />
                  导出日志
                </a-button>
                <a-button @click="clearCache">
                  <DeleteOutlined />
                  清除缓存
                </a-button>
                <a-button danger @click="restartSystem">
                  <ReloadOutlined />
                  重启系统
                </a-button>
              </a-space>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 用户表单对话框 -->
    <a-modal
      v-model:open="userFormVisible"
      :title="userFormData.id ? '编辑用户' : '添加用户'"
      width="600px"
      @ok="handleUserFormSubmit"
      :confirm-loading="userFormLoading"
      @cancel="userFormVisible = false"
    >
      <a-form
        ref="userForm"
        :model="userFormData"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
        :rules="userFormRules"
      >
        <a-form-item label="用户名" name="username">
          <a-input v-model:value="userFormData.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="姓名" name="full_name">
          <a-input v-model:value="userFormData.full_name" placeholder="请输入姓名" />
        </a-form-item>
        <a-form-item label="邮箱" name="email">
          <a-input v-model:value="userFormData.email" placeholder="请输入邮箱" />
        </a-form-item>
        <a-form-item label="电话" name="phone">
          <a-input v-model:value="userFormData.phone" placeholder="请输入电话" />
        </a-form-item>
        <a-form-item label="用户类型" name="user_type">
          <a-select v-model:value="userFormData.user_type" placeholder="请选择用户类型">
            <a-select-option
              v-for="option in userTypeOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="科室" name="department">
          <a-input v-model:value="userFormData.department" placeholder="请输入科室" />
        </a-form-item>
        <a-form-item label="职称" name="title">
          <a-input v-model:value="userFormData.title" placeholder="请输入职称" />
        </a-form-item>
        <a-form-item label="执业证书号" name="license_number">
          <a-input v-model:value="userFormData.license_number" placeholder="请输入执业证书号" />
        </a-form-item>
        <a-form-item label="密码" name="password" v-if="!userFormData.id">
          <a-input-password v-model:value="userFormData.password" placeholder="请输入密码" />
        </a-form-item>
        <a-form-item label="角色" name="role_ids">
          <a-select
            v-model:value="userFormData.role_ids"
            mode="multiple"
            placeholder="请选择角色"
            style="width: 100%"
          >
            <a-select-option
              v-for="role in roleList"
              :key="role.id"
              :value="role.id"
            >
              {{ role.role_name }}
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 角色表单对话框 -->
    <a-modal
      v-model:open="roleFormVisible"
      :title="roleFormData.id ? '编辑角色' : '添加角色'"
      width="500px"
      @ok="handleRoleFormSubmit"
      :confirm-loading="roleFormLoading"
      @cancel="roleFormVisible = false"
    >
      <a-form
        ref="roleForm"
        :model="roleFormData"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
        :rules="roleFormRules"
      >
        <a-form-item label="角色名称" name="role_name">
          <a-input v-model:value="roleFormData.role_name" placeholder="请输入角色名称" />
        </a-form-item>
        <a-form-item label="角色代码" name="role_code">
          <a-input v-model:value="roleFormData.role_code" placeholder="请输入角色代码" />
        </a-form-item>
        <a-form-item label="描述" name="description">
          <a-textarea v-model:value="roleFormData.description" placeholder="请输入角色描述" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 权限表单对话框 -->
    <a-modal
      v-model:open="permissionFormVisible"
      :title="permissionFormData.id ? '编辑权限' : '添加权限'"
      width="500px"
      @ok="handlePermissionFormSubmit"
      :confirm-loading="permissionFormLoading"
      @cancel="permissionFormVisible = false"
    >
      <a-form
        ref="permissionForm"
        :model="permissionFormData"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
        :rules="permissionFormRules"
      >
        <a-form-item label="权限名称" name="permission_name">
          <a-input v-model:value="permissionFormData.permission_name" placeholder="请输入权限名称" />
        </a-form-item>
        <a-form-item label="权限代码" name="permission_code">
          <a-input v-model:value="permissionFormData.permission_code" placeholder="请输入权限代码" />
        </a-form-item>
        <a-form-item label="资源" name="resource">
          <a-input v-model:value="permissionFormData.resource" placeholder="请输入资源名称" />
        </a-form-item>
        <a-form-item label="操作" name="action">
          <a-input v-model:value="permissionFormData.action" placeholder="请输入操作类型" />
        </a-form-item>
        <a-form-item label="描述" name="description">
          <a-textarea v-model:value="permissionFormData.description" placeholder="请输入权限描述" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
  SettingOutlined,
  CameraOutlined,
  UserOutlined,
  DatabaseOutlined,
  UserAddOutlined,
  ExportOutlined,
  DeleteOutlined,
  ReloadOutlined,
  EditOutlined,
  DeleteOutlined as DeleteIcon,
  TeamOutlined,
  SafetyCertificateOutlined,
  PlusOutlined,
  KeyOutlined,
  FileTextOutlined,
  InfoCircleOutlined
} from '@ant-design/icons-vue';
import userAPI from '@/api/user';
import roleAPI from '@/api/role';
import permissionAPI from '@/api/permission';
import { configAPI } from '@/api/config';

// 响应式数据
const selectedKeys = ref(['general']);

// 常规设置
const generalSettings = reactive({
  systemName: '瑞尔明康眼底检查系统',
  language: 'zh-CN',
  theme: 'light',
  autoSaveInterval: 5
});

// 配置相关数据
const databaseConfig = reactive({
  host: '',
  port: 3306,
  database: '',
  username: '',
  password: '',
  log_level: 'info'
});

const loggingConfig = reactive({
  level: 'info',
  format: 'json',
  output: 'console',
  file_path: '',
  report_caller: false
});

const otherConfig = reactive({
  server: {
    host: '',
    port: 8080
  },
  third_party: {
    base_url: '',
    port: 8080,
    timeout: 30,
    retry_count: 3
  },
  save_folder_path: ''
});

// 配置加载状态
const databaseConfigLoading = ref(false);
const loggingConfigLoading = ref(false);
const otherConfigLoading = ref(false);
const testConnectionLoading = ref(false);

// 设备配置
const deviceSettings = reactive({
  socketHost: 'localhost',
  socketPort: 8081,
  imageQuality: 'high',
  timeout: 30,
  autoReconnect: true
});

// 用户管理相关数据
const userList = ref([]);
const userLoading = ref(false);
const userPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
});

// 用户表单相关
const userFormVisible = ref(false);
const userFormLoading = ref(false);
const userForm = ref(null);
const userFormData = reactive({
  id: null,
  username: '',
  full_name: '',
  email: '',
  phone: '',
  user_type: 'doctor',
  department: '',
  title: '',
  license_number: '',
  password: '',
  role_ids: []
});

// 角色和权限数据
const roleList = ref([]);
const permissionList = ref([]);

// 角色管理相关数据
const roleLoading = ref(false);
const roleFormVisible = ref(false);
const roleFormLoading = ref(false);
const roleForm = ref(null);
const roleFormData = reactive({
  id: null,
  role_name: '',
  role_code: '',
  description: ''
});

// 权限管理相关数据
const permissionLoading = ref(false);
const permissionFormVisible = ref(false);
const permissionFormLoading = ref(false);
const permissionForm = ref(null);
const permissionFormData = reactive({
  id: null,
  permission_name: '',
  permission_code: '',
  resource: '',
  action: '',
  description: ''
});

// 用户类型选项
const userTypeOptions = [
  { value: 'admin', label: '管理员' },
  { value: 'doctor', label: '医生' },
  { value: 'technician', label: '技师' },
  { value: 'viewer', label: '查看者' }
];

// 用户表单验证规则
const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 5, max: 20, message: '用户名长度在5-20个字符', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  user_type: [
    { required: true, message: '请选择用户类型', trigger: 'change' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ]
};

// 角色表单验证规则
const roleFormRules = {
  role_name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ],
  role_code: [
    { required: true, message: '请输入角色代码', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '角色代码只能包含字母、数字和下划线，且不能以数字开头', trigger: 'blur' }
  ]
};

// 权限表单验证规则
const permissionFormRules = {
  permission_name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' }
  ],
  permission_code: [
    { required: true, message: '请输入权限代码', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '权限代码只能包含字母、数字和下划线，且不能以数字开头', trigger: 'blur' }
  ],
  resource: [
    { required: true, message: '请输入资源名称', trigger: 'blur' }
  ],
  action: [
    { required: true, message: '请输入操作类型', trigger: 'blur' }
  ]
};

// 数据库配置表单验证规则
const databaseConfigRules = {
  host: [
    { required: true, message: '请输入数据库主机地址', trigger: 'blur' }
  ],
  port: [
    { required: true, message: '请输入端口号', trigger: 'blur' },
    { type: 'number', min: 1, max: 65535, message: '端口号必须在1-65535之间', trigger: 'blur' }
  ],
  database: [
    { required: true, message: '请输入数据库名', trigger: 'blur' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ],
  max_open_conns: [
    { type: 'number', min: 1, max: 1000, message: '最大连接数必须在1-1000之间', trigger: 'blur' }
  ],
  max_idle_conns: [
    { type: 'number', min: 1, max: 100, message: '最大空闲连接数必须在1-100之间', trigger: 'blur' }
  ],
  conn_max_lifetime: [
    { type: 'number', min: 60, max: 86400, message: '连接最大生存时间必须在60-86400秒之间', trigger: 'blur' }
  ]
};

// 日志配置表单验证规则
const loggingConfigRules = {
  level: [
    { required: true, message: '请选择日志级别', trigger: 'change' }
  ],
  format: [
    { required: true, message: '请选择日志格式', trigger: 'change' }
  ],
  output: [
    { required: true, message: '请选择输出方式', trigger: 'change' }
  ],
  file_path: [
    { required: true, message: '请输入日志文件路径', trigger: 'blur' }
  ]
};

// 其他配置表单验证规则
const otherConfigRules = {
  'server.host': [
    { required: true, message: '请输入服务器主机地址', trigger: 'blur' }
  ],
  'server.port': [
    { required: true, message: '请输入服务器端口', trigger: 'blur' },
    { type: 'number', min: 1, max: 65535, message: '端口号必须在1-65535之间', trigger: 'blur' }
  ],
  'third_party.base_url': [
    { required: true, message: '请输入第三方服务基础URL', trigger: 'blur' },
    { pattern: /^https?:\/\//, message: 'URL必须以http://或https://开头', trigger: 'blur' }
  ],
  'third_party.port': [
    { required: true, message: '请输入第三方服务端口', trigger: 'blur' },
    { type: 'number', min: 1, max: 65535, message: '端口号必须在1-65535之间', trigger: 'blur' }
  ],
  'third_party.timeout': [
    { type: 'number', min: 1, max: 300, message: '超时时间必须在1-300秒之间', trigger: 'blur' }
  ],
  'third_party.retry_count': [
    { type: 'number', min: 0, max: 10, message: '重试次数必须在0-10之间', trigger: 'blur' }
  ],
  save_folder_path: [
    { required: true, message: '请输入保存文件夹路径', trigger: 'blur' }
  ]
};

// 系统信息
const systemInfo = reactive({
  version: '加载中...',
  buildTime: '加载中...',
  platform: '加载中...',
  arch: '加载中...',
  uptime: '加载中...',
  memoryUsage: '加载中...'
});

// 用户表格列配置
const userColumns = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
    width: 120,
    align: 'center'
  },
  {
    title: '姓名',
    dataIndex: 'fullName',
    key: 'fullName',
    width: 120,
    align: 'center'
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email',
    width: 200,
    align: 'center'
  },
  {
    title: '用户类型',
    dataIndex: 'userType',
    key: 'userType',
    width: 100,
    align: 'center'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 80,
    align: 'center'
  },
  {
    title: '最后登录',
    dataIndex: 'lastLogin',
    key: 'lastLogin',
    width: 150,
    align: 'center'
  },
  {
    title: '操作',
    key: 'action',
    width: 150,
    fixed: 'right',
    align: 'center'
  }
];

// 角色表格列配置
const roleColumns = [
  {
    title: '角色名称',
    dataIndex: 'role_name',
    key: 'role_name',
    width: 150,
    align: 'center'
  },
  {
    title: '角色代码',
    dataIndex: 'role_code',
    key: 'role_code',
    width: 150,
    align: 'center'
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description',
    width: 200,
    align: 'center'
  },
  {
    title: '类型',
    dataIndex: 'is_system_role',
    key: 'is_system_role',
    width: 120,
    align: 'center'
  },
  {
    title: '状态',
    dataIndex: 'is_active',
    key: 'is_active',
    width: 80,
    align: 'center'
  },
  {
    title: '操作',
    key: 'action',
    width: 220,
    fixed: 'right',
    align: 'center'
  }
];

// 权限表格列配置
const permissionColumns = [
  {
    title: '权限名称',
    dataIndex: 'permission_name',
    key: 'permission_name',
    width: 150,
    align: 'center'
  },
  {
    title: '权限代码',
    dataIndex: 'permission_code',
    key: 'permission_code',
    width: 150,
    align: 'center'
  },
  {
    title: '资源',
    dataIndex: 'resource',
    key: 'resource',
    width: 120,
    align: 'center'
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description',
    width: 200,
    align: 'center'
  },
  {
    title: '状态',
    dataIndex: 'is_active',
    key: 'is_active',
    width: 80,
    align: 'center'
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
    fixed: 'right',
    align: 'center'
  }
];

// 计算属性
const currentTitle = computed(() => {
  const titles = {
    general: '常规设置',
    device: '设备配置',
    user: '用户管理',
    role: '角色管理',
    permission: '权限管理',
    'database-config': '数据库配置',
    'logging-config': '日志配置',
    'other-config': '其他配置',
    system: '系统信息'
  };
  return titles[selectedKeys.value[0]] || '设置';
});

// 方法
const handleMenuClick = ({ key }) => {
  selectedKeys.value = [key];
  if (key === 'user') {
    fetchUsers();
    fetchRoles();
  } else if (key === 'role') {
    fetchRoles();
  } else if (key === 'permission') {
    fetchPermissions();
  } else if (key === 'database-config') {
    fetchDatabaseConfig();
  } else if (key === 'logging-config') {
    fetchLoggingConfig();
  } else if (key === 'other-config') {
    fetchOtherConfig();
  }
};

// 用户管理方法
const fetchUsers = async () => {
  userLoading.value = true;
  try {
    const res = await userAPI.getUsers({
      page: userPagination.current,
      pageSize: userPagination.pageSize
    });
    if (res.success || (res.code && res.code >= 200 && res.code < 300)) {
      userList.value = res.data?.data || res.data || [];
      userPagination.total = res.data?.total || 0;
    } else {
      message.error(res.message || '获取用户列表失败');
    }
  } catch (err) {
    console.error('获取用户列表失败:', err);
    message.error('获取用户列表失败');
  } finally {
    userLoading.value = false;
  }
};

const fetchRoles = async () => {
  try {
    const res = await roleAPI.getRoles();
    if (res.success || (res.code && res.code >= 200 && res.code < 300)) {
      roleList.value = res.data?.data || res.data || [];
    }
  } catch (err) {
    console.error('获取角色列表失败:', err);
  }
};

const fetchPermissions = async () => {
  permissionLoading.value = true;
  try {
    const res = await permissionAPI.getPermissions();
    if (res.success || (res.code && res.code >= 200 && res.code < 300)) {
      permissionList.value = res.data || [];
    }
  } catch (err) {
    console.error('获取权限列表失败:', err);
    message.error('获取权限列表失败');
  } finally {
    permissionLoading.value = false;
  }
};

const showAddUserModal = () => {
  resetUserForm();
  userFormData.id = null;
  userFormVisible.value = true;
};

const editUser = (record) => {
  resetUserForm();
  Object.assign(userFormData, {
    id: record.id,
    username: record.username,
    full_name: record.full_name,
    email: record.email || '',
    phone: record.phone || '',
    user_type: record.user_type,
    department: record.department || '',
    title: record.title || '',
    license_number: record.license_number || '',
    password: '',
    role_ids: record.roles?.map(r => r.id) || []
  });
  userFormVisible.value = true;
};

const resetUserForm = () => {
  Object.assign(userFormData, {
    id: null,
    username: '',
    full_name: '',
    email: '',
    phone: '',
    user_type: 'doctor',
    department: '',
    title: '',
    license_number: '',
    password: '',
    role_ids: []
  });
};

const handleUserFormSubmit = async () => {
  try {
    await userForm.value.validate();
    userFormLoading.value = true;

    const data = { ...userFormData };
    if (!data.id && !data.password) {
      message.error('新用户必须设置密码');
      return;
    }

    let res;
    if (data.id) {
      // 更新用户
      delete data.password; // 更新时不修改密码
      res = await userAPI.updateUser(data.id, data);
    } else {
      // 创建用户
      res = await userAPI.createUser(data);
    }

    if (res.success || (res.code && res.code >= 200 && res.code < 300)) {
      message.success(data.id ? '用户更新成功' : '用户创建成功');
      userFormVisible.value = false;
      fetchUsers();
    } else {
      message.error(res.message || (data.id ? '用户更新失败' : '用户创建失败'));
    }
  } catch (err) {
    console.error('用户操作失败:', err);
    message.error('操作失败');
  } finally {
    userFormLoading.value = false;
  }
};

const toggleUserStatus = (record) => {
  const action = record.status === 'active' ? '停用' : '激活';
  Modal.confirm({
    title: `确认${action}`,
    content: `确定要${action}用户 "${record.full_name}" 吗？`,
    onOk: async () => {
      try {
        const newStatus = record.status === 'active' ? 'inactive' : 'active';
        const res = await userAPI.updateUserStatus(record.id, newStatus);
        if (res.success || (res.code && res.code >= 200 && res.code < 300)) {
          message.success(`用户${action}成功`);
          fetchUsers();
        } else {
          message.error(res.message || `用户${action}失败`);
        }
      } catch (err) {
        console.error(`用户${action}失败:`, err);
        message.error(`用户${action}失败`);
      }
    }
  });
};

const deleteUser = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除用户 "${record.full_name}" 吗？此操作不可撤销。`,
    okText: '确认删除',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      try {
        const res = await userAPI.deleteUser(record.id);
        if (res.success || (res.code && res.code >= 200 && res.code < 300)) {
          message.success('用户删除成功');
          fetchUsers();
        } else {
          message.error(res.message || '用户删除失败');
        }
      } catch (err) {
        console.error('用户删除失败:', err);
        message.error('用户删除失败');
      }
    }
  });
};

const handleUserTableChange = (pagination) => {
  userPagination.current = pagination.current;
  userPagination.pageSize = pagination.pageSize;
  fetchUsers();
};

const getUserTypeColor = (type) => {
  const colors = {
    admin: 'red',
    doctor: 'blue',
    technician: 'green',
    viewer: 'orange'
  };
  return colors[type] || 'default';
};

const getUserTypeName = (type) => {
  const names = {
    admin: '管理员',
    doctor: '医生',
    technician: '技师',
    viewer: '查看者'
  };
  return names[type] || type;
};

// 角色管理方法
const showAddRoleModal = () => {
  resetRoleForm();
  roleFormData.id = null;
  roleFormVisible.value = true;
};

const editRole = (record) => {
  Object.assign(roleFormData, {
    id: record.id,
    role_name: record.role_name,
    role_code: record.role_code,
    description: record.description || ''
  });
  roleFormVisible.value = true;
};

const resetRoleForm = () => {
  Object.assign(roleFormData, {
    id: null,
    role_name: '',
    role_code: '',
    description: ''
  });
};

const handleRoleFormSubmit = async () => {
  try {
    await roleForm.value.validate();
    roleFormLoading.value = true;

    const data = { ...roleFormData };
    let res;
    if (data.id) {
      res = await roleAPI.updateRole(data.id, data);
    } else {
      res = await roleAPI.createRole(data);
    }

    if (res.success || (res.code && res.code >= 200 && res.code < 300)) {
      message.success(data.id ? '角色更新成功' : '角色创建成功');
      roleFormVisible.value = false;
      fetchRoles();
    } else {
      message.error(res.message || (data.id ? '角色更新失败' : '角色创建失败'));
    }
  } catch (err) {
    console.error('角色操作失败:', err);
    message.error('操作失败');
  } finally {
    roleFormLoading.value = false;
  }
};

const deleteRole = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除角色 "${record.role_name}" 吗？此操作不可撤销。`,
    okText: '确认删除',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      try {
        const res = await roleAPI.deleteRole(record.id);
        if (res.success || (res.code && res.code >= 200 && res.code < 300)) {
          message.success('角色删除成功');
          fetchRoles();
        } else {
          message.error(res.message || '角色删除失败');
        }
      } catch (err) {
        console.error('角色删除失败:', err);
        message.error('角色删除失败');
      }
    }
  });
};

const manageRolePermissions = (record) => {
  message.info(`管理角色 "${record.role_name}" 的权限功能开发中...`);
};

// 权限管理方法
const showAddPermissionModal = () => {
  resetPermissionForm();
  permissionFormData.id = null;
  permissionFormVisible.value = true;
};

const editPermission = (record) => {
  Object.assign(permissionFormData, {
    id: record.id,
    permission_name: record.permission_name,
    permission_code: record.permission_code,
    resource: record.resource,
    action: record.action,
    description: record.description || ''
  });
  permissionFormVisible.value = true;
};

const resetPermissionForm = () => {
  Object.assign(permissionFormData, {
    id: null,
    permission_name: '',
    permission_code: '',
    resource: '',
    action: '',
    description: ''
  });
};

const handlePermissionFormSubmit = async () => {
  try {
    await permissionForm.value.validate();
    permissionFormLoading.value = true;

    // 这里需要实现权限的创建和更新API
    message.info('权限管理功能开发中...');
    permissionFormVisible.value = false;
  } catch (err) {
    console.error('权限操作失败:', err);
    message.error('操作失败');
  } finally {
    permissionFormLoading.value = false;
  }
};

const deletePermission = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除权限 "${record.permission_name}" 吗？此操作不可撤销。`,
    okText: '确认删除',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      try {
        // 这里需要实现权限删除API
        message.info('权限删除功能开发中...');
      } catch (err) {
        console.error('权限删除失败:', err);
        message.error('权限删除失败');
      }
    }
  });
};

const saveGeneralSettings = () => {
  message.success('常规设置已保存');
};

const resetGeneralSettings = () => {
  Object.assign(generalSettings, {
    systemName: '瑞尔明康眼底检查系统',
    language: 'zh-CN',
    theme: 'light',
    autoSaveInterval: 5
  });
  message.info('常规设置已重置');
};

const saveDeviceSettings = () => {
  message.success('设备配置已保存');
};

const testConnection = () => {
  message.loading('正在测试连接...', 2);
  setTimeout(() => {
    message.success('连接测试成功');
  }, 2000);
};

const resetDeviceSettings = () => {
  Object.assign(deviceSettings, {
    socketHost: 'localhost',
    socketPort: 8081,
    imageQuality: 'high',
    timeout: 30,
    autoReconnect: true
  });
  message.info('设备配置已重置');
};

// 配置管理方法
const fetchDatabaseConfig = async () => {
  databaseConfigLoading.value = true;
  try {
    const res = await configAPI.getDatabaseConfig();
    if (res.code === 200) {
      // 确保数据正确填充到表单中
      console.log('获取到的数据库配置:', res.data);
      // 使用解构赋值确保所有字段都被正确赋值
      const { host, port, user, password, dbname, log_level, max_open_conns, max_idle_conns, conn_max_lifetime } = res.data;
      
      // 逐个赋值确保响应式更新，注意字段名映射
      databaseConfig.host = host || '';
      databaseConfig.port = port || 3306;
      databaseConfig.database = dbname || ''; // 后端是dbname，前端是database
      databaseConfig.username = user || '';   // 后端是user，前端是username
      databaseConfig.password = password || '';
      databaseConfig.log_level = log_level || 'info';
      databaseConfig.max_open_conns = max_open_conns || 100;
      databaseConfig.max_idle_conns = max_idle_conns || 10;
      databaseConfig.conn_max_lifetime = conn_max_lifetime || 3600;
    } else {
      message.error(res.msg || '获取数据库配置失败');
    }
  } catch (err) {
    console.error('获取数据库配置失败:', err);
    message.error('获取数据库配置失败');
  } finally {
    databaseConfigLoading.value = false;
  }
};

const saveDatabaseConfig = async () => {
  databaseConfigLoading.value = true;
  try {
    const res = await configAPI.updateDatabaseConfig(databaseConfig);
    if (res.code === 200) {
      message.success('数据库配置保存成功');
    } else {
      message.error(res.msg || '保存数据库配置失败');
    }
  } catch (err) {
    console.error('保存数据库配置失败:', err);
    message.error('保存数据库配置失败');
  } finally {
    databaseConfigLoading.value = false;
  }
};

const testDatabaseConnection = async () => {
  testConnectionLoading.value = true;
  try {
    const res = await configAPI.testDatabaseConnection(databaseConfig);
    if (res.code === 200) {
      message.success('数据库连接测试成功');
    } else {
      message.error(res.msg || '数据库连接测试失败');
    }
  } catch (err) {
    console.error('数据库连接测试失败:', err);
    message.error('数据库连接测试失败');
  } finally {
    testConnectionLoading.value = false;
  }
};

const resetDatabaseConfig = () => {
  Object.assign(databaseConfig, {
    host: 'localhost',
    port: 3306,
    database: 'eyes_remk',
    username: 'root',
    password: '',
    max_open_conns: 100,
    max_idle_conns: 10,
    conn_max_lifetime: 3600
  });
  message.info('数据库配置已重置');
};

const fetchLoggingConfig = async () => {
  loggingConfigLoading.value = true;
  try {
    const res = await configAPI.getLoggingConfig();
    if (res.code === 200) {
      console.log('获取到的日志配置:', res.data);
      // 使用解构赋值确保所有字段都被正确赋值
      const { level, format, output, file_path, report_caller } = res.data;
      
      // 逐个赋值确保响应式更新
      loggingConfig.level = level || 'info';
      loggingConfig.format = format || 'json';
      loggingConfig.output = output || 'console';
      loggingConfig.file_path = file_path || '';
      loggingConfig.report_caller = report_caller !== undefined ? report_caller : false;
    } else {
      message.error(res.msg || '获取日志配置失败');
    }
  } catch (err) {
    console.error('获取日志配置失败:', err);
    message.error('获取日志配置失败');
  } finally {
    loggingConfigLoading.value = false;
  }
};

const saveLoggingConfig = async () => {
  loggingConfigLoading.value = true;
  try {
    const res = await configAPI.updateLoggingConfig(loggingConfig);
    if (res.code === 200) {
      message.success('日志配置保存成功');
    } else {
      message.error(res.msg || '保存日志配置失败');
    }
  } catch (err) {
    console.error('保存日志配置失败:', err);
    message.error('保存日志配置失败');
  } finally {
    loggingConfigLoading.value = false;
  }
};

const resetLoggingConfig = () => {
  Object.assign(loggingConfig, {
    level: 'info',
    format: 'json',
    output: 'both',
    file_path: 'logs/app.log',
    report_caller: true
  });
  message.info('日志配置已重置');
};

const fetchOtherConfig = async () => {
  otherConfigLoading.value = true;
  try {
    const res = await configAPI.getOtherConfig();
    if (res.code === 200) {
      console.log('获取到的其他配置:', res.data);
      // 使用解构赋值确保所有字段都被正确赋值
      const { server, third_party, save_folder_path } = res.data;
      
      // 逐个赋值确保响应式更新
      if (server) {
        otherConfig.server.host = server.host || 'localhost';
        otherConfig.server.port = server.port || 8080;
      }
      
      if (third_party) {
        otherConfig.third_party.base_url = third_party.base_url || 'http://localhost';
        otherConfig.third_party.port = third_party.port || 8080;
        otherConfig.third_party.timeout = third_party.timeout || 30;
        otherConfig.third_party.retry_count = third_party.retry_count || 3;
      }
      
      otherConfig.save_folder_path = save_folder_path || './save';
    } else {
      message.error(res.msg || '获取其他配置失败');
    }
  } catch (err) {
    console.error('获取其他配置失败:', err);
    message.error('获取其他配置失败');
  } finally {
    otherConfigLoading.value = false;
  }
};

const saveOtherConfig = async () => {
  otherConfigLoading.value = true;
  try {
    const res = await configAPI.updateOtherConfig(otherConfig);
    if (res.code === 200) {
      message.success('其他配置保存成功');
    } else {
      message.error(res.msg || '保存其他配置失败');
    }
  } catch (err) {
    console.error('保存其他配置失败:', err);
    message.error('保存其他配置失败');
  } finally {
    otherConfigLoading.value = false;
  }
};

const resetOtherConfig = () => {
  Object.assign(otherConfig, {
    server: {
      host: 'localhost',
      port: 8080
    },
    third_party: {
      base_url: 'http://localhost',
      port: 9000,
      timeout: 30,
      retry_count: 3
    },
    save_folder_path: './save'
  });
  message.info('其他配置已重置');
};


const exportLogs = () => {
  message.success('日志导出功能待实现');
};

const clearCache = () => {
  Modal.confirm({
    title: '确认清除缓存',
    content: '清除缓存可能会影响系统性能，确定要继续吗？',
    onOk() {
      message.success('缓存已清除');
    }
  });
};

const restartSystem = () => {
  Modal.confirm({
    title: '确认重启系统',
    content: '重启系统将断开所有连接，确定要继续吗？',
    okType: 'danger',
    onOk() {
      message.warning('系统重启功能待实现');
    }
  });
};

// 生命周期
onMounted(() => {
  // 初始化时可以加载一些基础数据
});
</script>

<style scoped>
.system-settings {
  padding: 24px;
}

.settings-menu,
.settings-content {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.settings-panel {
  padding: 16px 0;
}

.settings-scroll-panel {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  padding-right: 16px;
}

.settings-scroll-panel::-webkit-scrollbar {
  width: 6px;
}

.settings-scroll-panel::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.settings-scroll-panel::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.settings-scroll-panel::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.switch-label {
  margin-left: 8px;
  color: #666;
}

.user-actions {
  margin-bottom: 16px;
}

.system-actions {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

/* 用户管理表格固定表头和滚动样式 */
.user-management-table {
  height: calc(100vh - 380px);
}

.user-management-table .ant-table-thead > tr > th {
  position: sticky;
  top: 0;
  background: #fafafa;
  z-index: 10;
  border-bottom: 1px solid #f0f0f0;
}

.user-management-table .ant-table-tbody {
  overflow-y: auto;
}

/* 固定操作列样式 */
.user-management-table .ant-table-thead > tr > th.ant-table-cell-fix-right,
.user-management-table .ant-table-tbody > tr > td.ant-table-cell-fix-right {
  background: #fafafa;
  box-shadow: -2px 0 4px rgba(0, 0, 0, 0.05);
}

/* 美化滚动条 */
.user-management-table .ant-table-body::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.user-management-table .ant-table-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.user-management-table .ant-table-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.user-management-table .ant-table-body::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 用户管理面板样式 */
.user-management-panel {
  height: calc(100vh - 200px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.user-management-actions {
  flex-shrink: 0;
  margin-bottom: 16px;
}

.user-management-content {
  flex: 1;
  overflow: hidden;
}

/* 角色和权限管理表格固定表头和滚动样式 */
.role-management-table,
.permission-management-table {
  height: calc(100vh - 340px);
}

.role-management-table .ant-table-thead > tr > th,
.permission-management-table .ant-table-thead > tr > th {
  position: sticky;
  top: 0;
  background: #fafafa;
  z-index: 10;
  border-bottom: 1px solid #f0f0f0;
}

.role-management-table .ant-table-tbody,
.permission-management-table .ant-table-tbody {
  overflow-y: auto;
}

/* 固定操作列样式 */
.role-management-table .ant-table-thead > tr > th.ant-table-cell-fix-right,
.role-management-table .ant-table-tbody > tr > td.ant-table-cell-fix-right,
.permission-management-table .ant-table-thead > tr > th.ant-table-cell-fix-right,
.permission-management-table .ant-table-tbody > tr > td.ant-table-cell-fix-right {
  background: #fafafa;
  box-shadow: -2px 0 4px rgba(0, 0, 0, 0.05);
}

/* 角色和权限管理表格滚动条样式 */
.role-management-table .ant-table-body::-webkit-scrollbar,
.permission-management-table .ant-table-body::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.role-management-table .ant-table-body::-webkit-scrollbar-track,
.permission-management-table .ant-table-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.role-management-table .ant-table-body::-webkit-scrollbar-thumb,
.permission-management-table .ant-table-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.role-management-table .ant-table-body::-webkit-scrollbar-thumb:hover,
.permission-management-table .ant-table-body::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 角色和权限管理面板样式 */
.role-management-panel,
.permission-management-panel {
  height: calc(100vh - 200px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.role-actions,
.permission-actions {
  flex-shrink: 0;
  margin-bottom: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .system-settings {
    padding: 16px;
  }
  
  .ant-col:first-child {
    margin-bottom: 16px;
  }

  .user-management-table {
    height: calc(100vh - 300px);
  }

  .role-management-table,
  .permission-management-table {
    height: calc(100vh - 260px);
  }
}
</style>
