# コーディング規約（Django）

バックエンドの実装における規約を定める。プロジェクト固有の事情で本規約から外れる場合は、PRで理由を明記してレビューを受ける。

## 1. 基本方針

- **Python 3.x + Django + Django REST Framework（DRF）** を標準構成とする
- **PEP 8** に準拠する（`black` / `ruff` / `isort` で自動フォーマット）
- 型ヒントを積極的に使用する（`mypy` で検証）
- 1関数 / 1メソッドは **単一責任** を守る（長すぎる関数は分割）

## 2. ファイル・ディレクトリ構成

```text
apps/
├── contract/              アプリ単位で分割（データ単位と対応）
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── services.py         ビジネスロジック（model/viewに収まらないもの）
│   ├── validators.py       カスタムバリデーション
│   ├── permissions.py      権限制御
│   ├── selectors.py        複雑なクエリ（任意）
│   └── tests/
│       ├── test_models.py
│       ├── test_views.py
│       └── test_services.py
└── common/                複数アプリで共有するユーティリティ
```

### ■ アプリ分割の基準

- **データ単位** で分ける（契約・請求・注文 …）
- 横串の処理は `common/` や独立アプリに切り出す
- アプリ間の依存は最小限に。循環依存は禁止

## 3. 命名規則

| 対象 | 規則 | 例 |
| :--- | :--- | :--- |
| アプリ名 | snake_case 単数形 | `contract`、`partner` |
| モデル名 | PascalCase 単数形 | `Contract`、`Partner` |
| モデルフィールド | snake_case | `ordered_at`、`customer_id` |
| Serializer | モデル名 + `Serializer` | `ContractSerializer` |
| ViewSet | モデル名 + `ViewSet` | `ContractViewSet` |
| 関数 | snake_case | `create_contract` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| プライベート関数・メソッド | `_` 始まり | `_build_query` |
| マイグレーション | 番号 + snake_case | `0001_initial.py`、`0042_add_status_to_contract.py` |

## 4. コメント

### ■ 関数・メソッドの docstring

すべての関数・メソッドに **docstring** を付ける。何をする処理か、引数・戻り値・発生例外を明示して、実装を読まずに意図が把握できるようにする。
フォーマットは **Google スタイル** または **reST スタイル** のいずれかでプロジェクト内で統一する。

```python
def create_contract(payload: dict, user: User) -> Contract:
    """契約を新規登録する。

    バリデーション後、契約レコードを作成してトランザクション確定する。

    Args:
        payload: 契約入力値（バリデーション済み）
        user: 操作ユーザー

    Returns:
        作成された契約オブジェクト

    Raises:
        ContractDuplicationError: 同名の契約が既に存在する場合
    """
    ...
```

- ViewSet / Serializer / Service 関数のすべてに付与する
- 1行で収まる簡単な処理でもサマリー（最初の1行）は必ず書く
- **docstring なしの関数は原則NG**（自明な getter 等を除く）

### ■ 分岐のコメント

`if` / `else` / `match` などの条件分岐を行う場合、**各分岐の直前に条件の意図をコメント** で記載する。

```python
def update_contract_status(contract: Contract, new_status: str, user: User) -> None:
    """契約ステータスを更新する。"""
    # 現在ステータスが completed の場合は変更不可
    if contract.status == "completed":
        raise ContractFrozenError()

    # 管理者は任意のステータスに遷移可能
    if user.is_admin:
        contract.status = new_status
    # 一般ユーザーは承認待ち → 承認済みへの遷移のみ許可
    elif contract.status == "pending" and new_status == "approved":
        contract.status = new_status
    else:
        raise PermissionDeniedError()

    contract.save()
```

```python
# match でも同様に、各 case の条件・意図を明記する
match status:
    # 未承認：承認待ちアイコンを表示
    case "pending":
        return "clock"
    # 承認済み：チェックアイコンを表示
    case "approved":
        return "check"
    # その他：デフォルトアイコン
    case _:
        return "circle"
```

- 自明なガード（`if obj is None: return` など）は省略可

### ■ APIエンドポイントのコメント（ViewSet / APIView）

ViewSet のアクションメソッド、または APIView の `get` / `post` メソッドには、**画面ID・API名・対応する画面仕様書** を docstring に明記する。

```python
class ContractViewSet(viewsets.ModelViewSet):
    """契約関連のAPIエンドポイント。"""

    def list(self, request, *args, **kwargs):
        """契約一覧取得API。

        対応画面：SC-00-00 契約一覧
        API名：契約一覧取得API
        GET /api/v1/contracts/
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """契約登録API。

        対応画面：SC-00-01 契約登録
        API名：契約登録API
        POST /api/v1/contracts/
        """
        return super().create(request, *args, **kwargs)
```

- 対応画面・API名・エンドポイントの3点セットで記載する
- 画面仕様書／API設計書と**双方向に参照可能**にすることが目的

## 5. 一覧系APIの検索・ページング

一覧取得API（`list` アクション）の検索条件・ページングは、**URLのクエリパラメータ** として受ける（POSTボディではない）。
DRF の `filter_backends` / `pagination_class` を活用する。

```python
class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = ContractFilter  # 絞り込み（status, customer_id 等）
    search_fields = ["name", "order_no"]  # 部分一致検索
    ordering_fields = ["created_at", "order_date"]  # ソート対象
    pagination_class = StandardResultsSetPagination
```

- フロント側の検索条件（URLクエリ）とそのまま噛み合うようにする
- 絞り込みロジックが複雑な場合は `FilterSet` クラスに集約し、ViewSet には書かない
- **POSTで検索条件を受けるのは禁止**（キャッシュ・ブックマーク不可になるため）

## 6. モデル

### ■ 設計

- すべてのモデルは [04_DB設計規約.md](./04_DB設計規約.md) に従う
- 共通フィールド（`created_at`、`updated_at`、`created_by`、`updated_by`）は **抽象基底モデル** を継承
- **論理削除** を原則とする（`is_deleted` または `deleted_at`）

### ■ メソッド

- モデルに固有のロジックは **モデルメソッド** として実装する（例：`contract.is_active()`）
- 複数モデルに跨るロジックは **services.py** に実装

## 5. View / ViewSet

- **CBV（Class-Based View）** を基本とし、DRFの `ModelViewSet` / `GenericAPIView` を活用する
- ビジネスロジックは View に書かず、**services.py** に委譲する
- ViewSet の肥大化を避け、複雑になったら mixin / service に分離する

### ■ ステータスコード

- **200 OK**：取得・更新成功
- **201 Created**：新規作成成功
- **204 No Content**：削除成功
- **400 Bad Request**：バリデーションエラー
- **401 Unauthorized**：未認証
- **403 Forbidden**：権限不足
- **404 Not Found**：リソース未存在
- **409 Conflict**：排他エラー・重複
- **500 Internal Server Error**：サーバーエラー

## 6. Serializer

- **バリデーションは Serializer に集約** する（`validate_xxx` / `validate`）
- 複雑なビジネスバリデーションは `services.py` の関数を呼び出す
- 入力用・出力用で別Serializerに分けるのが望ましい（`ContractCreateSerializer` / `ContractDetailSerializer`）

## 7. トランザクション

- DB更新を伴う処理は **`transaction.atomic`** で囲む
- View ではなく **services.py** の関数単位でトランザクションを張る
- トランザクション中で外部API・メール送信を行わない（完了後に実行）

## 8. 認証・認可

- 認証は Django 標準 + DRF の仕組みに乗る
- 権限チェックは **`permissions.py`** に切り出し、ViewSet の `permission_classes` で指定
- 認可ロジックを View 内に直書きしない

## 9. エラーハンドリング

- 予想されるビジネスエラーは **カスタム例外**（`ContractNotFoundError` 等）を定義して投げる
- DRF の **カスタム例外ハンドラ** で共通レスポンス形式（メッセージID・メッセージ内容）に変換する
- エラーレスポンスの形式は [03_API設計規約.md](./03_API設計規約.md) を参照

## 10. ロギング

- `logging.getLogger(__name__)` を使う
- ログレベルを使い分ける：
  - `DEBUG`：開発時のみの詳細情報
  - `INFO`：正常終了・主要イベント
  - `WARNING`：想定内だが通知したい状況
  - `ERROR`：異常終了・リカバリ可能
  - `CRITICAL`：システム停止レベル
- **個人情報・認証情報をログに出力しない**
- 構造化ログ（JSON形式）を推奨

## 11. テスト

- **pytest + pytest-django** を標準とする
- テストは `tests/` 配下に配置、対象と対応関係を持たせる（`test_models.py` / `test_views.py`）
- **境界値・異常系・正常系** を網羅する
- 外部APIやメール送信はモック化する
- DBアクセスは `@pytest.mark.django_db` を付与、fixture でデータ準備する

## 12. 禁止事項

- ORM の N+1 クエリ（`select_related` / `prefetch_related` で回避）
- View 内での生SQL（`.raw()`）の濫用。使う場合はコメントで理由を明記
- Print 文の本番残留（ロガー経由にする）
- 例外の握りつぶし（`except: pass` のみは禁止、最低限ログ出力する）
- 密度の高いロジックを View・Serializer に書く（services へ逃がす）
- マジックナンバー・マジックストリング（定数化・Enum化）
- 個人情報・パスワード・トークンの平文ログ出力
