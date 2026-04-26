# 【API設計書】報告書自動生成API

## 1. 概要

対象期間のプロジェクトデータを集計し、報告書テキストを自動生成して返す。DBへの保存は行わない。

## 2. エンドポイント

- **Method:** `GET`
- **Path:** `/api/v1/projects/{project_id}/reports/generate/`
- **認証:** 必要 / **権限:** メンバー以上

## 3. リクエスト

### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `period_start` | date | ※ | 対象期間開始日（YYYY-MM-DD） |
| `period_end` | date | ※ | 対象期間終了日（YYYY-MM-DD） |
| `quarter_id` | UUID | ※ | クォーター指定（`period_start/end` と排他） |

※ `period_start`+`period_end` または `quarter_id` のいずれかを指定

## 4. レスポンス

```json
{
  "sections": {
    "overview": "プロジェクト「ECサイトリニューアル」の進捗報告です...",
    "summary": "全体進捗：40%",
    "quarters": "Q1進捗：60%、Q2進捗：20%",
    "tasks": "完了タスク数：5、進行中：8...",
    "delayed": "期限超過タスク：2件（1.1 ヒアリング、1.2 要件整理）",
    "reviews": "差し戻し中：1件、確認待ち：0件"
  },
  "period_start": "2026-04-01",
  "period_end": "2026-06-30"
}
```

## 5. 内部処理

1. バリデーション：期間またはクォーターのどちらかが指定されていること
2. `quarter_id` 指定時は `quarter` から期間を取得
3. 対象期間の `task`・`quarter`・`review` データを集計
4. 各セクションのテキストを生成してレスポンスで返す（DB保存なし）
