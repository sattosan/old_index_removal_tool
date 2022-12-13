import math
import sys
from datetime import datetime

from decouple import config
from elasticsearch import Elasticsearch

# 現在時刻
now: datetime = datetime.now()
# 除外するindex
excluded_indicies: list[str] = config("EXCLUDED_INDICIES").split(",")


# 削除可能なindexを選択
def select_deletable_indices(indices):
    return dict(filter(
        lambda index: is_deletable_index(index[0], index[1]),
        indices.items()))


# 削除可能なindexか判定
def is_deletable_index(index_name: str, property) -> bool:
    # 初期のindexとaliasに紐づくindexは除外
    if index_name.startswith(".") or property["aliases"]:
        return False

    # その他、除外するindexがあればスキップ
    if index_name in excluded_indicies:
        return False

    # 寿命を超えたindexが削除対象
    return is_not_alive_index(property)


def is_not_alive_index(property) -> bool:
    # datetimeでミリ秒のEpoch Timeが扱えないので秒に変換
    formatted_epoch_time = int(property["settings"]
                               ["index"]["creation_date"]) / 1000
    creation_datetime = datetime.fromtimestamp(formatted_epoch_time)
    # 経過した日数を算出
    elapsed_days = (now - creation_datetime).days

    # 寿命を超えていた場合
    return int(config("MAX_INDEX_AGE_DAYS")) < elapsed_days


def switch_es_client_by_env() -> (Elasticsearch | None):
    match config('APP_ENV'):
        case "local":
            return Elasticsearch(hosts=[config("ELASTICSEARCH_LOCAL_HOST")])
        case "http_auth":
            return Elasticsearch(
                hosts=[config("ELASTICSEARCH_HOST")],
                http_auth=(config("ELASTICSEARCH_ID"), config("ELASTICSEARCH_PASSWORD")))
        case _:
            return None


# bytesを適切なサイズ表記に変換
def convert_size(size: int) -> str:
    units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")
    i = math.floor(math.log(size, 1024)) if size > 0 else 0
    size = round(size / 1024 ** i, 2)

    return f"{size} {units[i]}"


# 指定された複数のindexサイズを取得
def get_indices_size(es: Elasticsearch, indices: list[str]) -> int:
    total_size_in_bytes = 0
    for i in range(0, len(indices), 100):
        # 大量のindexを指定するとサイズオーバーでリクエストできないので分ける
        indices_stats = es.indices.stats(
            index=indices[i: i + 100], filter_path=['_all'])
        total_size_in_bytes += indices_stats['_all']['total']['store']['size_in_bytes']

    return total_size_in_bytes


def main():
    # 準備
    es: Elasticsearch | None = switch_es_client_by_env()
    if es is None:
        print("Please set enviroment variable APP_ENV.")
        print("Exit this program.")
        sys.exit(1)

    target_indices: list[str] = config("TARGET_INDICES").split(",")

    # 削除対象のindexを抽出
    deletable_indices = select_deletable_indices(
        es.indices.get(index=target_indices))

    if not deletable_indices.keys():
        print(f"Target index is not found in {config('APP_ENV')}.")

    # 結果の表示
    print("================================")
    for index in deletable_indices:
        print(index)
    print(f"合計：{len(deletable_indices.keys())}件")

    # 削除対象のindexサイズを取得
    total_size_in_bytes: int = get_indices_size(
        es, list(deletable_indices.keys()))
    print(f"サイズ：{convert_size(total_size_in_bytes)}")
    print("================================")

    # 削除するかの確認
    key_input: str = input("Delete all indices? (Y/N): ")

    # 削除 or 終了
    if key_input in ["Y", "y", "yes"]:
        print(f"=> Target indices have deleted in {config('APP_ENV')}.")
        es.indices.delete(index=list(deletable_indices.keys()))
    print("Exit this program.")


if __name__ == "__main__":
    main()
