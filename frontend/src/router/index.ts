// ルート定義（認証ガード付き）
import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/api'
import { isPageLoading } from '@/composables/usePageLoading'

const PUBLIC_ROUTES = ['/login', '/register']

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // 認証系
    { path: '/login', name: 'login', component: () => import('@/views/auth/LoginView.vue') },
    { path: '/register', name: 'register', component: () => import('@/views/auth/TenantRegisterView.vue') },
    { path: '/users', name: 'users', component: () => import('@/views/auth/UserManagementView.vue') },
    { path: '/users/invite', name: 'user-invite', component: () => import('@/views/auth/UserInviteView.vue') },
    { path: '/profile', name: 'profile', component: () => import('@/views/auth/ProfileView.vue') },

    // ダッシュボード
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', name: 'dashboard', component: () => import('@/views/dashboard/DashboardView.vue') },

    // プロジェクト管理
    { path: '/projects', name: 'projects', component: () => import('@/views/project/ProjectListView.vue') },
    { path: '/projects/new', name: 'project-create', component: () => import('@/views/project/ProjectCreateView.vue') },
    { path: '/projects/:projectId/edit', name: 'project-edit', component: () => import('@/views/project/ProjectEditView.vue') },
    { path: '/projects/:projectId', name: 'project-detail', component: () => import('@/views/project/ProjectDetailView.vue') },
    { path: '/projects/:projectId/members', name: 'project-members', component: () => import('@/views/project/MemberManagementView.vue') },

    // クォーター管理
    { path: '/projects/:projectId/quarters', name: 'quarters', component: () => import('@/views/quarter/QuarterManagementView.vue') },
    { path: '/projects/:projectId/quarters/new', name: 'quarter-create', component: () => import('@/views/quarter/QuarterCreateView.vue') },
    { path: '/projects/:projectId/quarters/:quarterId/edit', name: 'quarter-edit', component: () => import('@/views/quarter/QuarterEditView.vue') },

    // WBS・タスク管理
    { path: '/projects/:projectId/wbs', name: 'wbs', component: () => import('@/views/task/WbsListView.vue') },
    { path: '/projects/:projectId/tasks/:taskId', name: 'task-detail', component: () => import('@/views/task/TaskDetailView.vue') },
    { path: '/projects/:projectId/auto-assign', name: 'auto-assign', component: () => import('@/views/task/AutoAssignView.vue') },
    { path: '/projects/:projectId/recent', name: 'recent-tasks', component: () => import('@/views/task/RecentTasksView.vue') },
    { path: '/projects/:projectId/progress', name: 'progress-list', component: () => import('@/views/task/ProgressListView.vue') },

    // ガントチャート
    { path: '/projects/:projectId/gantt', name: 'gantt', component: () => import('@/views/gantt/GanttView.vue') },

    // プロダクトロードマップ
    { path: '/projects/:projectId/roadmap', name: 'roadmap', component: () => import('@/views/roadmap/RoadmapView.vue') },
    { path: '/projects/:projectId/roadmap/new', name: 'roadmap-item-create', component: () => import('@/views/roadmap/RoadmapItemCreateView.vue') },
    { path: '/projects/:projectId/roadmap/:itemId/edit', name: 'roadmap-item-edit', component: () => import('@/views/roadmap/RoadmapItemEditView.vue') },

    // レビュー管理
    { path: '/projects/:projectId/reviews', name: 'reviews', component: () => import('@/views/review/ReviewListView.vue') },
    { path: '/projects/:projectId/tasks/:taskId/reviews', name: 'review-detail', component: () => import('@/views/review/ReviewDetailView.vue') },

    // 報告書管理
    { path: '/projects/:projectId/reports', name: 'reports', component: () => import('@/views/report/ReportView.vue') },

    // Excel出力
    { path: '/projects/:projectId/export/excel', name: 'excel-export', component: () => import('@/views/excel/ExcelExportView.vue') },

    // テンプレート管理
    { path: '/templates', name: 'templates', component: () => import('@/views/template/TemplateListView.vue') },
    { path: '/templates/new', name: 'template-create', component: () => import('@/views/template/TemplateCreateView.vue') },
    { path: '/templates/:templateId/edit', name: 'template-edit', component: () => import('@/views/template/TemplateEditView.vue') },
  ],
})

// 未認証ユーザーをログイン画面へリダイレクトするナビゲーションガード
router.beforeEach((to) => {
  isPageLoading.value = true
  if (!PUBLIC_ROUTES.includes(to.path) && !getToken()) {
    return { path: '/login' }
  }
})

router.afterEach(() => {
  isPageLoading.value = false
})

export default router
