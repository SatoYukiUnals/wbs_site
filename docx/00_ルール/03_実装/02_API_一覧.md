# 実装：一覧API

[02_API.md](./02_API.md) の共通ルールに加え、一覧API（`list` アクション）では以下を守る。

## 1. ■設計方針

### ファイル構成

一覧APIは役割ごとにファイルを分割する。各APIモジュール（`ordering/{app}/api/{機能名}/`）に以下を配置する。

| ファイル | 役割 | 必須 |
|------|------|:---:|
| `views.py` | ViewSet（`list` メソッドのエントリポイント） | ✅ |
| `serializers.py` | Request / Content / Response シリアライザー | ✅ |
| `query.py` | 検索・絞り込み・ソート・アノテーション等のクエリロジック（`{機能名}ListQuery` クラス） | ✅ |
| `sort_key.py` | ソートキーのEnum（APIが受け付けるソート値を定義） | ✅ |
| `pagination.py` | ページネーション（`CommonListPagination` を継承した独自クラスが必要な場合のみ） | - |
| `page_size.py` | ページサイズのEnum（独自のページサイズ候補が必要な場合のみ） | - |

- ViewSet はクエリビルドや検索条件の分岐を直接書かず、必ず `query.py` の Query クラスに委譲する。
- ファイル名は snake_case に統一する（`sortkey.py`・`sortkeys.py` などの揺れは不可）。

### クエリパラメータ

- 検索・絞り込み条件は **クエリパラメータ** で受け取る。リクエストボディやパスパラメータは使わない。
- 例：`/api/v1/orders/?status=active&keyword=test`

### クエリパラメータのバリデーション

- クエリパラメータは `RequestSerializer`（`serializers.Serializer` のサブクラス）でバリデーションする。
- `validate_serializer_or_error` を使ってエラーレスポンスを返す。

```python
def list(self, request, *args, **kwargs):
    serializer = OrderListRequestSerializer(data=request.query_params)
    error_response = validate_serializer_or_error(serializer)
    if error_response:
        return error_response
    return super().list(request, *args, **kwargs)
```

### ページネーション

- 一覧APIには必ずページネーションを設定する。
- `CommonListPagination`（`ordering/contract/utils/paginations.py`）を継承して使う。
- レスポンス形式は以下で統一されている。

```json
{
  "num_of_pages": 5,
  "num_of_items": 100,
  "current_page": 1,
  "num_of_items_per_page": 20,
  "results": [...]
}
```

### N+1対策

- 一覧APIでは以下のいずれかでN+1を避ける：
  - Query クラスで `annotate(field=F("related__field"))` や `Subquery` / `Exists` を使ってフラットな1クエリに集約する（推奨）
  - ネスト済みのオブジェクトを返す必要がある場合は `select_related`（ForeignKey）・`prefetch_related`（逆参照・ManyToMany）を明示する

### シリアライザーの命名規則

一覧APIは以下の3クラスをセットで実装する。

| 種別 | 命名 | 用途 |
|------|------|------|
| リクエスト | `{機能名}ListRequestSerializer` | クエリパラメータ（検索・絞り込み条件・ページング） |
| 1件分のデータ | `{機能名}ListContentSerializer` | レスポンスの `results` 配列1件分 |
| レスポンス全体 | `{機能名}ListResponseSerializer` | `ListResponseSerializer` を継承し、`results = {機能名}ListContentSerializer(many=True)` を定義 |

```python
class OrderListRequestSerializer(serializers.Serializer):
    status = serializers.CharField(required=False)
    keyword = serializers.CharField(required=False)


class OrderListContentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)


class OrderListResponseSerializer(ListResponseSerializer):
    results = OrderListContentSerializer(many=True)
```

- `Request` / `Response` のみ（`Serializer` なし）や、`ListPageContentSerializer` などの旧表記は新規実装で使わない。

---

## 2. ■作業手順

- [ ] **RequestSerializerの実装**: クエリパラメータ用の `RequestSerializer` をAPI設計書に沿って実装します。
- [ ] **レスポンス用シリアライザーの実装**: `ListResponseSerializer` を継承したレスポンスシリアライザーを実装します。
- [ ] **ビューの実装**: `list` メソッドで `RequestSerializer` によるバリデーション・テナント分離・`select_related`/`prefetch_related` を実装します。
- [ ] **ページネーションの設定**: `CommonListPagination` を `pagination_class` に設定します。
- [ ] **単体テストの実装・実行**: 検索条件・ページングの境界値テストを実装し、全件グリーンであることを確認します。

---

## 3. ■セルフチェック

- [ ] クエリパラメータが `RequestSerializer` でバリデーションされている
- [ ] ページネーションが設定され、レスポンス形式が統一仕様と一致している
- [ ] N+1クエリが発生していない（`annotate` / `select_related` / `prefetch_related` 等で解消されている）
- [ ] `list` または `get_queryset` で `filter(tenant=request.user.tenant)` によるテナント分離が行われている
