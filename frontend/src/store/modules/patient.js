/**
 * 患者信息状态管理
 */

import { defineStore } from 'pinia';

export const usePatientStore = defineStore('patient', {
  state: () => ({
    // 当前患者信息
    currentPatient: null,
    // 当前检查记录信息
    currentExamination: null,
    // 是否为新检查模式
    isNewExamination: false,
    // 患者信息是否已加载
    isPatientLoaded: false
  }),

  getters: {
    // 获取当前患者信息
    getCurrentPatient: (state) => state.currentPatient,
    
    // 获取当前检查记录信息
    getCurrentExamination: (state) => state.currentExamination,
    
    // 获取患者ID
    getPatientId: (state) => state.currentPatient?.id || null,
    
    // 获取检查记录ID
    getExaminationId: (state) => state.currentExamination?.id || null,
    
    // 获取患者姓名
    getPatientName: (state) => state.currentPatient?.name || '',
    
    // 获取患者编号
    getPatientNumber: (state) => state.currentPatient?.patient_id || '',
    
    // 检查是否有患者信息
    hasPatientInfo: (state) => !!state.currentPatient,
    
    // 检查是否有检查记录信息
    hasExaminationInfo: (state) => !!state.currentExamination,
    
    // 检查是否为新检查模式
    isNewExaminationMode: (state) => state.isNewExamination
  },

  actions: {
    // 设置患者信息
    setPatientInfo(patientInfo) {
      this.currentPatient = patientInfo;
      this.isPatientLoaded = true;
      console.log('患者信息已设置:', patientInfo);
    },
    
    // 设置检查记录信息
    setExaminationInfo(examinationInfo) {
      this.currentExamination = examinationInfo;
      console.log('检查记录信息已设置:', examinationInfo);
    },
    
    // 设置新检查模式
    setNewExaminationMode(isNew) {
      this.isNewExamination = isNew;
      console.log('新检查模式已设置:', isNew);
    },
    
    // 设置完整的患者和检查信息
    setPatientAndExamination(patientInfo, examinationInfo, isNewExamination = false) {
      this.currentPatient = patientInfo;
      this.currentExamination = examinationInfo;
      this.isNewExamination = isNewExamination;
      this.isPatientLoaded = true;
      console.log('患者和检查信息已设置:', { patientInfo, examinationInfo, isNewExamination });
    },
    
    // 清除患者信息
    clearPatientInfo() {
      this.currentPatient = null;
      this.currentExamination = null;
      this.isNewExamination = false;
      this.isPatientLoaded = false;
      console.log('患者信息已清除');
    },
    
    // 更新患者信息
    updatePatientInfo(updates) {
      if (this.currentPatient) {
        this.currentPatient = { ...this.currentPatient, ...updates };
        console.log('患者信息已更新:', this.currentPatient);
      }
    },
    
    // 更新检查记录信息
    updateExaminationInfo(updates) {
      if (this.currentExamination) {
        this.currentExamination = { ...this.currentExamination, ...updates };
        console.log('检查记录信息已更新:', this.currentExamination);
      }
    },
    
    // 从URL参数设置患者信息
    setPatientFromUrlParams(params) {
      const patientInfo = {
        id: params.patientId ? parseInt(params.patientId) : null,
        patient_id: params.patientNumber || '',
        name: params.patientName || '',
        gender: params.gender || '',
        age: params.age || null
      };
      
      const examinationInfo = {
        id: params.examinationId ? parseInt(params.examinationId) : null,
        examination_type_id: params.examinationTypeId ? parseInt(params.examinationTypeId) : null,
        examination_type: params.examinationType || '',
        department: params.department || '',
        doctor_id: params.doctorId ? parseInt(params.doctorId) : null,
        doctor_name: params.doctorName || '',
        scheduled_date: params.scheduledDate || '',
        scheduled_time: params.scheduledTime || '',
        priority: params.priority || '',
        notes: params.notes || ''
      };
      
      this.setPatientAndExamination(patientInfo, examinationInfo, params.mode === 'new_examination');
    },
    
    // 保存到本地存储
    saveToLocalStorage() {
      if (typeof window === 'undefined') return;
      
      const patientData = {
        currentPatient: this.currentPatient,
        currentExamination: this.currentExamination,
        isNewExamination: this.isNewExamination,
        isPatientLoaded: this.isPatientLoaded,
        timestamp: Date.now()
      };
      
      try {
        localStorage.setItem('eyes_remk_patient', JSON.stringify(patientData));
        console.log('患者信息已保存到本地存储');
      } catch (error) {
        console.error('保存患者信息到本地存储失败:', error);
      }
    },
    
    // 从本地存储加载
    loadFromLocalStorage() {
      if (typeof window === 'undefined') return false;
      
      try {
        const stored = localStorage.getItem('eyes_remk_patient');
        if (stored) {
          const patientData = JSON.parse(stored);
          
          // 检查数据是否过期（24小时）
          const maxAge = 24 * 60 * 60 * 1000; // 24小时
          if (Date.now() - patientData.timestamp < maxAge) {
            this.currentPatient = patientData.currentPatient;
            this.currentExamination = patientData.currentExamination;
            this.isNewExamination = patientData.isNewExamination;
            this.isPatientLoaded = patientData.isPatientLoaded;
            
            console.log('患者信息已从本地存储加载');
            return true;
          } else {
            // 数据过期，清除存储
            this.clearLocalStorage();
          }
        }
      } catch (error) {
        console.error('从本地存储加载患者信息失败:', error);
        this.clearLocalStorage();
      }
      
      return false;
    },
    
    // 清除本地存储
    clearLocalStorage() {
      if (typeof window === 'undefined') return;
      
      try {
        localStorage.removeItem('eyes_remk_patient');
        console.log('患者信息本地存储已清除');
      } catch (error) {
        console.error('清除患者信息本地存储失败:', error);
      }
    },
    
    // 初始化患者状态
    initializePatientState() {
      return this.loadFromLocalStorage();
    }
  }
});
