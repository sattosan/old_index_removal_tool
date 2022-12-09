# Elasticsearchの古いindex削除ツール
## 概要
Elasticsearch内にあるindexを以下の観点で削除するツールです。

- 作成してからxx日以上経過
- aliasから参照されていない

## デモ
TODO

## 機能
- aliasに紐付かない古いindexを削除する
  - 削除対象はindex名のパターンを指定して制限可能
  - 削除対象から除外設定が可能
- 削除件数の表示
- 削除対象のindexサイズを表示

## 依存パッケージ
利用する依存パッケージは以下の通りです。

- python 3.10
- elasticsearch = 7.17.0
- python-decouple = 3.6

接続するElasticsearchのバージョンによって`elasticsearch`のバージョンを合わせる必要があるので適宜変更してください。

## インストール

### 準備
リポジトリをクローンして依存パッケージをインストールします

```bash
$ git clone https://github.com/sattosan/old_index_removal_tool.git
$ cd old_index_removal_tool
$ poetry install
```

### 環境変数の設定
色々な設定が記載されている`.env`のバックアップファイルをコピーして.envを作成する

```bash
cp ./src/.env.bk ./src/.env
```

`.env`の中は適宜いい感じに変えてください。

## ユースケース
### ワイルドカードを使って削除対象を制御
例えば、index名が`test_xxx`のようにあるパターンに該当するindexを削除したい場合、`.env`にて以下のように設定することで削除対象を制御できます。

```bash
TARGET_INDICES="test_*"
```

### 複数のパターンを指定
上のユースケースに関連した機能ですが、複数のパターンを指定することもできます。

```bash
TARGET_INDICES="hoge_*,fuga_*,*_test"
```

この例では、`hoge_xxx`、`fuga_xxx`、`xxx_test`のパターンに一致するindexが削除されます。


### 削除対象から特定のindexを除外したい
例えば、`test_index`というindexを削除したくない場合、`.env`にて以下のように設定することでスキップできます。

```bash
EXCLUDED_INDICIES="test_index"
```

## 実行
以下のコマンドでツールを実行できます

```bash
$ poetry run python ./src/main.py
================================
test-1
test-2
test-4
test-5
合計：4件
サイズ：8.12 GB
================================
Delete all indices? (Y/N): Y
=> Target indices have deleted in http_auth.
Exit this program.
```

実行すると削除対象のindexがあれば表示されます。ここで`Y`と押すと表示されたindexが全て削除されます。

削除対象のindexがない場合は表示されず、プログラムは終了します。
