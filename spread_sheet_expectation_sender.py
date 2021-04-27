"""
■ ご依頼その1
このプログラムを実行……

python spread_sheet_expectation_sender.py

したとき、一番下にある 1.4.6.18.89 のデータが Satou さんの「予想データ」として
Spread Sheet にきちんと格納されるように、関数 send を作ってください!
"""
#必要モジュールの準備
import pandas as pd
import gspread
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe
from datetime import datetime as dt
from time import sleep

#LINE_idを元にシート名の辞書を作成する。
# ATTENTION: LINE channel が変わるたび、
#            そして Group が変わるたび、
#            ここの user id は変化します。
#            そのたびにログを参照して、各々の user id を取得し、
#            この↓ dict を更新してください。
seat_dict = {
    'U07294e976ea424c3023889f937bbd88f':'ササキ',
    'sample-id-2':'コバヤシ',
    'U8983175d9d45162373fe3916b543d0f6':'ウエハラ',
    'Uedab1cb5b1d9797691884a37044d0567':'マツノ',
    'U2d60dfb30b93c289b2fb32d92a3f29fd':'アカミネ',
    'U66bcf58c341aae32e40591b0abd1c963':'フクヤマ',
    'U036190fdaed7c8747f930a98534c04b4':'トヨシ',
    }

#現在日時を取得して文字型のYYYY/mm/ddの形へ変更する。
current_time = dt.now()
current_time_str = current_time.strftime('%Y/%m/%d')
#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
#テスト的に日付を強制合わせする。
# current_time_str = '2021/04/17'
#＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊


def send(user_id, numbers_str):

    ################################
    #.区切りの予想データをsplitで分割してリスト化
    expected_no_list = numbers_str.split('.')

    #2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    #認証情報設定
    #ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'g1-point-7e93bd98712c.json',
        scope
        )

    #OAuth2の資格情報を使用してGoogle APIにログインします。
    gc = gspread.authorize(credentials)

    #共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
    SPREADSHEET_KEY = '1pCTN9momqKlH4UtTRTf11yqXW2nI3grXUzRpbu6M6Tw'#スプレッドシートのd/〜〜/までをコピー。

    #編集するワークシート名を取得。入ってきたLINE_idを辞書で調べて取得。
    seat_selection = seat_dict[user_id]

    #ワークシート名を指定
    SP_SHEET = seat_selection

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
    #現在の年月日がスプレッドシートの開催年月日のデータにない場合は、近い未来の日程を取得する。
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

    #予想を書込む範囲を指定する。(H○:L○)で指定。
    expected_change_range = worksheet.range('H' + str(cell_index_no) + ':' + 'L' + str(cell_index_no))

    #変更範囲を指定して、変更内容を書込みしスプレッドシートに反映させる。
    for i,cell in enumerate(expected_change_range):
        cell.value = expected_no_list[i]
    worksheet.update_cells(expected_change_range)


    #編集した開催年月日を取得。YYYY/mm/dd⇨YYYY-mm-ddの形へ変換して
    return_date = edit_date.replace('/','-')
    #編集したレース名を取得
    edit_race_name = df.at[edit_date,'レース名']

    print(f'編集した年月日:{edit_date}')
    print(f'編集したレース名:{edit_race_name}')
    print(f'編集したシート名:{seat_selection}')
    # この関数が終わるとき、データが Spread Sheet の【各ユーザーのシートに予想印を】にきちんと格納されるように、作ってほしい。

    # SpreadSheet に格納したら、「どの日付の、どのレースの予想として格納したか」を return してください。
    return return_date , edit_race_name


if __name__ == '__main__':
    send('sample-id-4', '10.5.13.12.1')
