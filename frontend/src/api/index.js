import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Projects
export const getProjects = () => api.get('/projects')
export const getProject = (id) => api.get(`/projects/${id}`)
export const createProject = (data) => api.post('/projects', data)
export const updateProject = (id, data) => api.put(`/projects/${id}`, data)
export const deleteProject = (id) => api.delete(`/projects/${id}`)

// Eval Objects
export const getEvalObjects = (projectId) => api.get(`/projects/${projectId}/eval-objects`)
export const createEvalObject = (projectId, data) => api.post(`/projects/${projectId}/eval-objects`, data)
export const updateEvalObject = (projectId, objId, data) => api.put(`/projects/${projectId}/eval-objects/${objId}`, data)
export const deleteEvalObject = (projectId, objId) => api.delete(`/projects/${projectId}/eval-objects/${objId}`)
export const copyRecords = (projectId, targetId, sourceId) => api.post(`/projects/${projectId}/eval-objects/${targetId}/copy-from/${sourceId}`)

// Check Items (Question Bank)
export const getCheckItems = (params) => api.get('/check-items', { params })
export const getCheckItemCount = () => api.get('/check-items/count')
export const createCheckItem = (data) => api.post('/check-items', data)
export const updateCheckItem = (id, data) => api.put(`/check-items/${id}`, data)
export const deleteCheckItem = (id) => api.delete(`/check-items/${id}`)
export const getCategories = (params) => api.get('/check-items/categories', { params })

// Check Records
export const getCheckRecords = (objId, params) => api.get(`/eval-objects/${objId}/records`, { params })
export const updateCheckRecord = (objId, recordId, data) => api.put(`/eval-objects/${objId}/records/${recordId}`, data)
export const uploadAttachment = (objId, recordId, formData) => api.post(`/eval-objects/${objId}/records/${recordId}/attachments`, formData)
export const getAttachments = (objId, recordId) => api.get(`/eval-objects/${objId}/records/${recordId}/attachments`)
export const deleteAttachment = (objId, recordId, attId) => api.delete(`/eval-objects/${objId}/records/${recordId}/attachments/${attId}`)

// Issues
export const getIssues = (projectId) => api.get(`/projects/${projectId}/issues`)
export const createIssue = (projectId, data) => api.post(`/projects/${projectId}/issues`, data)
export const updateIssue = (projectId, issueId, data) => api.put(`/projects/${projectId}/issues/${issueId}`, data)
export const deleteIssue = (projectId, issueId) => api.delete(`/projects/${projectId}/issues/${issueId}`)

// Statistics
export const getStats = (projectId) => api.get(`/projects/${projectId}/stats`)

// Export
export const exportExcel = (projectId) => {
  return api.get(`/projects/${projectId}/export/excel`, { responseType: 'blob' })
}

export default api
