"""
■ ご依頼その4
このプログラムを実行……

python netkeiba_scrape_arguments_retreiver.py

したとき、一番下で retreive 関数に渡している日付に、
(スクレイピングしてほしい)レースが存在するなら、
URL を作成するための情報を return してほしいです。
そんなことが出来る関数 retreive を作ってください!
"""

#必要モジュールの準備
import pandas as pd
import gspread
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe

# User modules.
import consts

#競馬場別で振分けされているコードの辞書を作成。
racecourse_code_dict = {
    '札幌':'01',
    '函館':'02',
    '福島':'03',
    '新潟':'04',
    '東京':'05',
    '中山':'06',
    '中京':'07',
    '京都':'08',
    '阪神':'09',
    '小倉':'10',
    }

#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

#認証情報設定
# NOTE: もともとは from_json_keyfile_name で json ファイルから credentials を作っていました。
#       しかし秘密鍵である json ファイルを repository に含めると、 GitHub で公開できません!
#       なので from_json_keyfile_dict に変更して、 json ファイルがなくても動くようにしました。
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    consts.GSPREAD_CREDENTIAL_JSON,
    scope,
)

#OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)

#共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
SPREADSHEET_KEY = '1pCTN9momqKlH4UtTRTf11yqXW2nI3grXUzRpbu6M6Tw'#スプレッドシートのd/〜〜/までをコピー。

#ワークシート名を指定。
SP_SHEET = '指定レース情報'

#共有設定したスプレッドシートを開く
sh = gc.open_by_key(SPREADSHEET_KEY)

#ワークシートの選択
worksheet = sh.worksheet(SP_SHEET)

#スプレットシートの全データを取得
data = worksheet.get_all_values()

#上から２列目を無視上から１列目をカラムとする。indexは開催年月日とする。
df = pd.DataFrame(data[2:],columns=data[1]).set_index('開催年月日')

#開催年月日リストを作成。
holding_date_list = list(df.index.values)

def retreive(yyyymmdd):

    # year: str, racetrack_code: str, times: str, date: str, race_number: str

    #yyyymmdd⇨yyyy/mm/ddの形へ変換。
    yyyymmdd = yyyymmdd.replace('-','/')

    #スプレッドシートの開催年月日と呼び出された引数が存在するか判定する。
    if yyyymmdd in holding_date_list:
        year = yyyymmdd[:4]
        racetrack_code = racecourse_code_dict[df.at[yyyymmdd,'競馬場']]
        times = df.at[yyyymmdd,'第何回']
        if len(times) == 1:
            times = '0' + times
        date = df.at[yyyymmdd,'何日']
        if len(date) == 1:
            date = '0' + date
        race_number = df.at[yyyymmdd,'何R']
        if len(race_number) == 1:
            race_number = '0' + race_number
        race_name = df.at[yyyymmdd,'レース名']

        print(year,racetrack_code,times,date,race_number)
        print(f'本日は、{race_name}があります。')

    #開催年月日がない場合は、空文字でreturnする。
    else:
        year = racetrack_code = times = date = race_number = ''
        print('開催レースは存在しません。')

    return {
        'year': year,
        'racetrack_code': racetrack_code,
        'times': times,
        'date': date,
        'race_number': race_number,
    }


if __name__ == '__main__':
    retreive('2021-04-18')
