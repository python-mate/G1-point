"""
■ ご依頼その3
このプログラムを実行……

python spread_sheet_dataset_retreiver.py

したとき、レース 65 の「予想」と「着順」データが
print されるように、関数 retreive を作ってください!
"""
#必要モジュールの準備
import pandas as pd
import gspread
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe
from time import sleep

seat_dict = {
    'sample-id-1':'ササキ',
    'sample-id-2':'コバヤシ',
    'sample-d-3':'ウエハラ',
    'sample-id-4':'マツノ',
    'sample-id-5':'アカミネ',
    'sample-id-6':'フクヤマ',
    'sample-id-7':'トヨシ',
    }

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

def retreive(race_held_yyyy_mm_dd):

    # ここを埋めてほしい。
    #####################################
    # 各ユーザーのシートの払戻金額から的中判定する。

    #シートのリストを取得。
    seat_dict_key_list = list(seat_dict.keys())
    print_name_list = []
    ####################################
    # seat_dict_key_listの数だけ下記を回す。
    for _ in range(len(seat_dict_key_list)):
        #ワークシート名
        SP_SHEET = seat_dict[seat_dict_key_list[_]]

        #共有設定したスプレッドシートを開く
        sh = gc.open_by_key(SPREADSHEET_KEY)

        #ワークシートの選択
        worksheet_user = sh.worksheet(SP_SHEET)

        #スプレットシートの全データを取得
        data_users = worksheet_user.get_all_values()

        #pandasでindex番号を取得
        #上から２列目を無視上から１列目をカラムとする。indexは開催年月日とする。
        df_accurate_decision = pd.DataFrame(data_users[2:],columns=data_users[1]).set_index('開催年月日')

        # 開催年月日と比較したいのでrace_held_yyyy_mm_ddを編集
        acquisition_date = race_held_yyyy_mm_dd.replace('-','/')



        #結果発表のレース名を取得
        race_name = df_accurate_decision.at[acquisition_date,'レース名']

        #取得したいcolumns名を定義
        columns_get_list = ['単勝','馬連','馬単','3連複','3連単']

        #各払戻を加算して0以上なら的中が合ったと判断する。
        accurate_decision = 0
        print(seat_dict[seat_dict_key_list[_]])
        for column_get_list in columns_get_list:
            number_conversion = df_accurate_decision.at[acquisition_date,column_get_list].replace('¥','')
            number_conversion = number_conversion.replace(',','')
            accurate_decision += int(number_conversion)
        #払戻情報があれば的中者としてprint_name_listにappendする。
        if accurate_decision > 0:
            print_name_list.append(seat_dict[seat_dict_key_list[_]])

        print(accurate_decision)



    #的中報告のprint_nameを作成。
    if len(print_name_list) > 0:
        print_name = '\n'.join(print_name_list)
    else:
        print_name_list.append('今回的中者はいません!!\n次回のレースは頑張りましょう!!')

    # 開催年月日が一致するindex番号を取得
    # 次回のレース日程とレース名を取得
    cell_index_no = 0
    cell_index_no = df_accurate_decision.index.get_loc(acquisition_date)
    next_race_date = df_accurate_decision.index.values[cell_index_no + 1]
    next_race_name = df_accurate_decision.iat[cell_index_no + 1,0]

    # この print の中に、データがきちんと入るように作ってほしい

    line_accurate_report = ('【' + race_name + '的中報告】\n' + print_name +'\n'
    +'\n'+'※次回のG1ポイントレースは、\n'
    + next_race_date + ':' + next_race_name + 'です。\n'
    +'\n【スプレッドシート URL】\n'+
    'https://docs.google.com/spreadsheets/d/1pCTN9momqKlH4UtTRTf11yqXW2nI3grXUzRpbu6M6Tw/edit#gid=0'
    )


    return line_accurate_report


if __name__ == '__main__':
    retreive('2021-03-14')
