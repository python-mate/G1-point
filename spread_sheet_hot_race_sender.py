"""
■ 機能を追加
このプログラムを実行……

python spread_sheet_hot_race_sender.py

したとき、user_id に紐づいた　〇〇さんの「勝負レース」として
Spread Sheet にきちんと格納されるように、関数 send_geme を作くろう!
"""

#必要モジュールの準備
import pandas as pd
import gspread
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe
from datetime import datetime as dt
from time import sleep

# User modules.
import consts

#現在日時を取得して文字型のYYYY/mm/ddの形へ変更する。
current_time = dt.now()
current_time_str = current_time.strftime('%Y/%m/%d')
#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
#テスト的に日付を強制合わせする。
# current_time_str = '2021/04/17'
#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊

#LINE_idを元にシート名の辞書を作成する。
# ATTENTION: LINE channel が変わるたび、
#            そして Group が変わるたび、
#            ここの user id は変化します。
#            そのたびにログを参照して、各々の user id を取得し、
#            この↓ dict を更新してください。
seat_dict = {
    'U07294e976ea424c3023889f937bbd88f':'ササキ',
    'U97030df889f29fe5fa83fae98957a04d':'コバヤシ',
    'U8983175d9d45162373fe3916b543d0f6':'ウエハラ',
    'Uedab1cb5b1d9797691884a37044d0567':'マツノ',
    'U2d60dfb30b93c289b2fb32d92a3f29fd':'アカミネ',
    'U66bcf58c341aae32e40591b0abd1c963':'フクヤマ',
    'U036190fdaed7c8747f930a98534c04b4':'トヨシ',
    }

#⭐️スプレッドシートを扱う絶対必要なもの⭐️
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
SP_SHEET = ''#ワークシート名 とりあえず空を定義

def send_geme(user_id:str):
    """
    この関数が呼び出されると、user_idに紐づいたワークシートの
    '勝負'のカラムにTUREを入れる（チェックのこと）
    編集したシート名をリターンする。
    """
    #ワークシート名を指定
    SP_SHEET = seat_dict[user_id]

        #共有設定したスプレッドシートを開く
    sh = gc.open_by_key(SPREADSHEET_KEY)

    #ワークシートの選択
    worksheet = sh.worksheet(SP_SHEET)

    #スプレットシートの全データを取得
    data = worksheet.get_all_values()

    #上から２列目を無視上から１列目をカラムとする。indexは開催年月日とする。
    df = pd.DataFrame(data[2:],columns=data[1]).set_index('開催年月日')

    #現在の年月日がスプレッドシートの開催年月日のデータと一致する値があるなら現在年月日を代入（問題なし)
    if current_time_str in list(df.index.values):
        edit_date = current_time_str
    #現在の年月日がスプレッドシートの開催年月日のデータにない場合は、近い未来の日程を取得する。※ここいつかバグるな・・・
    else:
        current_time_rep = current_time_str.replace('/','')
        df_index_list = [ _.replace('/','') for _ in list(df.index.values)]
        #下記変数に空のリストを定義。と空文字を定義。
        date_survey_list_yyyy = date_survey_list_mm =date_survey_list_dd =[]
        edit_date = ''
        #①:年部分を比較し一致するデータのみリスト化
        date_survey_list_yyyy =[yyyy for yyyy in df_index_list if current_time_rep[0:4] == yyyy[0:4]]
        #②:月部分を比較し一致するデータのみリスト化
        date_survey_list_mm =[mm for mm in date_survey_list_yyyy if current_time_rep[4:6] == mm[4:6]]
        #③:日部分を比較し現在日程より先の日程のみリスト化する。
        date_survey_list_dd =[dd for dd in date_survey_list_mm if int(current_time_rep[6:8]) < int(dd[6:8])]
        #④:③に値があるなら一番若いindexの値を編集する日程とする。
        if len(date_survey_list_dd) > 0:
            edit_date = str(date_survey_list_dd[0])[0:4]+'/'+ str(date_survey_list_dd[0])[4:6]+'/'+str(date_survey_list_dd[0])[6:8]
        #⑤:③に値がない場合は、②で取得したデータの次の値を取得する。
        else:
            edit_date = date_survey_list_yyyy[date_survey_list_yyyy.index(date_survey_list_mm[-1])+1]
            edit_date = edit_date[0:4]+'/'+ edit_date[4:6]+'/'+edit_date[6:8]

    # 開催年月日が一致するindex番号を取得
    # スプレッドシートのフォーマット状　取得したインデックスに３加算した値がセルの位置
    cell_index_no = df.index.get_loc(edit_date)+3

    #編集する内容を記載する。
    #セルを取得して勝負カラムのチェック状態を調べる。
    sell_bool_type = worksheet.acell(f'M{cell_index_no}').value

    #FALSE=勝負にチェック　TRUE=勝負のチェックを外す
    if sell_bool_type == 'FALSE':
        #セルを指定して書込む
        worksheet.update_acell(f'M{cell_index_no}','TRUE')
        is_geme_or_cancel = '勝負'
    else:
        worksheet.update_acell(f'M{cell_index_no}','FALSE')
        is_geme_or_cancel = 'キャンセル'


    #編集した開催年月日を取得。YYYY/mm/dd⇨YYYY-mm-ddの形へ変換して
    return_date = edit_date.replace('/','-')
    #編集したレース名を取得
    edit_race_name = df.at[edit_date,'レース名']

    print(f'勝負レースとした年月日:{edit_date}')
    print(f'勝負としてレース名:{edit_race_name}')
    print(f'勝負レースとしたシート名:{SP_SHEET}')
    print(f'勝負かキャンセルか:{is_geme_or_cancel}')

    # SpreadSheet に格納したら、「どの日付の、どのレースを勝負としたのか」を return してください。
    return return_date , edit_race_name



if __name__ == '__main__':
    print(send_geme('U2d60dfb30b93c289b2fb32d92a3f29fd'))
