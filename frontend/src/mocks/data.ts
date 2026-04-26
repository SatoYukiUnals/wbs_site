// MOCKデータ定義
// バックエンドAPIのレスポンスを模したローカルデータ

import type {
  User, Project, Quarter, Task, Review, ReviewComment, ReviewHistory,
  RoadmapItem, Template, AutoAssignPreview, ProjectSummary, MyTask, ProjectMember
} from '@/types'

/** sort_order・childrenを除いた生タスク型 */
type RawTask = Omit<Task, 'sort_order' | 'children'> & { children?: RawTask[] }

/** wbs_noの末尾番号からsort_orderを付与する */
const withSortOrders = (tasks: RawTask[]): Task[] =>
  tasks.map(t => ({
    ...t,
    sort_order: parseInt(t.wbs_no.split('.').pop() ?? '1'),
    children: t.children ? withSortOrders(t.children) : undefined,
  }))

/** MOCKユーザー一覧 */
export const mockUsers: User[] = [
  { id: 'u1', email: 'master@example.com', display_name: 'マスターユーザー', role: 'master', tenant_id: 't1' },
  { id: 'u2', email: 'sato@example.com',   display_name: '佐藤',             role: 'admin',  tenant_id: 't1' },
  { id: 'u3', email: 'tanaka@example.com', display_name: '田中',             role: 'member', tenant_id: 't1' },
  { id: 'u4', email: 'ito@example.com',    display_name: '伊藤',             role: 'member', tenant_id: 't1' },
]

/** MOCKログインユーザー（佐藤として動作） */
export const mockCurrentUser: User = mockUsers[1]

/** MOCKプロジェクト一覧 */
export const mockProjects: Project[] = [
  {
    id: 'p1',
    name: 'ECサイト 運用保守プロジェクト',
    description: 'ECサイトの運用保守・機能改善プロジェクト（2026年4月〜6月）',
    start_date: '2026-04-01',
    end_date: '2026-06-30',
    progress: 38,
    tenant_id: 't1',
  },
  {
    id: 'p2',
    name: '社内DXツール開発',
    description: '業務効率化のための社内ツール開発',
    start_date: '2026-05-01',
    end_date: '2026-10-31',
    progress: 20,
    tenant_id: 't1',
  },
]

/** MOCKプロジェクトメンバー */
export const mockMembers: ProjectMember[] = [
  { id: 'm1', user_id: 'u1', user_name: 'マスターユーザー', email: 'master@example.com', role: 'admin',  project_id: 'p1' },
  { id: 'm2', user_id: 'u2', user_name: '佐藤',             email: 'sato@example.com',   role: 'admin',  project_id: 'p1' },
  { id: 'm3', user_id: 'u3', user_name: '田中',             email: 'tanaka@example.com', role: 'member', project_id: 'p1' },
  { id: 'm4', user_id: 'u4', user_name: '伊藤',             email: 'ito@example.com',    role: 'member', project_id: 'p1' },
]

/** MOCKクォーター一覧 */
export const mockQuarters: Quarter[] = [
  { id: 'q1', title: '2026年4月〜6月', start_date: '2026-04-01', end_date: '2026-06-30', progress: 38, project_id: 'p1' },
]

/** MOCKタスク一覧（階層ツリー） */
export const mockTasks: Task[] = withSortOrders([

  // =====================================================
  // 1. 開発ルール・ドキュメント改善
  // =====================================================
  {
    id: 't1', title: '開発ルール・ドキュメント改善',
    description: '開発ルールの整備とドキュメントの改善作業',
    status: 'InProgress', progress: 65,
    start_date: '2026-04-01', end_date: '2026-05-12',
    actual_start_date: '2026-04-01', actual_end_date: null,
    estimated_hours: null, quarter_id: 'q1', parent_task_id: null,
    project_id: 'p1', wbs_no: '1', task_type: 'item', depth: 0, task_kind: null, tm_reviewer: null, pj_reviewer: null,
    assignees: [{ id: 'u2', name: '佐藤' }],
    children: [
      // 1.1 基本設計遡形作成
      {
        id: 't1-1', title: '基本設計遡形作成',
        description: '既存基本設計のテンプレート・ルール整備',
        status: 'Done', progress: 100,
        start_date: '2026-04-01', end_date: '2026-04-09',
        actual_start_date: '2026-04-01', actual_end_date: '2026-04-09',
        estimated_hours: null, quarter_id: 'q1', parent_task_id: 't1',
        project_id: 'p1', wbs_no: '1.1', task_type: 'item', depth: 1, task_kind: null, tm_reviewer: null, pj_reviewer: null,
        assignees: [{ id: 'u2', name: '佐藤' }],
        children: [
          {
            id: 't1-1-1', title: 'GitHubテンプレート作成',
            description: 'GitHubのIssue/PRテンプレートを作成する',
            status: 'Done', progress: 100,
            start_date: '2026-04-01', end_date: '2026-04-01',
            actual_start_date: '2026-04-01', actual_end_date: '2026-04-02',
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't1-1',
            project_id: 'p1', wbs_no: '1.1.1', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-1-2', title: 'API概要のテンプレート作成',
            description: 'API設計書のテンプレートを作成する',
            status: 'Done', progress: 100,
            start_date: '2026-04-01', end_date: '2026-04-01',
            actual_start_date: '2026-04-02', actual_end_date: '2026-04-02',
            estimated_hours: 1, quarter_id: 'q1', parent_task_id: 't1-1',
            project_id: 'p1', wbs_no: '1.1.2', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-1-3', title: '基本設計セルフチェックシート作成',
            description: '基本設計レビュー用セルフチェックシートを作成する',
            status: 'Done', progress: 100,
            start_date: '2026-04-02', end_date: '2026-04-07',
            actual_start_date: '2026-04-07', actual_end_date: '2026-04-07',
            estimated_hours: 4, quarter_id: 'q1', parent_task_id: 't1-1',
            project_id: 'p1', wbs_no: '1.1.3', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-1-4', title: '詳細設計 仕様書テンプレート作成',
            description: 'API/画面/IF/バッチ/テスト各仕様書テンプレートを整備する',
            status: 'Done', progress: 100,
            start_date: '2026-04-07', end_date: '2026-04-08',
            actual_start_date: '2026-04-07', actual_end_date: '2026-04-08',
            estimated_hours: 7, quarter_id: 'q1', parent_task_id: 't1-1',
            project_id: 'p1', wbs_no: '1.1.4', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-1-5', title: 'TMRV',
            description: 'チームレビュー実施',
            status: 'Done', progress: 100,
            start_date: '2026-04-08', end_date: '2026-04-08',
            actual_start_date: '2026-04-08', actual_end_date: '2026-04-08',
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't1-1',
            project_id: 'p1', wbs_no: '1.1.5', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't1-1-6', title: 'TMRV修正',
            description: 'チームレビュー指摘事項を修正する',
            status: 'Done', progress: 100,
            start_date: '2026-04-09', end_date: '2026-04-09',
            actual_start_date: '2026-04-09', actual_end_date: '2026-04-09',
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't1-1',
            project_id: 'p1', wbs_no: '1.1.6', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
        ],
      },
      // 1.2 GitHubの運用ルール
      {
        id: 't1-2', title: 'GitHubの運用ルール',
        description: 'GitHubを使った開発フローのルール整備',
        status: 'Done', progress: 100,
        start_date: '2026-04-08', end_date: '2026-04-14',
        actual_start_date: '2026-04-08', actual_end_date: '2026-04-14',
        estimated_hours: null, quarter_id: 'q1', parent_task_id: 't1',
        project_id: 'p1', wbs_no: '1.2', task_type: 'item', depth: 1, task_kind: null, tm_reviewer: null, pj_reviewer: null,
        assignees: [{ id: 'u2', name: '佐藤' }],
        children: [
          {
            id: 't1-2-1', title: 'ブランチの管理方法 ドキュメント作成',
            description: 'ブランチ命名規則・管理フローのドキュメントを作成する',
            status: 'Done', progress: 100,
            start_date: '2026-04-08', end_date: '2026-04-08',
            actual_start_date: '2026-04-08', actual_end_date: '2026-04-14',
            estimated_hours: 1, quarter_id: 'q1', parent_task_id: 't1-2',
            project_id: 'p1', wbs_no: '1.2.1', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-2-2', title: '命名規約 ドキュメント作成',
            description: '変数・関数・ファイルの命名規約ドキュメントを作成する',
            status: 'Done', progress: 100,
            start_date: '2026-04-08', end_date: '2026-04-08',
            actual_start_date: '2026-04-08', actual_end_date: '2026-04-14',
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't1-2',
            project_id: 'p1', wbs_no: '1.2.2', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-2-3', title: 'PRルール ドキュメント作成',
            description: 'プルリクエストの作成・レビュールールを文書化する',
            status: 'Done', progress: 100,
            start_date: '2026-04-08', end_date: '2026-04-08',
            actual_start_date: '2026-04-08', actual_end_date: '2026-04-14',
            estimated_hours: 1.5, quarter_id: 'q1', parent_task_id: 't1-2',
            project_id: 'p1', wbs_no: '1.2.3', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-2-4', title: 'Issue管理 ドキュメント作成',
            description: 'Issueの起票・管理フロールールを文書化する',
            status: 'Done', progress: 100,
            start_date: '2026-04-08', end_date: '2026-04-08',
            actual_start_date: '2026-04-08', actual_end_date: '2026-04-14',
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't1-2',
            project_id: 'p1', wbs_no: '1.2.4', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
        ],
      },
      // 1.3 マニュアルルール作成
      {
        id: 't1-3', title: 'マニュアルルール作成',
        description: 'マニュアルの執筆ルール・フォーマットを整備する',
        status: 'Done', progress: 100,
        start_date: '2026-04-09', end_date: '2026-04-15',
        actual_start_date: '2026-04-09', actual_end_date: '2026-04-15',
        estimated_hours: null, quarter_id: 'q1', parent_task_id: 't1',
        project_id: 'p1', wbs_no: '1.3', task_type: 'item', depth: 1, task_kind: null, tm_reviewer: null, pj_reviewer: null,
        assignees: [{ id: 'u2', name: '佐藤' }],
        children: [
          {
            id: 't1-3-1', title: 'ドキュメント作成',
            description: 'マニュアル執筆ルールのドキュメントを作成する',
            status: 'Done', progress: 100,
            start_date: '2026-04-09', end_date: '2026-04-14',
            actual_start_date: '2026-04-09', actual_end_date: '2026-04-14',
            estimated_hours: 6, quarter_id: 'q1', parent_task_id: 't1-3',
            project_id: 'p1', wbs_no: '1.3.1', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-3-2', title: 'TMRV',
            description: 'チームレビュー実施',
            status: 'Done', progress: 100,
            start_date: '2026-04-15', end_date: '2026-04-15',
            actual_start_date: '2026-04-15', actual_end_date: '2026-04-15',
            estimated_hours: 1, quarter_id: 'q1', parent_task_id: 't1-3',
            project_id: 'p1', wbs_no: '1.3.2', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't1-3-3', title: 'TMRV修正',
            description: 'チームレビュー指摘事項を修正する',
            status: 'Done', progress: 100,
            start_date: '2026-04-15', end_date: '2026-04-15',
            actual_start_date: '2026-04-15', actual_end_date: '2026-04-15',
            estimated_hours: 1, quarter_id: 'q1', parent_task_id: 't1-3',
            project_id: 'p1', wbs_no: '1.3.3', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
        ],
      },
      // 1.4 画面一覧の作成
      {
        id: 't1-4', title: '画面一覧の作成',
        description: '全83画面の一覧ドキュメントを作成する',
        status: 'InProgress', progress: 65,
        start_date: '2026-04-15', end_date: '2026-05-12',
        actual_start_date: '2026-04-14', actual_end_date: null,
        estimated_hours: null, quarter_id: 'q1', parent_task_id: 't1',
        project_id: 'p1', wbs_no: '1.4', task_type: 'item', depth: 1, task_kind: null, tm_reviewer: null, pj_reviewer: null,
        assignees: [{ id: 'u2', name: '佐藤' }],
        children: [
          {
            id: 't1-4-1', title: 'ログイン・TOP・契約関連画面',
            description: 'ログイン/TOP/契約一覧・登録・変更・詳細・複製画面の一覧項目を作成する',
            status: 'Done', progress: 100,
            start_date: '2026-04-15', end_date: '2026-04-15',
            actual_start_date: '2026-04-14', actual_end_date: '2026-04-15',
            estimated_hours: 3.5, quarter_id: 'q1', parent_task_id: 't1-4',
            project_id: 'p1', wbs_no: '1.4.1', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-4-2', title: '請求・注文・担当者・条件関連画面',
            description: '請求/注文/担当者/条件/会社情報管理等の一覧項目を作成する',
            status: 'Done', progress: 100,
            start_date: '2026-04-16', end_date: '2026-04-16',
            actual_start_date: '2026-04-15', actual_end_date: '2026-04-16',
            estimated_hours: 6, quarter_id: 'q1', parent_task_id: 't1-4',
            project_id: 'p1', wbs_no: '1.4.2', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-4-3', title: '事業者・担当者・承認依頼関連画面',
            description: '事業者/担当者/条件通知/通信グループ/承認依頼等の一覧項目を作成する',
            status: 'Done', progress: 100,
            start_date: '2026-04-21', end_date: '2026-04-22',
            actual_start_date: '2026-04-21', actual_end_date: '2026-04-22',
            estimated_hours: 8, quarter_id: 'q1', parent_task_id: 't1-4',
            project_id: 'p1', wbs_no: '1.4.3', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-4-4', title: 'LP・申込・アカウント・通知関連画面',
            description: 'LP/申込/アカウント情報管理/お知らせ/注文書添付等の一覧項目を作成する',
            status: 'Done', progress: 100,
            start_date: '2026-04-23', end_date: '2026-04-23',
            actual_start_date: '2026-04-23', actual_end_date: '2026-04-23',
            estimated_hours: 6, quarter_id: 'q1', parent_task_id: 't1-4',
            project_id: 'p1', wbs_no: '1.4.4', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-4-5', title: 'インポート・承認・残り画面',
            description: 'インポート/承認一覧/プラン変更/お知らせ詳細等の残り画面の一覧項目を作成する',
            status: 'Todo', progress: 0,
            start_date: '2026-04-28', end_date: '2026-05-07',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 8, quarter_id: 'q1', parent_task_id: 't1-4',
            project_id: 'p1', wbs_no: '1.4.5', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't1-4-6', title: 'TMRV',
            description: 'チームレビュー実施',
            status: 'Todo', progress: 0,
            start_date: '2026-05-12', end_date: '2026-05-12',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 3, quarter_id: 'q1', parent_task_id: 't1-4',
            project_id: 'p1', wbs_no: '1.4.6', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't1-4-7', title: 'TMRV修正',
            description: 'チームレビュー指摘事項を修正する',
            status: 'Todo', progress: 0,
            start_date: '2026-05-12', end_date: '2026-05-12',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 3, quarter_id: 'q1', parent_task_id: 't1-4',
            project_id: 'p1', wbs_no: '1.4.7', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
        ],
      },
    ],
  },

  // =====================================================
  // 2. 要件追加
  // =====================================================
  {
    id: 't2', title: '要件追加',
    description: '新規機能・変更要件の実装',
    status: 'InProgress', progress: 42,
    start_date: '2026-04-01', end_date: '2026-06-09',
    actual_start_date: '2026-04-01', actual_end_date: null,
    estimated_hours: null, quarter_id: 'q1', parent_task_id: null,
    project_id: 'p1', wbs_no: '2', task_type: 'item', depth: 0, task_kind: null, tm_reviewer: null, pj_reviewer: null,
    assignees: [{ id: 'u3', name: '田中' }],
    children: [
      // 2.1 解約後アンケートの追加
      {
        id: 't2-1', title: '解約後アンケートの追加',
        description: '解約後にアンケートを送信する機能を追加する',
        status: 'InProgress', progress: 76,
        start_date: '2026-04-01', end_date: '2026-05-07',
        actual_start_date: '2026-04-01', actual_end_date: null,
        estimated_hours: null, quarter_id: 'q1', parent_task_id: 't2',
        project_id: 'p1', wbs_no: '2.1', task_type: 'item', depth: 1, task_kind: null, tm_reviewer: null, pj_reviewer: null,
        assignees: [{ id: 'u3', name: '田中' }],
        children: [
          {
            id: 't2-1-1', title: '詳細設計 ドキュメント作成',
            description: 'アンケート機能の詳細設計書を作成する',
            status: 'Done', progress: 100,
            start_date: '2026-04-01', end_date: '2026-04-02',
            actual_start_date: '2026-04-01', actual_end_date: '2026-04-02',
            estimated_hours: 6, quarter_id: 'q1', parent_task_id: 't2-1',
            project_id: 'p1', wbs_no: '2.1.1', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-1-2', title: 'テーブル設計 ドキュメント作成',
            description: 'アンケートデータのテーブル設計書を作成する',
            status: 'Done', progress: 100,
            start_date: '2026-04-02', end_date: '2026-04-02',
            actual_start_date: '2026-04-02', actual_end_date: '2026-04-02',
            estimated_hours: 1, quarter_id: 'q1', parent_task_id: 't2-1',
            project_id: 'p1', wbs_no: '2.1.2', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-1-3', title: 'アンケート登録API 実装',
            description: 'アンケート回答を登録するAPIを実装する',
            status: 'Done', progress: 100,
            start_date: '2026-04-15', end_date: '2026-04-15',
            actual_start_date: '2026-04-14', actual_end_date: '2026-04-14',
            estimated_hours: 3, quarter_id: 'q1', parent_task_id: 't2-1',
            project_id: 'p1', wbs_no: '2.1.3', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-1-4', title: 'アンケート一覧API 実装',
            description: 'アンケート一覧を取得するAPIを実装する',
            status: 'Done', progress: 100,
            start_date: '2026-04-16', end_date: '2026-04-16',
            actual_start_date: '2026-04-14', actual_end_date: '2026-04-15',
            estimated_hours: 4, quarter_id: 'q1', parent_task_id: 't2-1',
            project_id: 'p1', wbs_no: '2.1.4', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-1-5', title: 'アンケート登録画面 実装',
            description: 'アンケート回答を入力・登録する画面を実装する',
            status: 'Done', progress: 100,
            start_date: '2026-04-16', end_date: '2026-04-21',
            actual_start_date: '2026-04-15', actual_end_date: '2026-04-16',
            estimated_hours: 4, quarter_id: 'q1', parent_task_id: 't2-1',
            project_id: 'p1', wbs_no: '2.1.5', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-1-6', title: 'アンケート一覧表示画面 実装',
            description: 'アンケート回答一覧を表示する画面を実装する',
            status: 'Done', progress: 100,
            start_date: '2026-04-21', end_date: '2026-04-22',
            actual_start_date: '2026-04-21', actual_end_date: '2026-04-22',
            estimated_hours: 4, quarter_id: 'q1', parent_task_id: 't2-1',
            project_id: 'p1', wbs_no: '2.1.6', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-1-7', title: 'マニュアル修正（画像以外）',
            description: 'アンケート機能追加に伴うマニュアルのテキスト部分を修正する',
            status: 'Done', progress: 100,
            start_date: '2026-04-22', end_date: '2026-04-22',
            actual_start_date: '2026-04-22', actual_end_date: '2026-04-22',
            estimated_hours: 3, quarter_id: 'q1', parent_task_id: 't2-1',
            project_id: 'p1', wbs_no: '2.1.7', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-1-8', title: 'リリース TMRV',
            description: 'リリース前チームレビュー実施',
            status: 'Todo', progress: 0,
            start_date: '2026-04-28', end_date: '2026-04-28',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't2-1',
            project_id: 'p1', wbs_no: '2.1.8', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't2-1-9', title: 'テスト実施・修正',
            description: 'リリース前テストを実施し指摘事項を修正する',
            status: 'Todo', progress: 0,
            start_date: '2026-04-30', end_date: '2026-04-30',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 2.25, quarter_id: 'q1', parent_task_id: 't2-1',
            project_id: 'p1', wbs_no: '2.1.9', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-1-10', title: 'マニュアル修正（画像）',
            description: 'アンケート機能追加に伴うマニュアルのスクリーンショットを更新する',
            status: 'Todo', progress: 0,
            start_date: '2026-04-28', end_date: '2026-05-07',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't2-1',
            project_id: 'p1', wbs_no: '2.1.10', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
        ],
      },
      // 2.2 契約計算式の端数処理の修正
      {
        id: 't2-2', title: '契約計算式の端数処理の修正',
        description: '契約金額の計算式における端数処理バグを修正する',
        status: 'InProgress', progress: 14,
        start_date: '2026-04-23', end_date: '2026-05-28',
        actual_start_date: '2026-04-23', actual_end_date: null,
        estimated_hours: null, quarter_id: 'q1', parent_task_id: 't2',
        project_id: 'p1', wbs_no: '2.2', task_type: 'item', depth: 1, task_kind: null, tm_reviewer: null, pj_reviewer: null,
        assignees: [{ id: 'u3', name: '田中' }],
        children: [
          {
            id: 't2-2-1', title: '詳細設計 ドキュメント作成',
            description: '端数処理修正の詳細設計書を作成する（計算式の具体的な決定）',
            status: 'Done', progress: 100,
            start_date: '2026-04-23', end_date: '2026-04-23',
            actual_start_date: '2026-04-23', actual_end_date: '2026-04-23',
            estimated_hours: 6, quarter_id: 'q1', parent_task_id: 't2-2',
            project_id: 'p1', wbs_no: '2.2.1', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-2-2', title: 'テーブル設計 ドキュメント作成',
            description: 'テーブル変更の設計書を作成する',
            status: 'Todo', progress: 0,
            start_date: '2026-04-28', end_date: '2026-04-28',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 1, quarter_id: 'q1', parent_task_id: 't2-2',
            project_id: 'p1', wbs_no: '2.2.2', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-2-3', title: 'API設計 ドキュメント作成',
            description: '修正APIの設計書を作成する',
            status: 'Todo', progress: 0,
            start_date: '2026-04-28', end_date: '2026-04-28',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 4, quarter_id: 'q1', parent_task_id: 't2-2',
            project_id: 'p1', wbs_no: '2.2.3', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-2-4', title: '画面仕様書 ドキュメント作成',
            description: '契約登録・変更・複製画面の仕様書を作成する',
            status: 'Todo', progress: 0,
            start_date: '2026-04-30', end_date: '2026-04-30',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 4, quarter_id: 'q1', parent_task_id: 't2-2',
            project_id: 'p1', wbs_no: '2.2.4', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-2-5', title: '実装・テスト',
            description: '端数処理の修正実装とテストを実施する',
            status: 'Todo', progress: 0,
            start_date: '2026-05-14', end_date: '2026-05-21',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 12, quarter_id: 'q1', parent_task_id: 't2-2',
            project_id: 'p1', wbs_no: '2.2.5', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-2-6', title: 'リリース・テスト',
            description: 'リリース前テスト・本番リリースを実施する',
            status: 'Todo', progress: 0,
            start_date: '2026-05-27', end_date: '2026-05-28',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 2, quarter_id: 'q1', parent_task_id: 't2-2',
            project_id: 'p1', wbs_no: '2.2.6', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
        ],
      },
      // 2.3 注文書・請求書の文字サイズ自動調整
      {
        id: 't2-3', title: '注文書・請求書の文字サイズ自動調整',
        description: 'PDF出力時に文字量に応じてフォントサイズを自動調整する機能を追加する',
        status: 'Todo', progress: 0,
        start_date: '2026-05-27', end_date: '2026-06-09',
        actual_start_date: null, actual_end_date: null,
        estimated_hours: null, quarter_id: 'q1', parent_task_id: 't2',
        project_id: 'p1', wbs_no: '2.3', task_type: 'item', depth: 1, task_kind: null, tm_reviewer: null, pj_reviewer: null,
        assignees: [{ id: 'u3', name: '田中' }],
        children: [
          {
            id: 't2-3-1', title: '詳細設計 ドキュメント作成',
            description: '文字サイズ自動調整の詳細設計書を作成する',
            status: 'Todo', progress: 0,
            start_date: '2026-05-27', end_date: '2026-06-02',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 4, quarter_id: 'q1', parent_task_id: 't2-3',
            project_id: 'p1', wbs_no: '2.3.1', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't2-3-2', title: '実装・テスト',
            description: '文字サイズ自動調整の実装とテストを実施する',
            status: 'Todo', progress: 0,
            start_date: '2026-06-03', end_date: '2026-06-09',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 9, quarter_id: 'q1', parent_task_id: 't2-3',
            project_id: 'p1', wbs_no: '2.3.2', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
        ],
      },
    ],
  },

  // =====================================================
  // 3. 運用保守
  // =====================================================
  {
    id: 't3', title: '運用保守',
    description: '定期リリース・月次報告・障害対応等の運用業務',
    status: 'InProgress', progress: 33,
    start_date: '2026-04-02', end_date: '2026-06-17',
    actual_start_date: '2026-04-02', actual_end_date: null,
    estimated_hours: null, quarter_id: 'q1', parent_task_id: null,
    project_id: 'p1', wbs_no: '3', task_type: 'item', depth: 0, task_kind: null, tm_reviewer: null, pj_reviewer: null,
    assignees: [{ id: 'u2', name: '佐藤' }, { id: 'u3', name: '田中' }],
    children: [
      // 3.1 月次報告
      {
        id: 't3-1', title: '月次報告',
        description: '各月の進捗・稼働時間報告書を作成する',
        status: 'InProgress', progress: 33,
        start_date: '2026-04-02', end_date: '2026-06-02',
        actual_start_date: '2026-04-02', actual_end_date: null,
        estimated_hours: null, quarter_id: 'q1', parent_task_id: 't3',
        project_id: 'p1', wbs_no: '3.1', task_type: 'item', depth: 1, task_kind: null, tm_reviewer: null, pj_reviewer: null,
        assignees: [{ id: 'u2', name: '佐藤' }],
        children: [
          {
            id: 't3-1-1', title: '3月 報告書作成',
            description: '3月分の月次報告書を作成・提出する',
            status: 'Done', progress: 100,
            start_date: '2026-04-02', end_date: '2026-04-02',
            actual_start_date: '2026-04-02', actual_end_date: '2026-04-02',
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't3-1',
            project_id: 'p1', wbs_no: '3.1.1', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't3-1-2', title: '4月 報告書作成',
            description: '4月分の月次報告書を作成・提出する',
            status: 'Todo', progress: 0,
            start_date: '2026-05-07', end_date: '2026-05-07',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't3-1',
            project_id: 'p1', wbs_no: '3.1.2', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't3-1-3', title: '5月 報告書作成',
            description: '5月分の月次報告書を作成・提出する',
            status: 'Todo', progress: 0,
            start_date: '2026-06-02', end_date: '2026-06-02',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't3-1',
            project_id: 'p1', wbs_no: '3.1.3', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
        ],
      },
      // 3.2 定期リリース
      {
        id: 't3-2', title: '定期リリース',
        description: '毎月の定期リリース作業（リグレッションテスト・本番リリース）',
        status: 'InProgress', progress: 33,
        start_date: '2026-04-08', end_date: '2026-06-17',
        actual_start_date: '2026-04-08', actual_end_date: null,
        estimated_hours: null, quarter_id: 'q1', parent_task_id: 't3',
        project_id: 'p1', wbs_no: '3.2', task_type: 'item', depth: 1, task_kind: null, tm_reviewer: null, pj_reviewer: null,
        assignees: [{ id: 'u3', name: '田中' }],
        children: [
          {
            id: 't3-2-1', title: '4月 リリースお知らせ',
            description: 'リリース内容のお知らせを作成・送付する',
            status: 'Done', progress: 100,
            start_date: '2026-04-08', end_date: '2026-04-08',
            actual_start_date: '2026-04-09', actual_end_date: '2026-04-09',
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't3-2',
            project_id: 'p1', wbs_no: '3.2.1', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't3-2-2', title: '4月 リリース準備',
            description: '本番リリース前の準備作業（設定確認・バックアップ等）',
            status: 'Done', progress: 100,
            start_date: '2026-04-09', end_date: '2026-04-09',
            actual_start_date: '2026-04-09', actual_end_date: '2026-04-09',
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't3-2',
            project_id: 'p1', wbs_no: '3.2.2', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't3-2-3', title: '4月 リグレッションテスト',
            description: '本番リリース前のリグレッションテストを実施する',
            status: 'Done', progress: 100,
            start_date: '2026-04-14', end_date: '2026-04-14',
            actual_start_date: '2026-04-14', actual_end_date: '2026-04-14',
            estimated_hours: 3, quarter_id: 'q1', parent_task_id: 't3-2',
            project_id: 'p1', wbs_no: '3.2.3', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't3-2-4', title: '4月 定期リリース',
            description: '4月度の本番リリースを実施する',
            status: 'Done', progress: 100,
            start_date: '2026-04-15', end_date: '2026-04-15',
            actual_start_date: '2026-04-15', actual_end_date: '2026-04-15',
            estimated_hours: 1, quarter_id: 'q1', parent_task_id: 't3-2',
            project_id: 'p1', wbs_no: '3.2.4', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't3-2-5', title: '5月 リリースお知らせ',
            description: 'リリース内容のお知らせを作成・送付する',
            status: 'Todo', progress: 0,
            start_date: '2026-05-07', end_date: '2026-05-07',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't3-2',
            project_id: 'p1', wbs_no: '3.2.5', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't3-2-6', title: '5月 リグレッションテスト',
            description: '本番リリース前のリグレッションテストを実施する',
            status: 'Todo', progress: 0,
            start_date: '2026-05-07', end_date: '2026-05-07',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 3, quarter_id: 'q1', parent_task_id: 't3-2',
            project_id: 'p1', wbs_no: '3.2.6', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't3-2-7', title: '5月 定期リリース',
            description: '5月度の本番リリースを実施する',
            status: 'Todo', progress: 0,
            start_date: '2026-05-13', end_date: '2026-05-13',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 1, quarter_id: 'q1', parent_task_id: 't3-2',
            project_id: 'p1', wbs_no: '3.2.7', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't3-2-8', title: '6月 リリースお知らせ',
            description: 'リリース内容のお知らせを作成・送付する',
            status: 'Todo', progress: 0,
            start_date: '2026-06-10', end_date: '2026-06-10',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't3-2',
            project_id: 'p1', wbs_no: '3.2.8', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't3-2-9', title: '6月 リグレッションテスト',
            description: '本番リリース前のリグレッションテストを実施する',
            status: 'Todo', progress: 0,
            start_date: '2026-06-11', end_date: '2026-06-11',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 3, quarter_id: 'q1', parent_task_id: 't3-2',
            project_id: 'p1', wbs_no: '3.2.9', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't3-2-10', title: '6月 定期リリース',
            description: '6月度の本番リリースを実施する',
            status: 'Todo', progress: 0,
            start_date: '2026-06-17', end_date: '2026-06-17',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 1, quarter_id: 'q1', parent_task_id: 't3-2',
            project_id: 'p1', wbs_no: '3.2.10', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
        ],
      },
    ],
  },

  // =====================================================
  // 4. その他
  // =====================================================
  {
    id: 't4', title: 'その他',
    description: '前Qからの繰越タスク・次Q準備等',
    status: 'InProgress', progress: 55,
    start_date: '2026-03-25', end_date: '2026-06-24',
    actual_start_date: '2026-03-25', actual_end_date: null,
    estimated_hours: null, quarter_id: 'q1', parent_task_id: null,
    project_id: 'p1', wbs_no: '4', task_type: 'item', depth: 0, task_kind: null, tm_reviewer: null, pj_reviewer: null,
    assignees: [{ id: 'u2', name: '佐藤' }],
    children: [
      // 4.1 前Qのタスク 稼働時間精算
      {
        id: 't4-1', title: '前Qのタスク 稼働時間精算',
        description: '前クォーターから持ち越された稼働時間精算作業',
        status: 'Done', progress: 100,
        start_date: '2026-03-25', end_date: '2026-04-15',
        actual_start_date: '2026-03-25', actual_end_date: '2026-04-15',
        estimated_hours: null, quarter_id: 'q1', parent_task_id: 't4',
        project_id: 'p1', wbs_no: '4.1', task_type: 'item', depth: 1, task_kind: null, tm_reviewer: null, pj_reviewer: null,
        assignees: [{ id: 'u2', name: '佐藤' }],
        children: [
          {
            id: 't4-1-1', title: '仕様書修正',
            description: '稼働時間精算の仕様書を修正する',
            status: 'Done', progress: 100,
            start_date: '2026-03-25', end_date: '2026-03-25',
            actual_start_date: '2026-03-25', actual_end_date: '2026-03-25',
            estimated_hours: 1, quarter_id: 'q1', parent_task_id: 't4-1',
            project_id: 'p1', wbs_no: '4.1.1', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't4-1-2', title: 'コード修正',
            description: '稼働時間精算のコードを修正する',
            status: 'Done', progress: 100,
            start_date: '2026-03-25', end_date: '2026-03-26',
            actual_start_date: '2026-03-25', actual_end_date: '2026-04-01',
            estimated_hours: 4, quarter_id: 'q1', parent_task_id: 't4-1',
            project_id: 'p1', wbs_no: '4.1.2', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't4-1-3', title: 'テスト修正',
            description: 'コード修正に伴うテストを修正する',
            status: 'Done', progress: 100,
            start_date: '2026-03-26', end_date: '2026-03-26',
            actual_start_date: '2026-03-26', actual_end_date: '2026-04-01',
            estimated_hours: 2, quarter_id: 'q1', parent_task_id: 't4-1',
            project_id: 'p1', wbs_no: '4.1.3', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't4-1-4', title: 'テスト実施',
            description: '修正後のテストを実施する',
            status: 'Done', progress: 100,
            start_date: '2026-03-26', end_date: '2026-03-26',
            actual_start_date: '2026-04-02', actual_end_date: '2026-04-07',
            estimated_hours: 1, quarter_id: 'q1', parent_task_id: 't4-1',
            project_id: 'p1', wbs_no: '4.1.4', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't4-1-5', title: 'リリース',
            description: '稼働時間精算機能をリリースする',
            status: 'Done', progress: 100,
            start_date: '2026-04-07', end_date: '2026-04-15',
            actual_start_date: '2026-04-07', actual_end_date: '2026-04-15',
            estimated_hours: 0.5, quarter_id: 'q1', parent_task_id: 't4-1',
            project_id: 'p1', wbs_no: '4.1.5', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
        ],
      },
      // 4.2 次Q準備
      {
        id: 't4-2', title: '次Q準備',
        description: '次クォーターに向けたWBS・仕様書の作成',
        status: 'Todo', progress: 0,
        start_date: '2026-06-16', end_date: '2026-06-24',
        actual_start_date: null, actual_end_date: null,
        estimated_hours: null, quarter_id: 'q1', parent_task_id: 't4',
        project_id: 'p1', wbs_no: '4.2', task_type: 'item', depth: 1, task_kind: null, tm_reviewer: null, pj_reviewer: null,
        assignees: [{ id: 'u2', name: '佐藤' }, { id: 'u3', name: '田中' }],
        children: [
          {
            id: 't4-2-1', title: '仕様検討（佐藤）',
            description: '次Q対応機能の仕様を検討・ドキュメント化する（佐藤分）',
            status: 'Todo', progress: 0,
            start_date: '2026-06-16', end_date: '2026-06-18',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 9.5, quarter_id: 'q1', parent_task_id: 't4-2',
            project_id: 'p1', wbs_no: '4.2.1', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
          {
            id: 't4-2-2', title: '仕様検討（田中）',
            description: '次Q対応機能の仕様を検討・ドキュメント化する（田中分）',
            status: 'Todo', progress: 0,
            start_date: '2026-06-16', end_date: '2026-06-18',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 9.5, quarter_id: 'q1', parent_task_id: 't4-2',
            project_id: 'p1', wbs_no: '4.2.2', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u3', name: '田中' }],
          },
          {
            id: 't4-2-3', title: 'WBS作成',
            description: '次クォーターのWBSを作成・PJレビューを受ける',
            status: 'Todo', progress: 0,
            start_date: '2026-06-23', end_date: '2026-06-24',
            actual_start_date: null, actual_end_date: null,
            estimated_hours: 7, quarter_id: 'q1', parent_task_id: 't4-2',
            project_id: 'p1', wbs_no: '4.2.3', task_type: 'task', depth: 2, task_kind: null, tm_reviewer: null, pj_reviewer: null,
            assignees: [{ id: 'u2', name: '佐藤' }],
          },
        ],
      },
    ],
  },
])

/** MOCKレビュー一覧 */
export const mockReviews: Review[] = [
  {
    id: 'r1', task_id: 't2-1', task_title: '解約後アンケートの追加',
    status: 'pending', reviewer_id: null, reviewer_name: null,
    created_at: '2026-04-22T14:00:00', updated_at: '2026-04-22T14:00:00',
  },
]

/** MOCKレビューコメント */
export const mockReviewComments: ReviewComment[] = [
  {
    id: 'rc1', review_id: 'r1', body: 'アンケート登録APIのバリデーション処理が不足しています。必須項目チェックを追加してください。',
    author_id: 'u2', author_name: '佐藤', created_at: '2026-04-22T15:00:00',
  },
]

/** MOCKレビュー履歴 */
export const mockReviewHistory: ReviewHistory[] = [
  {
    id: 'rh1', review_id: 'r1', action: 'request_review',
    user_id: 'u3', user_name: '田中', created_at: '2026-04-22T14:00:00',
  },
]

/** MOCKロードマップアイテム */
export const mockRoadmapItems: RoadmapItem[] = [
  { id: 'ri1', title: '解約後アンケート リリース', description: '解約後アンケート機能の本番リリース', quarter_id: 'q1', quarter_title: '2026年4月〜6月', status: 'InProgress', project_id: 'p1' },
  { id: 'ri2', title: '契約計算式修正 リリース', description: '端数処理バグ修正の本番リリース', quarter_id: 'q1', quarter_title: '2026年4月〜6月', status: '計画中', project_id: 'p1' },
  { id: 'ri3', title: '文字サイズ自動調整 リリース', description: 'PDF出力文字サイズ自動調整機能のリリース', quarter_id: 'q1', quarter_title: '2026年4月〜6月', status: '計画中', project_id: 'p1' },
]

/** MOCKテンプレート一覧 */
export const mockTemplates: Template[] = [
  {
    id: 'tpl1', title: '機能追加 標準フロー', type: 'wbs',
    content: '詳細設計\nテーブル設計\nAPI設計\n画面仕様書\nテスト仕様書\n実装\nTMRV\nTMRV修正\nリリース',
    is_shared: true, created_by: 'u2', created_by_name: '佐藤',
  },
  {
    id: 'tpl2', title: 'バグ修正テンプレート', type: 'task',
    content: '## 概要\n\n## 再現手順\n1. \n\n## 原因\n\n## 対応内容\n',
    is_shared: true, created_by: 'u2', created_by_name: '佐藤',
  },
]

/** MOCKダッシュボードサマリー */
export const mockProjectSummaries: ProjectSummary[] = [
  {
    id: 'p1', name: 'ECサイト 運用保守プロジェクト', progress: 38,
    status_counts: { Todo: 18, InProgress: 4, Done: 19, InReview: 0, OnHold: 0 },
    delayed_count: 0,
  },
  {
    id: 'p2', name: '社内DXツール開発', progress: 20,
    status_counts: { Todo: 3, InProgress: 1, Done: 0, InReview: 0, OnHold: 0 },
    delayed_count: 0,
  },
]

/** MOCKダッシュボード・自分のタスク */
export const mockMyTasks: MyTask[] = [
  { id: 't1-4', title: '画面一覧の作成', project_id: 'p1', project_name: 'ECサイト 運用保守プロジェクト', status: 'InProgress', progress: 65, end_date: '2026-05-12' },
  { id: 't2-1', title: '解約後アンケートの追加', project_id: 'p1', project_name: 'ECサイト 運用保守プロジェクト', status: 'InProgress', progress: 76, end_date: '2026-05-07' },
  { id: 't2-2', title: '契約計算式の端数処理の修正', project_id: 'p1', project_name: 'ECサイト 運用保守プロジェクト', status: 'InProgress', progress: 14, end_date: '2026-05-28' },
]

/** MOCKアサインプレビュー結果 */
export const mockAutoAssignPreview: AutoAssignPreview[] = [
  { task_id: 't2-2-2', task_title: 'テーブル設計 ドキュメント作成', assignee_id: 'u3', assignee_name: '田中' },
  { task_id: 't2-2-3', task_title: 'API設計 ドキュメント作成', assignee_id: 'u3', assignee_name: '田中' },
]
