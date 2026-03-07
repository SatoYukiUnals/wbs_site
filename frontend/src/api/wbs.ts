import axios from 'axios'
import type { WBSItem, WBSItemCreate, WBSItemUpdate } from '../types/wbs'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const wbsApi = {
  getAll: () => apiClient.get<WBSItem[]>('/wbs/'),
  getById: (id: number) => apiClient.get<WBSItem>(`/wbs/${id}/`),
  create: (data: WBSItemCreate) => apiClient.post<WBSItem>('/wbs/', data),
  update: (id: number, data: WBSItemUpdate) => apiClient.put<WBSItem>(`/wbs/${id}/`, data),
  patch: (id: number, data: WBSItemUpdate) => apiClient.patch<WBSItem>(`/wbs/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/wbs/${id}/`),
}
