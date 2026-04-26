# 【API設計書】WBS Excel出力API

## 1. 概要

WBSの内容をExcel（.xlsx）形式でエクスポートする。

## 2. エンドポイント

- **Method:** `POST`
- **Path:** `/api/v1/projects/{project_id}/export/excel/`
- **認証:** 必要 / **権限:** メンバー以上

## 3. リクエスト

```json
{
  "scope": "project",
  "quarter_id": null
}
```

- `scope`: `"project"` または `"quarter"`（`quarter` 指定時は `quarter_id` 必須）
- `quarter_id`: UUID または null

## 4. レスポンス

### 成功 (200 OK)

- `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `Content-Disposition: attachment; filename="wbs.xlsx"`
- ボディ：Excel バイナリ

## 5. 内部処理

1. JWT検証・メンバー確認
2. `scope` に応じてタスクを取得（プロジェクト全体 or クォーター単位）
3. openpyxl でExcelを生成
   - 列：WBS番号、タイトル（階層インデント）、担当者、開始日、終了日、工数、ステータス、進捗率
   - 階層はタイトル列をインデントで表現
4. バイナリをレスポンスで返す
