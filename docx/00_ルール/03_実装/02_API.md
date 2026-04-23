# 実装：API（シリアライザー・ビュー・単体テスト）

一覧APIに固有のルール（クエリパラメータのバリデーション、ページネーション、N+1対策など）は [02_API_一覧.md](./02_API_一覧.md) を参照。

## 1. ■設計方針

### URL設計

| 種別 | 方式 | 例 |
|------|------|----|
| 一覧・検索・絞り込み | クエリパラメータ（`?key=value`） | `/api/v1/orders/?status=active&keyword=test` |
| 特定リソースの取得・更新・削除 | パスパラメータ | `/api/v1/orders/123/` |

- URLの登録は `config/urls.py` の `SimpleRouter` に追加する。
- CRUD（一覧・取得・登録・更新・削除）のエンドポイントは `ModelViewSet` を使う。

```python
router.register(r"api/v1/orders", api_views.OrderViewSet, basename="orders")
```

### ViewSetの選択

| 種別 | 使いどころ |
|------|-----------|
| `ModelViewSet` | 基本はこれを使う（モデル単位のAPI） |
| `APIView` | 複数モデルを跨ぐ等、`ModelViewSet` に収まらないカスタム処理が必要な場合 |

- アクションによってシリアライザーを切り替える場合は `get_serializer_class()` を使う。

```python
def get_serializer_class(self):
    if self.action == "create":
        return OrderCreateSerializer
    elif self.action == "list":
        return OrderListSerializer
    return OrderDetailSerializer
```

### テナント分離

- `list` メソッドまたは `get_queryset` で必ず `filter(tenant=request.user.tenant)` を行う。
- クエリを Query クラスに切り出す場合も、Query クラス内でテナント分離を行う。

```python
def get_queryset(self):
    return Order.objects.filter(tenant=self.request.user.tenant)
```

### シリアライザー

- `ModelSerializer` を基本とする。
- 読み取り専用フィールドはフィールド定義に `read_only=True` を付ける（`Meta.read_only_fields` ではなく個別指定）。
- 一覧用・詳細用・登録用など用途が異なる場合は別クラスに分け、`get_serializer_class()` で切り替える。
- ネストされたシリアライザーは読み取り専用とし、書き込みはIDフィールドで受け取る。

#### 命名規則

- すべてのシリアライザーはクラス名末尾を `Serializer` にする（`Request` / `Response` 単独での命名は不可）。

| 種別 | 命名 | 用途 |
|------|------|------|
| モデル汎用 | `{モデル名}Serializer` | `ModelSerializer` を使うモデル単位のシリアライザー |
| リクエスト | `{機能名}RequestSerializer` | リクエストボディ・クエリパラメータのバリデーション |
| レスポンス | `{機能名}ResponseSerializer` | レスポンス全体 |
| 詳細取得 | `{機能名}DetailSerializer` | 詳細取得APIのレスポンス |
| 読み取り専用 | `ReadOnly{モデル名}Serializer` | 書き込み不可の読み取り専用シリアライザー |

- 一覧API用シリアライザーの命名は [02_API_一覧.md](./02_API_一覧.md) を参照。

### 単体テスト

- テストデータは **Factory（`factory_boy` の `DjangoModelFactory`）で実データとしてDBに作成する**。モデル・ORM・クエリをモックしない。
- データを変更・登録・削除するAPIのテストでは、**変更対象となるすべてのテーブルの全レコードを検証する**（更新されたレコードだけでなく、更新されていないレコード・関連テーブルのレコードも対象）。意図しない副作用を検知するため。
- Factory は `ordering/{app}/tests/factories/` 配下に、モデル単位でファイルを分けて定義する。

---

## 2. ■作業手順

- [ ] **シリアライザーの実装**: RequestSerializer（クエリパラメータ用）・レスポンス用シリアライザーをAPI設計書に沿って実装します。
- [ ] **ビューの実装**: ViewSetの種別を選択し、テナント分離・認証・認可・ビジネスロジックをAPI設計書・機能仕様書に沿って実装します。
- [ ] **URLルーティングの登録**: `config/urls.py` の `SimpleRouter` に実装したViewSetを追加します。
- [ ] **エラーハンドリングの実装**: バリデーションエラー・例外発生時に、エラーメッセージ仕様書に定義されたメッセージ・ステータスコードを返すことを確認します。
- [ ] **単体テストの実装・実行**: 単体テスト仕様書に基づき、正常系・異常系・境界値のテストケースを実装し、全件グリーンであることを確認します。

---

## 3. ■セルフチェック

### 設計との整合

- [ ] エンドポイント・HTTPメソッドがAPI設計書と一致している
- [ ] リクエスト・レスポンスのフィールド・型・必須フラグがAPI設計書と一致している
- [ ] ビジネスロジック・条件分岐が機能仕様書と一致している
- [ ] エラーメッセージ・HTTPステータスコードがエラーメッセージ仕様書と一致している

### セキュリティ

- [ ] 認証・認可のチェックが適切な箇所で行われている
- [ ] `list` または `get_queryset` で `filter(tenant=request.user.tenant)` によるテナント分離が行われている
- [ ] 生クエリを使用する場合、パラメータバインディングによるSQLインジェクション対策が行われている

### テスト

- [ ] 単体テスト仕様書に定義された全テストケースが実装・実行されており、すべてパスしている
- [ ] 正常系・異常系・境界値がテストで網羅されている
- [ ] 既存の単体テストが全件パスしており、デグレードがないことを確認している
- [ ] テストデータを Factory で実データとして作成している（モデル・ORM・クエリをモックしていない）
- [ ] データ変更系APIでは、変更対象となるすべてのテーブルの全レコードを検証している
