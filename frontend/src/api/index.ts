// API クライアント（JWT 認証付き axios ラッパー）
import axios from 'axios'
import type {
  User, Project, Quarter, Task, Review, ReviewComment, ReviewHistory,
  Template, AutoAssignPreview, ProjectMember, UserRole,
  WorkingHourSetting, UserPto,
} from '@/types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

// ---- トークン管理 --------------------------------------------------------

export const getToken = (): string | null => localStorage.getItem('access_token')
export const setTokens = (access: string, refresh: string): void => {
  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
}
export const clearTokens = (): void => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

// ---- axios インスタンス --------------------------------------------------

const http = axios.create({ baseURL: BASE_URL })

// リクエストインターセプター: Authorization ヘッダーを追加
http.interceptors.request.use(cfg => {
  const token = getToken()
  if (token) cfg.headers['Authorization'] = `Bearer ${token}`
  return cfg
})

// レスポンスインターセプター: 401 時にログイン画面へリダイレクト
http.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      clearTokens()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

// ---- アダプター ---------------------------------------------------------

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ApiUser = Record<string, any>

export const adaptUser = (u: ApiUser): User => ({
  id: u.id,
  email: u.email,
  display_name: u.username,
  role: u.role,
  tenant_id: u.tenant,
})

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ApiProject = Record<string, any>

export const adaptProject = (p: ApiProject): Project => ({
  id: p.id,
  name: p.name,
  description: p.description ?? '',
  progress: p.progress ?? 0,
  tenant_id: p.tenant,
  pj_reviewer_id: p.pj_reviewer ?? null,
  pj_reviewer_name: p.pj_reviewer_name ?? null,
})

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ApiQuarter = Record<string, any>

export const adaptQuarter = (q: ApiQuarter): Quarter => ({
  id: q.id,
  title: q.title,
  start_date: q.start_date,
  end_date: q.end_date,
  progress: q.progress ?? 0,
  project_id: q.project,
})

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ApiTask = Record<string, any>

export const adaptTask = (t: ApiTask): Task => ({
  id: t.id,
  title: t.title,
  description: t.description ?? '',
  task_type: t.task_type,
  status: t.status,
  sort_order: t.order ?? 0,
  progress: t.progress ?? 0,
  start_date: t.start_date ?? null,
  end_date: t.end_date ?? null,
  actual_start_date: t.actual_start_date ?? null,
  actual_end_date: t.actual_end_date ?? null,
  estimated_hours: t.estimated_hours != null ? parseFloat(t.estimated_hours) : null,
  quarter_id: t.quarter ?? null,
  parent_task_id: t.parent_task ?? null,
  project_id: t.project,
  wbs_no: t.wbs_no,
  // API の assignees: [{id, task, user, user_info}] → {id: user_id, name: username}
  assignees: (t.assignees ?? []).map((a: ApiUser) => ({
    id: a.user as string,
    name: (a.user_info?.username ?? '') as string,
  })),
  task_kind: t.task_kind ?? null,
  dates_manual: t.dates_manual ?? false,
  tm_reviewer: t.tm_reviewer
    ? { id: t.tm_reviewer, name: t.tm_reviewer_name ?? '' }
    : null,
  children: (t.children ?? []).map(adaptTask),
  depth: t.depth ?? 0,
})

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ApiMember = Record<string, any>

export const adaptMember = (m: ApiMember): ProjectMember => ({
  id: m.id,
  user_id: m.user,
  user_name: m.user_info?.username ?? '',
  email: m.user_info?.email ?? '',
  role: m.role,
  project_id: m.project,
})

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ApiTemplate = Record<string, any>

export const adaptTemplate = (t: ApiTemplate): Template => ({
  id: t.id,
  title: t.title,
  type: t.type,
  content: t.content,
  is_shared: t.is_shared,
  created_by: t.created_by,
  created_by_name: t.created_by_name ?? '',
})

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ApiReview = Record<string, any>

export const adaptReview = (r: ApiReview): Review => ({
  id: r.id,
  task_id: r.task,
  task_title: r.task_title ?? '',
  status: r.status,
  reviewer_id: r.reviewer ?? null,
  reviewer_name: r.reviewer_name ?? null,
  created_at: r.created_at,
  updated_at: r.updated_at ?? r.created_at,
})

// ---- API 関数 -----------------------------------------------------------

export const api = {
  auth: {
    /** ログイン → アクセストークンとユーザー情報を返す */
    login: async (email: string, password: string): Promise<{ user: User; access: string; refresh: string }> => {
      const { data } = await http.post('/auth/login/', { email, password })
      return { user: adaptUser(data.user), access: data.access, refresh: data.refresh }
    },

    /** 現在ログイン中のユーザー情報を取得 */
    getProfile: async (): Promise<User> => {
      const { data } = await http.get('/auth/profile/')
      return adaptUser(data)
    },

    /** プロフィール更新 */
    updateProfile: async (username: string): Promise<User> => {
      const { data } = await http.patch('/auth/profile/', { username })
      return adaptUser(data)
    },

    /** テナント内のユーザー一覧を取得 */
    listUsers: async (): Promise<User[]> => {
      const { data } = await http.get('/auth/users/')
      return (data as ApiUser[]).map(adaptUser)
    },

    /** ユーザーロール更新 */
    updateUserRole: async (userId: string, role: UserRole): Promise<void> => {
      await http.patch(`/auth/users/${userId}/role/`, { role })
    },

    /** ユーザー直接登録（master のみ） */
    createUser: async (payload: {
      username: string
      email: string
      password: string
      role: UserRole
    }): Promise<User> => {
      const { data } = await http.post('/auth/users/create/', payload)
      return adaptUser(data)
    },

    /** ユーザー情報更新（master のみ・表示名・メール・ロール・パスワード） */
    updateUser: async (
      userId: string,
      payload: {
        username?: string
        email?: string
        role?: UserRole
        password?: string
      },
    ): Promise<User> => {
      // password が空なら送信しない
      const body: Record<string, unknown> = { ...payload }
      if (!body.password) delete body.password
      const { data } = await http.patch(`/auth/users/${userId}/`, body)
      return adaptUser(data)
    },

    /** ユーザー削除 */
    deleteUser: async (userId: string): Promise<void> => {
      await http.delete(`/auth/users/${userId}/`)
    },

    /** ユーザー招待 */
    invite: async (email: string, role: UserRole): Promise<{
      email: string; role: UserRole; token: string; expires_at: string
    }> => {
      const { data } = await http.post('/auth/users/invite/', { email, role })
      return data
    },

    /** テナント新規登録（認証不要・初期 master ユーザーも作成） */
    registerTenant: async (payload: {
      tenant_name: string
      email: string
      username: string
      password: string
    }): Promise<{ user: User; access: string; refresh: string }> => {
      const { data } = await http.post('/auth/register/tenant/', payload)
      return {
        user: adaptUser(data.user),
        access: data.access,
        refresh: data.refresh,
      }
    },

    /** テナント情報を取得 */
    getTenant: async (): Promise<{
      id: string
      name: string
      holiday_weekdays: number[]
    }> => {
      const { data } = await http.get('/auth/tenant/')
      return {
        id: data.id,
        name: data.name,
        holiday_weekdays: data.holiday_weekdays ?? [],
      }
    },

    /** テナント情報を更新（master のみ） */
    updateTenant: async (
      payload: { name?: string; holiday_weekdays?: number[] },
    ): Promise<{ id: string; name: string; holiday_weekdays: number[] }> => {
      const { data } = await http.patch('/auth/tenant/', payload)
      return {
        id: data.id,
        name: data.name,
        holiday_weekdays: data.holiday_weekdays ?? [],
      }
    },

    /** 会社休日（テナント休日）一覧 */
    listTenantHolidays: async (): Promise<
      { id: string; date: string; name: string }[]
    > => {
      const { data } = await http.get('/auth/tenant/holidays/')
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (data as any[]).map(d => ({
        id: d.id, date: d.date, name: d.name ?? '',
      }))
    },

    /** 会社休日を追加 */
    addTenantHoliday: async (
      date: string, name = '',
    ): Promise<{ id: string; date: string; name: string }> => {
      const { data } = await http.post(
        '/auth/tenant/holidays/', { date, name },
      )
      return { id: data.id, date: data.date, name: data.name ?? '' }
    },

    /** 会社休日を削除 */
    removeTenantHoliday: async (date: string): Promise<void> => {
      await http.delete(`/auth/tenant/holidays/?date=${date}`)
    },
  },

  projects: {
    /** プロジェクト一覧 */
    list: async (): Promise<Project[]> => {
      const { data } = await http.get('/projects/')
      return (data as ApiProject[]).map(adaptProject)
    },

    /** プロジェクト詳細 */
    get: async (projectId: string): Promise<Project> => {
      const { data } = await http.get(`/projects/${projectId}/`)
      return adaptProject(data)
    },

    /** プロジェクト作成 */
    create: async (payload: { name: string; description?: string }): Promise<Project> => {
      const { data } = await http.post('/projects/', payload)
      return adaptProject(data)
    },

    /** プロジェクト更新（name / description / pj_reviewer など） */
    update: async (
      projectId: string,
      payload: Record<string, unknown>,
    ): Promise<Project> => {
      const { data } = await http.patch(`/projects/${projectId}/`, payload)
      return adaptProject(data)
    },

    /** プロジェクト削除 */
    delete: async (projectId: string): Promise<void> => {
      await http.delete(`/projects/${projectId}/`)
    },

    /** メンバー一覧 */
    listMembers: async (projectId: string): Promise<ProjectMember[]> => {
      const { data } = await http.get(`/projects/${projectId}/members/`)
      return (data as ApiMember[]).map(adaptMember)
    },

    /** メンバー追加 */
    addMember: async (projectId: string, userId: string, role: UserRole): Promise<ProjectMember> => {
      const { data } = await http.post(`/projects/${projectId}/members/`, { user: userId, role })
      return adaptMember(data)
    },

    /** メンバー削除 */
    removeMember: async (projectId: string, userId: string): Promise<void> => {
      await http.delete(`/projects/${projectId}/members/${userId}/`)
    },
  },

  quarters: {
    /** クォーター一覧 */
    list: async (projectId: string): Promise<Quarter[]> => {
      const { data } = await http.get(`/projects/${projectId}/quarters/`)
      return (data as ApiQuarter[]).map(adaptQuarter)
    },

    /** クォーター作成 */
    create: async (projectId: string, payload: { title: string; start_date?: string; end_date?: string }): Promise<Quarter> => {
      const { data } = await http.post(`/projects/${projectId}/quarters/`, payload)
      return adaptQuarter(data)
    },

    /** クォーター更新 */
    update: async (projectId: string, quarterId: string, payload: { title?: string; start_date?: string; end_date?: string }): Promise<Quarter> => {
      const { data } = await http.patch(`/projects/${projectId}/quarters/${quarterId}/`, payload)
      return adaptQuarter(data)
    },

    /** クォーター削除 */
    delete: async (projectId: string, quarterId: string): Promise<void> => {
      await http.delete(`/projects/${projectId}/quarters/${quarterId}/`)
    },
  },

  tasks: {
    /** タスクツリー（ルートのみ、children に子を再帰的に含む） */
    list: async (projectId: string, params?: { status?: string; assignee?: string; quarter?: string }): Promise<Task[]> => {
      const { data } = await http.get(`/projects/${projectId}/tasks/`, { params })
      return (data as ApiTask[]).map(adaptTask)
    },

    /** タスク詳細 */
    get: async (projectId: string, taskId: string): Promise<Task> => {
      const { data } = await http.get(`/projects/${projectId}/tasks/${taskId}/`)
      return adaptTask(data)
    },

    /** タスク更新 */
    update: async (projectId: string, taskId: string, payload: Record<string, unknown>): Promise<Task> => {
      const { data } = await http.patch(`/projects/${projectId}/tasks/${taskId}/`, payload)
      return adaptTask(data)
    },

    /**
     * タスクを一括作成する。
     * 1件ごとに parent_task / task_type / quarter を個別指定できるリッチペイロードを受け取る。
     */
    bulkCreate: async (
      projectId: string,
      items: Array<{
        title: string
        parent_task?: string | null
        quarter?: string | null
        task_type?: string
        status?: string
        progress?: number
      }>,
    ): Promise<Task[]> => {
      const payload = items.map(it => {
        const o: Record<string, unknown> = { title: it.title }
        if (it.quarter) o.quarter = it.quarter
        if (it.parent_task) o.parent_task = it.parent_task
        if (it.task_type) o.task_type = it.task_type
        if (it.status) o.status = it.status
        if (it.progress !== undefined) o.progress = it.progress
        return o
      })
      const { data } = await http.post(`/projects/${projectId}/tasks/bulk/`, payload)
      return (data as ApiTask[]).map(adaptTask)
    },

    /** タスク削除 */
    /**
     * タスク削除。
     * mode='cascade': 配下も含めて全て削除（既定）
     * mode='promote': 配下のタスクを 1階層上げてから自身のみ削除
     */
    delete: async (
      projectId: string,
      taskId: string,
      mode: 'cascade' | 'promote' = 'cascade',
    ): Promise<void> => {
      await http.delete(
        `/projects/${projectId}/tasks/${taskId}/?mode=${mode}`,
      )
    },

    /** 担当者を追加する */
    addAssignee: async (projectId: string, taskId: string, userId: string): Promise<void> => {
      await http.post(`/projects/${projectId}/tasks/${taskId}/assignees/`, { user_id: userId })
    },

    /** 担当者を削除する */
    removeAssignee: async (projectId: string, taskId: string, userId: string): Promise<void> => {
      await http.delete(`/projects/${projectId}/tasks/${taskId}/assignees/${userId}/`)
    },
  },

  dashboard: {
    /** ダッシュボードサマリー */
    get: async (): Promise<{ project_count: number; task_summary: { total: number; done: number; in_progress: number; todo: number } }> => {
      const { data } = await http.get('/dashboard/')
      return data
    },
  },

  progress: {
    /** 進捗集計行一覧 */
    get: async (projectId: string): Promise<unknown[]> => {
      const { data } = await http.get(`/projects/${projectId}/progress/`)
      return data.rows ?? []
    },
  },

  recent: {
    /** 直近タスク（overdue / starting_soon / in_progress） */
    get: async (projectId: string): Promise<{ overdue: Task[]; starting_soon: Task[]; in_progress: Task[] }> => {
      const { data } = await http.get(`/projects/${projectId}/recent/`)
      return {
        overdue: (data.overdue ?? []).map(adaptTask),
        starting_soon: (data.starting_soon ?? []).map(adaptTask),
        in_progress: (data.in_progress ?? []).map(adaptTask),
      }
    },
  },

  reviews: {
    /** プロジェクト内の全レビュー一覧 */
    listByProject: async (projectId: string): Promise<Review[]> => {
      const { data } = await http.get(`/projects/${projectId}/reviews/`)
      return (data as ApiReview[]).map(adaptReview)
    },

    /** タスクのレビュー一覧 */
    list: async (projectId: string, taskId: string): Promise<Review[]> => {
      const { data } = await http.get(`/projects/${projectId}/tasks/${taskId}/reviews/`)
      const items = Array.isArray(data) ? data : [data]
      return items.filter(Boolean).map(adaptReview)
    },

    /** レビュー操作履歴 */
    getHistory: async (projectId: string, taskId: string): Promise<ReviewHistory[]> => {
      const { data } = await http.get(`/projects/${projectId}/tasks/${taskId}/reviews/history/`)
      return (data as ApiUser[]).map(h => ({
        id: h.id,
        review_id: h.review,
        action: h.action,
        user_id: h.user,
        user_name: h.user_name ?? '',
        created_at: h.created_at,
      }))
    },

    /** レビューコメント一覧 */
    getComments: async (projectId: string, taskId: string, reviewId: string): Promise<ReviewComment[]> => {
      const { data } = await http.get(`/projects/${projectId}/tasks/${taskId}/reviews/${reviewId}/`)
      return (data.comments ?? []).map((c: ApiUser) => ({
        id: c.id,
        review_id: reviewId,
        body: c.body,
        author_id: c.author,
        author_name: c.author_name ?? '',
        created_at: c.created_at,
      }))
    },

    /** コメント追加 */
    addComment: async (projectId: string, taskId: string, reviewId: string, body: string): Promise<ReviewComment> => {
      const { data } = await http.post(`/projects/${projectId}/tasks/${taskId}/reviews/${reviewId}/`, { body })
      return {
        id: data.id,
        review_id: reviewId,
        body: data.body,
        author_id: data.author,
        author_name: data.author_name ?? '',
        created_at: data.created_at,
      }
    },

    /** 承認 */
    approve: async (projectId: string, taskId: string): Promise<void> => {
      await http.post(`/projects/${projectId}/tasks/${taskId}/reviews/approve/`)
    },

    /** 差し戻し */
    reject: async (projectId: string, taskId: string, comment?: string): Promise<void> => {
      await http.post(`/projects/${projectId}/tasks/${taskId}/reviews/reject/`, { comment })
    },
  },

  templates: {
    /** テンプレート一覧 */
    list: async (): Promise<Template[]> => {
      const { data } = await http.get('/templates/')
      return (data as ApiTemplate[]).map(adaptTemplate)
    },

    /** テンプレート詳細 */
    get: async (templateId: string): Promise<Template> => {
      const { data } = await http.get(`/templates/${templateId}/`)
      return adaptTemplate(data)
    },

    /** テンプレート作成 */
    create: async (payload: { title: string; type: string; content: string; is_shared: boolean }): Promise<Template> => {
      const { data } = await http.post('/templates/', payload)
      return adaptTemplate(data)
    },

    /** テンプレート更新 */
    update: async (templateId: string, payload: { title?: string; content?: string; is_shared?: boolean }): Promise<Template> => {
      const { data } = await http.patch(`/templates/${templateId}/`, payload)
      return adaptTemplate(data)
    },

    /** テンプレート削除 */
    delete: async (templateId: string): Promise<void> => {
      await http.delete(`/templates/${templateId}/`)
    },
  },

  excel: {
    /** Excel ダウンロード（WBS / 直近のタスク / 進捗一覧 の 3 シート） */
    export: async (
      projectId: string,
      params: { quarter_id?: string; start_date?: string; end_date?: string },
    ): Promise<Blob> => {
      const { data } = await http.post(
        `/projects/${projectId}/export/excel/`,
        params,
        { responseType: 'blob' },
      )
      return data as Blob
    },
  },

  autoAssign: {
    /** 自動割り振りプレビュー（日付スケジューラ） */
    preview: async (projectId: string): Promise<AutoAssignPreview> => {
      const { data } = await http.get(
        `/projects/${projectId}/auto-assign/preview/`,
      )
      return data as AutoAssignPreview
    },

    /** 自動割り振り確定 */
    confirm: async (
      projectId: string,
    ): Promise<{ applied?: number; detail?: string; errors?: unknown[] }> => {
      try {
        const { data } = await http.post(
          `/projects/${projectId}/auto-assign/confirm/`,
        )
        return data
      } catch (err) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const e = err as any
        if (e.response?.status === 400) return e.response.data
        throw err
      }
    },
  },

  workingHour: {
    /** 1日あたりの稼働時間設定を取得 */
    get: async (projectId: string): Promise<WorkingHourSetting> => {
      const { data } = await http.get(
        `/projects/${projectId}/working-hour-setting/`,
      )
      return { daily_hours: parseFloat(data.daily_hours) }
    },
    /** 1日あたりの稼働時間設定を更新 */
    update: async (
      projectId: string, dailyHours: number,
    ): Promise<WorkingHourSetting> => {
      const { data } = await http.put(
        `/projects/${projectId}/working-hour-setting/`,
        { daily_hours: dailyHours },
      )
      return { daily_hours: parseFloat(data.daily_hours) }
    },
  },

  pto: {
    /** 有休一覧 */
    list: async (projectId: string): Promise<UserPto[]> => {
      const { data } = await http.get(`/projects/${projectId}/user-ptos/`)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (data as any[]).map(r => ({
        id: r.id,
        user_id: r.user,
        user_name: r.user_name ?? '',
        date: r.date,
      }))
    },
    /** 有休追加 */
    add: async (
      projectId: string, userId: string, date: string,
    ): Promise<UserPto> => {
      const { data } = await http.post(
        `/projects/${projectId}/user-ptos/`,
        { user: userId, date },
      )
      return {
        id: data.id,
        user_id: data.user,
        user_name: data.user_name ?? '',
        date: data.date,
      }
    },
    /** 有休削除 */
    remove: async (
      projectId: string, userId: string, date: string,
    ): Promise<void> => {
      await http.delete(
        `/projects/${projectId}/user-ptos/?user=${userId}&date=${date}`,
      )
    },
  },

}
