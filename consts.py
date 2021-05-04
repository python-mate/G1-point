"""
Python やるときにいつもあって欲しい自分用モジュールです。
"""

# Built-in modules.
import os
import dotenv
import json


# .env をロードします。
# 本スクリプトは .env がなくても動きます。(そのための raise_error_if_not_found です。)
# NOTE: raise_error_if_not_found=False .env が見つからなくてもエラーを起こさない。
dotenv.load_dotenv(dotenv.find_dotenv(raise_error_if_not_found=False))


def get_env(keyname: str) -> str:
    """環境変数を取得します。
    GitHub Actions では環境変数が設定されていなくても yaml 内で空文字列が入ってしまう。空欄チェックも行います。

    Arguments:
        keyname {str} -- 環境変数名。

    Raises:
        KeyError: 環境変数が見つからない。

    Returns:
        str -- 環境変数の値。
    """
    _ = os.environ[keyname]
    if not _:
        raise KeyError(f'{keyname} is empty.')
    return _


LINE_CHANNEL_ACCESS_TOKEN = get_env('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = get_env('LINE_CHANNEL_SECRET')
LINE_G1_GROUP_ID = get_env('LINE_G1_GROUP_ID')
SLACK_CHANNEL_NAME = get_env('SLACK_CHANNEL_NAME')
SLACK_BOT_TOKEN = get_env('SLACK_BOT_TOKEN')

# GSPREAD_CREDENTIAL_JSON はただの文字列ではなく、 dict 定数として定義します。
# NOTE: これを使う ServiceAccountCredentials.from_json_keyfile_dict が dict 形式を求めるからです。
GSPREAD_CREDENTIAL_JSON = json.loads(get_env('GSPREAD_CREDENTIAL_JSON'))

if __name__ == '__main__':
    print(repr(LINE_CHANNEL_ACCESS_TOKEN))
    print(repr(LINE_CHANNEL_SECRET))
    print(repr(LINE_G1_GROUP_ID))
    print(repr(SLACK_CHANNEL_NAME))
    print(repr(SLACK_BOT_TOKEN))
    print(repr(GSPREAD_CREDENTIAL_JSON))
