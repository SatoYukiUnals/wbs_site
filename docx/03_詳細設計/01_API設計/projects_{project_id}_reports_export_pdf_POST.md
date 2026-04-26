# 【API設計書】PDF出力API

## 1. 概要

編集済みの報告書テキストをPDFに変換してバイナリで返す。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/reports/export/pdf/`
- **認証:** 必要 / **権限:** メンバー以上

## 3. リクエスト

```json
{
  "title": "2026年Q1 進捗報告書",
  "period_start": "2026-04-01",
  "period_end": "2026-06-30",
  "sections": {
    "overview": "プロジェクト概要テキスト...",
    "summary": "進捗サマリー...",
    "quarters": "クォーター別進捗...",
    "tasks": "タスク一覧...",
    "delayed": "遅延タスク...",
    "reviews": "レビュー状況..."
  }
}
```

## 4. レスポンス

### 成功 (200 OK)

- `Content-Type: application/pdf`
- `Content-Disposition: attachment; filename="report.pdf"`
- ボディ：PDF バイナリ

### エラー

| 状況 | ステータス |
|---|---|
| PDF生成失敗 | 500 |

## 5. 内部処理

1. JWT検証・メンバー確認
2. リクエストボディのテキストを HTML テンプレートに流し込む
3. WeasyPrint / ReportLab で PDF 生成
4. PDF バイナリをレスポンスで返す
