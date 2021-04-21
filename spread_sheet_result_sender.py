"""
■ ご依頼その2
このプログラムを実行……

python spread_sheet_result_sender.py

したとき、一番下にあるデータが「レース yyyy-mm-dd の着順」として
Spread Sheet にきちんと格納されるように、関数 send を作ってください!
"""


def send(race_held_yyyy_mm_dd, race_result):

    # ここを埋めてほしい。
    
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

    ####################################
    #pandasでindex番号を取得
    #上から２列目を無視上から１列目をカラムとする。indexは開催年月日とする。
    df = pd.DataFrame(data[2:],columns=data[1]).set_index('開催年月日')

    # 開催日程と比較したいのでrace_held_yyyy_mm_ddを編集
    acquisition_date = race_held_yyyy_mm_dd.replace('-','/')
    # セルは、スプレッドシートのフォーマット状　取得したインデックスに３加算した値
    cell_index_no = df.index.get_loc(acquisition_date)+3
    
    ####################################
    # スプレッドシートに書き込んでいく。くそー絶対もっといい方法あるヤロー・・・
    worksheet.update_acell('M' + str(cell_index_no), race_result['tansho_payout'])
    worksheet.update_acell('N' + str(cell_index_no), race_result['umaren_payout'])
    worksheet.update_acell('O' + str(cell_index_no), race_result['umatan_payout'])
    worksheet.update_acell('P' + str(cell_index_no), race_result['fuku3_payout'])
    worksheet.update_acell('Q' + str(cell_index_no), race_result['tan3_payout'])
    worksheet.update_acell('G' + str(cell_index_no), race_result['ranking1'])
    worksheet.update_acell('H' + str(cell_index_no), race_result['ranking1_name'])
    worksheet.update_acell('I' + str(cell_index_no), race_result['ranking2'])
    worksheet.update_acell('J' + str(cell_index_no), race_result['ranking2_name'])
    worksheet.update_acell('K' + str(cell_index_no), race_result['ranking3'])
    worksheet.update_acell('L' + str(cell_index_no), race_result['ranking3_name'])

    # この関数が終わるとき、データが Spread Sheet に【レース結果と払戻し情報】がきちんと格納されるように、作ってほしい。

    pass


if __name__ == '__main__':
    send('2021-01-24', {
        'tansho_payout': 480,
        'umaren_payout': 670,
        'umatan_payout': 1280,
        'fuku3_payout': 2660,
        'tan3_payout': 10400,
        'ranking1': 4,
        'ranking1_name': 'paparemon',
        'ranking2': 18,
        'ranking2_name': 'mamasenbai',
        'ranking3': 2,
        'ranking3_name': 'red-sakuranbo',
    })
