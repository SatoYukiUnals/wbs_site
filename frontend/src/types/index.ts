// アプリケーション全体で使用する型定義

/** ユーザーロール */
export type UserRole = 'master' | 'admin' | 'member'

/** タスクステータス */
export type TaskStatus = 'Todo' | 'InProgress' | 'InReview' | 'Done' | 'OnHold'

/** 優先度 */
export type Priority = '高' | '中' | '低'

/** レビューステータス */
export type ReviewStatus = 'pending' | 'approved' | 'rejected' | '確認待ち' | '完了'

/** ロードマップアイテムステータス */
export type RoadmapStatus = '計画中' | '進行中' | '完了' | '保留'

/** テンプレート種別 */
export type TemplateType = 'wbs' | 'task'

/** ガントチャート表示単位 */
export type ViewUnit = 'month' | 'week' | 'quarter'

/** タスク種別 */
export type TaskType = 'item' | 'task'

/** タスク作業種別 */
export type TaskKind = '実装' | 'ドキュメント作成' | 'レビュー依頼' | 'レビュー修正'

/** テナント */
export interface Tenant {
  id: string
  name: string
}

/** ユーザー */
export interface User {
  id: string
  email: string
  display_name: string
  role: UserRole
  tenant_id: string
}

/** プロジェクト */
export interface Project {
  id: string
  name: string
  description: string
  start_date: string
  end_date: string
  progress: number
  tenant_id: string
}

/** プロジェクトメンバー */
export interface ProjectMember {
  id: string
  user_id: string
  user_name: string
  email: string
  role: UserRole
  project_id: string
}

/** クォーター */
export interface Quarter {
  id: string
  title: string
  start_date: string
  end_date: string
  progress: number
  project_id: string
}

/** タスク */
export interface Task {
  id: string
  title: string
  description: string
  /** 'item'=項目（親ノード）/ 'task'=タスク（リーフ） */
  task_type: TaskType
  status: TaskStatus
  /** 同一親内での並び順（wbs_noの末尾番号と一致） */
  sort_order: number
  progress: number
  start_date: string | null
  end_date: string | null
  actual_start_date: string | null
  actual_end_date: string | null
  estimated_hours: number | null
  quarter_id: string | null
  parent_task_id: string | null
  project_id: string
  wbs_no: string
  /** 実装者（項目の場合）または担当者（タスクの場合） */
  assignees: { id: string; name: string }[]
  /** タスク作業種別（task のみ設定可） */
  task_kind: TaskKind | null
  /** TMレビュー担当者（項目のみ） */
  tm_reviewer: { id: string; name: string } | null
  /** PJレビュー担当者（項目のみ） */
  pj_reviewer: { id: string; name: string } | null
  children?: Task[]
  depth: number
}

/** レビュー */
export interface Review {
  id: string
  task_id: string
  task_title: string
  status: ReviewStatus
  reviewer_id: string | null
  reviewer_name: string | null
  created_at: string
  updated_at: string
}

/** レビューコメント */
export interface ReviewComment {
  id: string
  review_id: string
  body: string
  author_id: string
  author_name: string
  created_at: string
}

/** レビュー履歴 */
export interface ReviewHistory {
  id: string
  review_id: string
  action: string
  user_id: string
  user_name: string
  created_at: string
}

/** ロードマップアイテム */
export interface RoadmapItem {
  id: string
  title: string
  description: string
  quarter_id: string
  quarter_title: string
  status: RoadmapStatus
  project_id: string
}

/** 報告書セクション */
export interface ReportSections {
  overview: string
  summary: string
  quarters: string
  tasks: string
  delayed: string
  reviews: string
}

/** テンプレート */
export interface Template {
  id: string
  title: string
  type: TemplateType
  content: string
  is_shared: boolean
  created_by: string
  created_by_name: string
}

/** 自動割り振りプレビュー結果 */
export interface AutoAssignPreview {
  task_id: string
  task_title: string
  assignee_id: string
  assignee_name: string
}

/** ダッシュボード・プロジェクトサマリー */
export interface ProjectSummary {
  id: string
  name: string
  progress: number
  status_counts: {
    Todo: number
    InProgress: number
    Done: number
    InReview: number
    OnHold: number
  }
  delayed_count: number
}

/** ダッシュボード・自分のタスク */
export interface MyTask {
  id: string
  title: string
  project_id: string
  project_name: string
  status: TaskStatus
  progress: number
  end_date: string | null
}
