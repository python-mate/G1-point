"""
■ 機能を追加
このプログラムを実行……

python spread_sheet_hot_race_sender.py

したとき、user_id に紐づいた　〇〇さんの「勝負レース」として
Spread Sheet にきちんと格納されるように、関数 send_game を作くろう!
"""

# 必要モジュールの準備
import pandas as pd
import gspread
# ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials
# from gspread_dataframe import set_with_dataframe
from datetime import datetime as dt

# User modules.
import consts

# ⭐️スプレッドシートを扱う絶対必要なもの⭐️
# 認証情報設定
# NOTE: もともとは from_json_keyfile_name で json ファイルから credentials を作っていました。
#       しかし秘密鍵である json ファイルを repository に含めると、 GitHub で公開できません!
#       なので from_json_keyfile_dict に変更して、 json ファイルがなくても動くようにしました。
GSPREAD_CREDENTIAL = ServiceAccountCredentials.from_json_keyfile_dict(
    consts.GSPREAD_CREDENTIAL_JSON,
    consts.GSPREAD_SCOPE,
)

# OAuth2の資格情報を使用してGoogle APIにログインします。
GSPREAD_GC = gspread.authorize(GSPREAD_CREDENTIAL)


def send_game(user_id: str) -> dict:
    """
    この関数が呼び出されると、user_idに紐づいたワークシートの
    '勝負'のカラムにTRUEを入れる（チェックのこと）
    returnは、辞書型で返す。
    return_dict = dict(
        date = return_date,(日付)
        raec_name = edit_race_name,(レース名)
        sheet_name = SP_SHEET,(ワークシート)
        is_game = is_game(True->勝負 Flese->キャンセル)
    )
    """

    # 現在日時を取得して文字型のYYYY/mm/ddの形へ変更する。
    current_time = dt.now()
    current_time_str = current_time.strftime('%Y/%m/%d')
    # ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
    # テスト的に日付を強制合わせする。
    # current_time_str = '2021/04/17'
    # ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊

    # LINEのuser_idに紐付いたスプレッドシートのシート名指定して開く。
    # ワークシート名を指定
    SP_SHEET = consts.LINE_USER_ID_DICT[user_id]
    # 共有設定したスプレッドシートを開く
    SP_SH = GSPREAD_GC.open_by_key(consts.GSPREAD_SPREADSHEET_KEY)
    # ワークシートの選択
    SP_WORKSHEET = SP_SH.worksheet(SP_SHEET)
    # スプレットシートの全データを取得
    data = SP_WORKSHEET.get_all_values()

    # 上から２列目を無視上から１列目をカラムとする。indexは開催年月日とする。
    df = pd.DataFrame(data[2:], columns=data[1]).set_index('開催年月日')

    # 現在の年月日がスプレッドシートの開催年月日のデータと一致する値があるなら現在年月日を代入（問題なし)
    if current_time_str in list(df.index.values):
        edit_date = current_time_str

    # 現在の年月日がスプレッドシートの開催年月日のデータにない場合は、近い未来の日程を取得する。
    # NOTE:※ここいつかバグるな・・・
    #      自作した近未来の取得方法。現状は上手く行っているが、どこでバグるか・・・
    else:
        # 今の年月日とスプレッドの開催年月日を取得。
        current_time_rep = current_time_str.replace('/', '')
        df_index_list = [_.replace('/', '') for _ in list(df.index.values)]
        # 下記変数に空のリストを定義。と edit_dateに空文字を定義。
        date_survey_list_yyyy = date_survey_list_mm = date_survey_list_dd = []
        edit_date = ''

        # ①:年部分を比較し一致するデータのみリスト化
        date_survey_list_yyyy = [
            yyyy for yyyy in df_index_list if current_time_rep[0:4] == yyyy[0: 4]
            ]
        # ②:月部分を比較し一致するデータのみリスト化
        date_survey_list_mm = [
            mm for mm in date_survey_list_yyyy if current_time_rep[4:6] == mm[4:6]
            ]
        # ③:日部分を比較し現在日程より先の日程のみリスト化する。
        date_survey_list_dd = [
            dd for dd in date_survey_list_mm if int(current_time_rep[6:8]) < int(dd[6:8])
            ]
        # ④:③に値があるなら一番若いindexの値を編集する日程とする。
        if len(date_survey_list_dd) > 0:
            closest_date = date_survey_list_dd[0]
            edit_date = f'{closest_date[0:4]}/{closest_date[4:6]}/{closest_date[6:8]}'
        # ⑤:③に値がない場合は、②で取得したデータの次の値を取得する。
        # NOTE:これは、自分で書いたのかww!!どーいう意味やっけか・・・
        # 　　月→日で検索して開催日程が存在しないなら、月まで一致している最後の開催日の
        # 　　次の開催日を指定しているはず。
        else:
            edit_date = date_survey_list_yyyy[date_survey_list_yyyy.index(date_survey_list_mm[-1])+1]
            edit_date = f'{edit_date[0:4]}/{edit_date[4:6]}+{edit_date[6:8]}'

    # 開催年月日が一致するindex番号を取得
    # スプレッドシートのフォーマット状　取得したインデックスに３加算した値がセルの位置
    cell_index_no = df.index.get_loc(edit_date)+3

    # 編集する内容を記載する。
    # セルを取得して勝負カラムのチェック状態を調べる。
    cell_bool_type = SP_WORKSHEET.acell(f'M{cell_index_no}').value

    # セルの状態がFALSEであれば、True を返してもらう。
    is_game = cell_bool_type == 'FALSE'

    # FALSE=勝負にチェック　TRUE=勝負のチェックを外す。
    if is_game:
        # セルを指定して書込む
        SP_WORKSHEET.update_acell(f'M{cell_index_no}', 'TRUE')
    else:
        SP_WORKSHEET.update_acell(f'M{cell_index_no}', 'FALSE')

    # 編集した開催年月日を取得。YYYY/mm/dd⇨YYYY-mm-ddの形へ変換して
    return_date = edit_date.replace('/', '-')
    # 編集したレース名を取得
    edit_race_name = df.at[edit_date, 'レース名']

    print(f'勝負レース処理した年月日:{edit_date}')
    print(f'勝負レース処理したレース名:{edit_race_name}')
    print(f'勝負レース処理したシート名:{SP_SHEET}')
    print(f'勝負かキャンセルか:{is_game}')

    # returnするデータを辞書化する。
    return_dict = dict(
        date=return_date,
        race_name=edit_race_name,
        sheet_name=SP_SHEET,
        is_game=is_game
    )

    # SpreadSheet に格納したら、「どの日付の、どのレースを 勝負orキャンセルしたのか」を return
    return return_dict


if __name__ == '__main__':
    print(send_game('U2d60dfb30b93c289b2fb32d92a3f29fd'))
