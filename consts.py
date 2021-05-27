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

#LINE関係の環境変数
LINE_CHANNEL_ACCESS_TOKEN = get_env('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = get_env('LINE_CHANNEL_SECRET')
LINE_G1_GROUP_ID = get_env('LINE_G1_GROUP_ID')
#LINE_idを元にシート名の辞書を作成する。
# ATTENTION: LINE channel が変わるたび、
#            そして Group が変わるたび、
#            ここの user id は変化します。
#            そのたびにログを参照して、各々の user id を取得し、
#            この↓ dict を更新してください。
LINE_USER_ID_DICT = {
    "U07294e976ea424c3023889f937bbd88f" : "ササキ",
    "U97030df889f29fe5fa83fae98957a04d" : "コバヤシ",
    "U8983175d9d45162373fe3916b543d0f6" : "ウエハラ",
    "Uedab1cb5b1d9797691884a37044d0567" : "マツノ",
    "U2d60dfb30b93c289b2fb32d92a3f29fd" : "アカミネ",
    "U66bcf58c341aae32e40591b0abd1c963" : "フクヤマ",
    "U036190fdaed7c8747f930a98534c04b4" : "トヨシ",
    }

#Slack関係の環境変数
SLACK_CHANNEL_NAME = get_env('SLACK_CHANNEL_NAME')
SLACK_BOT_TOKEN = get_env('SLACK_BOT_TOKEN')


#GSPREAD関係の環境変数
# GSPREAD_CREDENTIAL_JSON はただの文字列ではなく、 dict 定数として定義します。
# NOTE: これを使う ServiceAccountCredentials.from_json_keyfile_dict が dict 形式を求めるからです。
GSPREAD_CREDENTIAL_JSON = json.loads(get_env('GSPREAD_CREDENTIAL_JSON'))
GSPREAD_SCOPE = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
#共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。スプレッドシートのd/〜〜/までをコピー。
GSPREAD_SPREADSHEET_KEY = '1pCTN9momqKlH4UtTRTf11yqXW2nI3grXUzRpbu6M6Tw'

if __name__ == '__main__':
    print(repr(LINE_CHANNEL_ACCESS_TOKEN))
    print(repr(LINE_CHANNEL_SECRET))
    print(repr(LINE_G1_GROUP_ID))
    print(repr((LINE_USER_ID_DICT)))
    print(repr(SLACK_CHANNEL_NAME))
    print(repr(SLACK_BOT_TOKEN))
    print(repr(GSPREAD_CREDENTIAL_JSON))
    print(repr(GSPREAD_SCOPE))
