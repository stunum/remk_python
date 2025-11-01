import request from '@/utils/request';

/**
 * 获取检查的诊断记录
 * @param {number} examinationId - 检查ID
 */
export function getDiagnosisRecord(examinationId) {
  return request({
    url: '/diagnosis/record',
    method: 'get',
    params: {
      examination_id: examinationId
    }
  });
}

/**
 * 保存或更新诊断记录
 * @param {Object} data - 诊断记录数据
 */
export function saveDiagnosisRecord(data) {
  return request({
    url: '/diagnosis/record',
    method: 'post',
    data
  });
}

/**
 * 删除诊断记录
 * @param {number} id - 诊断记录ID
 */
export function deleteDiagnosisRecord(id) {
  return request({
    url: `/diagnosis/record/${id}`,
    method: 'delete'
  });
}

/**
 * 获取AI诊断结果列表
 * @param {number} examinationId - 检查ID
 */
export function getAIDiagnoses(examinationId) {
  return request({
    url: '/diagnosis/ai',
    method: 'get',
    params: {
      examination_id: examinationId
    }
  });
}

/**
 * 执行AI诊断
 * @param {Object} data - AI诊断请求数据
 * @param {number} data.image_id - 图像ID
 */
export function performAIDiagnosis(data) {
  return request({
    url: '/diagnosis/ai/analyze',
    method: 'post',
    data
  });
}

