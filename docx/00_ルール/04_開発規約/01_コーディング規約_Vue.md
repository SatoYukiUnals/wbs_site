# コーディング規約（Vue.js）

フロントエンドの実装における規約を定める。プロジェクト固有の事情で本規約から外れる場合は、PRで理由を明記してレビューを受ける。

## 1. 基本方針

- **Composition API**（`<script setup>`）を標準とする
- **TypeScript** を使用する。`any` を避け、`unknown` や明示的な型を使う
- 1ファイル = 1コンポーネント（SFC：`.vue`）
- ESLint / Prettier の指摘は必ず解消してからPRを作成する

## 2. ファイル・ディレクトリ構成

```text
src/
├── views/           画面単位のコンポーネント（画面ID単位）
├── components/      画面を跨いで再利用する汎用コンポーネント
├── composables/     ロジック再利用用のフック（use〇〇）
├── stores/          Pinia ストア
├── api/             APIクライアント（axios等）
├── types/           型定義
├── utils/           ロジック非依存のユーティリティ
└── router/          ルート定義
```

### ■ 画面コンポーネントの配置

- 画面は `views/` 配下に **データ単位** のディレクトリで整理する
  - 例：`views/Contract/ContractListView.vue`（`SC-00-00_契約一覧`）
- 画面IDとコンポーネント名を対応させる

## 3. 命名規則

| 対象 | 規則 | 例 |
| :--- | :--- | :--- |
| コンポーネント名 | PascalCase + `View` / `Dialog` などのサフィックス | `ContractListView`、`PartnerSelectDialog` |
| ファイル名（SFC） | コンポーネント名と一致 | `ContractListView.vue` |
| Composable | `use` で始まるキャメルケース | `useContractSearch` |
| Pinia ストア | `use` で始まり `Store` で終わる | `useContractStore` |
| Props | キャメルケース。Template内ではケバブケースも可 | `initialValue` / `:initial-value` |
| Events | ケバブケース。動詞始まり | `@update:value`、`@submit` |
| 定数 | UPPER_SNAKE_CASE | `MAX_ITEM_COUNT` |
| Ref 変数 | キャメルケース。リアクティブな値には型をつける | `const count = ref<number>(0)` |

## 4. コンポーネント実装

### ■ `<script setup>` の順序

```vue
<script setup lang="ts">
// 1. import（型→外部ライブラリ→プロジェクト内の順）
import type { Contract } from '@/types/contract'
import { ref, computed } from 'vue'
import { useContractStore } from '@/stores/contract'

// 2. Props / Emits
const props = defineProps<{ id: number }>()
const emit = defineEmits<{ (e: 'submit', value: Contract): void }>()

// 3. Store / Composable
const store = useContractStore()

// 4. state（ref / reactive）
const isLoading = ref(false)

// 5. computed
const isEditable = computed(() => !isLoading.value)

// 6. methods（関数）
const handleSubmit = () => { ... }

// 7. lifecycle / watch
onMounted(() => { ... })
</script>
```

### ■ Props

- **型は必ず TypeScript で明示** する（`defineProps<{...}>()`）
- デフォルト値は `withDefaults` を使う
- 破壊的変更を防ぐため、オブジェクトや配列のPropsは直接変更しない

### ■ 一覧画面の検索条件は URL Query で管理する

一覧画面（`SC-DD-00`）では、検索条件・ページ番号・ソート条件を **URLのクエリパラメータ** で保持する。
画面遷移しても条件が復元でき、URLの共有・ブラウザバックにも対応できる。

```ts
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// クエリから検索条件を復元
const keyword = computed(() => route.query.keyword as string ?? '')
const page = computed(() => Number(route.query.page ?? 1))
const status = computed(() => route.query.status as string ?? 'all')

/**
 * 検索条件をURLクエリに反映する
 * @param params 新しい検索条件
 */
const updateQuery = (params: Record<string, string | number>) => {
  router.push({ query: { ...route.query, ...params } })
}
```

- 一覧画面では `ref` で検索条件を持たず、URLクエリを唯一の真実（single source of truth）とする
- 未指定時のデフォルト値は `??` で補う
- 画面を離れる操作（リンククリック・ブラウザバック）での状態復元は Vue Router に任せる

### ■ API呼出しのコメント

API を呼び出す箇所には、**何のAPIを呼んでいるか** を特定できるコメントを付ける。
画面仕様書・API設計書との対応を取りやすくするため、`API名` または `メソッド + パス` を明記する。

```ts
/**
 * 契約一覧を取得する
 * @param query 検索条件
 */
const fetchContracts = async (query: ContractQuery) => {
  // 契約一覧取得API：GET /api/v1/contracts/
  const { data } = await api.get('/api/v1/contracts/', { params: query })
  return data
}

/**
 * 契約を新規登録する
 */
const createContract = async (payload: ContractPayload) => {
  // 契約登録API：POST /api/v1/contracts/
  const { data } = await api.post('/api/v1/contracts/', payload)
  return data
}
```

- 関数のJSDocには **何をする関数か** を、API呼出し行の上に **どのAPIを呼ぶか** を書く（役割を分離）
- 複数APIを連続で呼ぶ場合はそれぞれの呼出し行にコメントを付ける

### ■ コメント（computed / methods / lifecycle）

**computed・methods・lifecycle** には決まった形式のコメントを付与する。何を目的にした処理か、引数・戻り値を明示して、実装を読まずに意図が把握できるようにする。

```ts
/**
 * 検索条件に合致する契約一覧を返す
 * @param contracts 全件の契約配列
 * @param keyword 検索キーワード（前方一致）
 * @returns 絞り込まれた契約配列
 */
const filteredContracts = computed(() => {
  return contracts.value.filter(c => c.name.startsWith(keyword.value))
})

/**
 * 『登録』ボタン押下時の処理
 * バリデーション後、登録APIを呼び出して一覧画面へ遷移する
 */
const handleSubmit = async () => { ... }

/**
 * マウント時の初期データ取得
 * 所有者・所有組織の選択肢をAPIから取得する
 */
onMounted(async () => { ... })
```

- 1行で収まる補足コメントは `//` でもよい
- **コメントなしの関数は原則NG**（一目で意図が分かる getter 等を除く）

#### ▶ 分岐のコメント

`if` / `else` / `switch` など条件分岐を行う場合、**各分岐の直前に条件の意図をコメント** で記載する。
コードを読まずに、どんな条件でどの処理が走るかを把握できるようにする。

```ts
/**
 * 『登録』ボタン押下時の処理
 */
const handleSubmit = async () => {
  // 必須項目が未入力の場合は早期リターン
  if (!form.value.name) {
    showError('契約名を入力してください')
    return
  }

  // 新規登録か更新かで呼び出すAPIを切り替える
  if (props.mode === 'create') {
    // 新規登録：契約作成APIを呼び出す
    await contractStore.create(form.value)
  } else {
    // 更新：契約更新APIを呼び出す
    await contractStore.update(props.id, form.value)
  }
}
```

```ts
// switch でも同様に、各 case の条件・意図を明記する
switch (status) {
  // 未承認：承認待ちアイコンを表示
  case 'pending':
    return 'clock'
  // 承認済み：チェックアイコンを表示
  case 'approved':
    return 'check'
  // 却下：バツアイコンを表示
  case 'rejected':
    return 'x'
  // その他：デフォルトアイコン
  default:
    return 'circle'
}
```

- 三項演算子でも、意図が読み取りにくい場合は上にコメントを付ける
- 単純な `if (!user) return` のような自明なガードは省略してよい

### ■ Template

- `v-if` と `v-for` を **同じ要素に書かない**（計算量の問題）
- `v-for` には必ず `:key` を指定する（インデックスではなく一意なIDを推奨）
- 複雑な条件式は `computed` に切り出す
- `data-testid` を付与する（結合テスト・E2Eテスト用）

#### ▶ 属性の記載順

HTML要素・コンポーネントに複数の属性がある場合、以下の順序で記載する。
（[Vue公式スタイルガイド](https://ja.vuejs.org/style-guide/rules-recommended.html#element-attribute-order) に準拠）

| 順序 | 区分 | 例 |
| :--- | :--- | :--- |
| 1 | 定義（どのコンポーネントか） | `is` |
| 2 | リストレンダリング | `v-for` |
| 3 | 条件分岐 | `v-if`、`v-else-if`、`v-else`、`v-show`、`v-cloak` |
| 4 | レンダリング修飾子 | `v-pre`、`v-once` |
| 5 | グローバル参照 | `id` |
| 6 | ユニーク属性 | `ref`、`key` |
| 7 | 双方向バインディング | `v-model` |
| 8 | その他の属性 | `class`、`data-testid`、`placeholder`、`:disabled` など |
| 9 | イベント | `@click`、`@input`、`v-on:xxx` |
| 10 | コンテンツ | `v-html`、`v-text` |

```vue
<!-- OK -->
<input
  v-if="isEditable"
  id="contract-name"
  ref="nameInput"
  v-model="form.name"
  class="border rounded px-2"
  data-testid="contract-name-input"
  placeholder="契約名を入力"
  @blur="validateName"
/>

<!-- NG：id が class より後、@blur が data-testid より前 -->
<input
  class="border rounded px-2"
  @blur="validateName"
  id="contract-name"
  data-testid="contract-name-input"
  v-model="form.name"
/>
```

#### ▶ 自己終了タグ

子要素を持たない要素は **自己終了タグ** で記載する（不要な `</〇〇>` を書かない）。

```vue
<!-- OK：子要素なし -->
<input type="text" />
<img src="/logo.png" alt="ロゴ" />
<MyButton label="登録" />

<!-- NG：空の終了タグを書いている -->
<input type="text"></input>
<MyButton label="登録"></MyButton>
```

ただし、ネイティブHTML要素（`<div>`・`<span>` など）で子要素が存在しうる場合は通常の開始・終了タグを使用する。

## 5. Composables

- **ロジックの再利用** が発生したら Composable に切り出す
- 1 Composable = 1 関心事
- 返り値は **オブジェクト** で返し、`readonly` で外部からの変更を防ぐ

```ts
export const useContractSearch = () => {
  const keyword = ref('')
  const results = ref<Contract[]>([])
  const search = async () => { ... }
  return { keyword, results: readonly(results), search }
}
```

## 6. 状態管理（Pinia）

- **画面を跨いで共有する state** のみストアに置く（単一画面で完結するものは `ref` で十分）
- Setup Store（`defineStore('xxx', () => {...})`）を標準とする
- ストア内で副作用（API呼出し等）を行う場合、`async` 関数として定義しエラー処理を内包する

## 7. スタイル

- スタイリングは **Tailwind CSS のユーティリティクラス** で行う
- **`<style>` ブロックは使用しない**（`<style>` / `<style scoped>` / `<style lang="scss">` 等、すべて禁止）
- **インライン `style=""` も使用しない**
- Tailwind のユーティリティクラスの並び順は公式の推奨順（レイアウト → Box → Typography → Color …）に従う
- Tailwind で表現できないスタイルがある場合は、共通コンポーネント化・`@apply`（`tailwind.config` / グローバルCSS側）で解決する

## 8. エラーハンドリング

- API呼出しは `try / catch` で囲み、エラー時は **共通エラーハンドラ** に委譲する
- ユーザー向けエラー表示は [エラーメッセージ.md](../02_ドキュメントガイドライン/エラーメッセージ.md) に従う
- `console.error` は本番に残さない（ログは共通ログ関数経由）

## 9. テスト

- **コンポーネントテスト**：Vitest + `@vue/test-utils`
- テストファイルは対象と同階層の `__tests__/` に配置
- `data-testid` でDOM要素を特定する（クラス名やテキストは変わりやすいため避ける）

## 10. 禁止事項

- `any` の濫用
- `v-html` の使用（XSS対策。やむを得ない場合はサニタイズ処理を挟む）
- グローバル変数の追加
- `console.log` の本番残留
- **`<style>` ブロック（`scoped` 含む）・インライン `style=""` の使用**（Tailwind のみで記述する）
- コメントアウトコードの残留（使わない場合は削除）
