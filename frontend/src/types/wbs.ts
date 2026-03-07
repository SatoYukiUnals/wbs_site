export interface WBSItem {
  id: number
  title: string
  description: string
  status: 'not_started' | 'in_progress' | 'completed' | 'on_hold'
  status_display: string
  priority: 1 | 2 | 3
  priority_display: string
  assignee: string
  start_date: string | null
  end_date: string | null
  progress: number
  parent: number | null
  order: number
  children: WBSItem[]
  created_at: string
  updated_at: string
}

export type WBSItemCreate = Omit<WBSItem, 'id' | 'status_display' | 'priority_display' | 'children' | 'created_at' | 'updated_at'>

export type WBSItemUpdate = Partial<WBSItemCreate>
