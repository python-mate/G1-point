"""
■ ご依頼その2
このプログラムを実行……

python spread_sheet_result_sender.py

したとき、一番下にあるデータが「レース yyyy-mm-dd の着順」として
Spread Sheet にきちんと格納されるように、関数 send を作ってください!
"""
#必要モジュールの準備
import pandas as pd
import gspread
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe

#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

#認証情報設定
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    '/Users/akamine/Documents/g1-point/g1-point-7e93bd98712c.json',
    scope
    )

#OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)

#共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
SPREADSHEET_KEY = '1pCTN9momqKlH4UtTRTf11yqXW2nI3grXUzRpbu6M6Tw'#スプレッドシートのd/〜〜/までをコピー。
SP_SHEET = '結果'#ワークシート名

#共有設定したスプレッドシートを開く
sh = gc.open_by_key(SPREADSHEET_KEY)

#ワークシートの選択
worksheet = sh.worksheet(SP_SHEET)

#スプレットシートの全データを取得
data = worksheet.get_all_values()



def send(race_held_yyyy_mm_dd, race_result):

    # ここを埋めてほしい。

    ####################################
    #pandasでindex番号を取得
    #上から２列目を無視上から１列目をカラムとする。indexは開催年月日とする。
    df = pd.DataFrame(data[2:],columns=data[1]).set_index('開催年月日')

    # 開催年月日と比較したいのでrace_held_yyyy_mm_ddを編集
    acquisition_date = race_held_yyyy_mm_dd.replace('-','/')

    # 開催年月日が一致するindex番号を取得
    # スプレッドシートのフォーマット状　取得したインデックスに３加算した値がセルの位置
    cell_index_no = df.index.get_loc(acquisition_date)+3

    #race_resultの辞書よりキーを取得してリスト化 11点のリストを確認してから並び替え
    race_result_list = race_result.keys()
    if len(race_result_list) == 11:
        sorted_race_result_list = [
            'ranking1',
            'ranking1_name',
            'ranking2',
            'ranking2_name',
            'ranking3',
            'ranking3_name',
            'tansho_payout',
            'umaren_payout',
            'umatan_payout',
            'fuku3_payout',
            'tan3_payout']


    #結果を書込む範囲を指定する。(G○:Q○)で指定。
    range_write_result = worksheet.range('G' + str(cell_index_no) + ':' + 'Q' + str(cell_index_no))

    #変更範囲を指定して、変更内容を書込みしスプレッドシートに反映させる。
    for i,cell in enumerate(range_write_result):
        cell.value = race_result[sorted_race_result_list[i]]
    worksheet.update_cells(range_write_result)

    # ####################################
    # # スプレッドシートに書き込んでいく。くそー絶対もっといい方法あるヤロー・・・
    # worksheet.update_acell('M' + str(cell_index_no), race_result['tansho_payout'])
    # worksheet.update_acell('N' + str(cell_index_no), race_result['umaren_payout'])
    # worksheet.update_acell('O' + str(cell_index_no), race_result['umatan_payout'])
    # worksheet.update_acell('P' + str(cell_index_no), race_result['fuku3_payout'])
    # worksheet.update_acell('Q' + str(cell_index_no), race_result['tan3_payout'])
    # worksheet.update_acell('G' + str(cell_index_no), race_result['ranking1'])
    # worksheet.update_acell('H' + str(cell_index_no), race_result['ranking1_name'])
    # worksheet.update_acell('I' + str(cell_index_no), race_result['ranking2'])
    # worksheet.update_acell('J' + str(cell_index_no), race_result['ranking2_name'])
    # worksheet.update_acell('K' + str(cell_index_no), race_result['ranking3'])
    # worksheet.update_acell('L' + str(cell_index_no), race_result['ranking3_name'])

    # この関数が終わるとき、データが Spread Sheet に【レース結果と払戻し情報】がきちんと格納されるように、作ってほしい。

    pass


if __name__ == '__main__':
    send('2021-03-14', {
        'tansho_payout': 13000,
        'umaren_payout': 5690,
        'umatan_payout': 72800,
        'fuku3_payout': 926600,
        'tan3_payout': 1340000,
        'ranking1': 5,
        'ranking1_name': 'papa-remon',
        'ranking2': 7,
        'ranking2_name': 'mama-senbai',
        'ranking3': 2,
        'ranking3_name': 'red-sakuranbo-',
    })
