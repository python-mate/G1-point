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


    #####################################
    # 結果を元に各ユーザーのシートに的中判定と的中金額を書き込んでいく。

    #シートのリストを取得。
    seat_dict_key_list = list(seat_dict.keys())
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
        df_result_writing = pd.DataFrame(data_users[2:],columns=data_users[1]).set_index('開催年月日')

        # 読み込んできたいcolumnsのリストと辞書を定義
        expected_columns_list = ['◎','○','▲','△','☆']
        refundment_writing_dict = {}

        #予想の辞書作成。
        for expected_column in expected_columns_list:
            refundment_writing_dict[expected_column] = int(df_result_writing.at[acquisition_date,expected_column])

        # 払戻情報を辞書化
        refund_info_dict = {'単勝':0,'馬連':0,'馬単':0,'3連複':0,'3連単':0}

        #レース結果の1,2,3着リスト
        ranking123_list = [race_result['ranking1'],race_result['ranking2'],race_result['ranking3']]

        # 単勝結果の判定
        if race_result['ranking1'] == refundment_writing_dict['◎']:
            refund_info_dict['単勝'] = race_result['tansho_payout'] * 10

        # 馬連結果の判定
        umaren_flag = 0
        if refundment_writing_dict['◎'] == race_result['ranking1'] or refundment_writing_dict['◎'] == race_result['ranking2']:
            umaren_flag += 10

        if refundment_writing_dict['○'] == race_result['ranking1'] or refundment_writing_dict['○'] == race_result['ranking2']:
            umaren_flag += 10

        if refundment_writing_dict['▲'] == race_result['ranking1'] or refundment_writing_dict['▲'] == race_result['ranking2']:
            umaren_flag += 1

        if refundment_writing_dict['△'] == race_result['ranking1'] or refundment_writing_dict['△'] == race_result['ranking2']:
            umaren_flag += 1

        if refundment_writing_dict['☆'] == race_result['ranking1'] or refundment_writing_dict['☆'] == race_result['ranking2']:
            umaren_flag += 1

        if umaren_flag >= 11:
            refund_info_dict['馬連'] = race_result['umaren_payout'] * 4

        # 馬単結果の判定
        if refundment_writing_dict['◎'] == race_result['ranking1']:
            if refundment_writing_dict['○'] == race_result['ranking2'] or refundment_writing_dict['▲'] == race_result['ranking2']:
                refund_info_dict['馬単'] = race_result['umatan_payout'] * 3

        #3連複の判定
        fuku3_len = set(list(refundment_writing_dict.values())) & set(ranking123_list)
        if len(fuku3_len) == 3:
            refund_info_dict['3連複'] = race_result['fuku3_payout'] * 2

        #3連単の判定
        if refundment_writing_dict['◎'] in ranking123_list:
            if len(set(list(refundment_writing_dict.values())) & set(ranking123_list)) == 3:
                refund_info_dict['3連単'] = race_result['tan3_payout'] * 1

        #結果を書込む範囲を指定する。(G○:Q○)で指定。
        range_write_refund = worksheet_user.range('N' + str(cell_index_no) + ':' + 'R' + str(cell_index_no))

        #変更範囲を指定して、変更内容を書込みしスプレッドシートに反映させる。
        for i,cell in enumerate(range_write_refund):
            cell.value = refund_info_dict[list(refund_info_dict.keys())[i]]
        worksheet_user.update_cells(range_write_refund)

        print(refund_info_dict)
    # この関数が終わるとき、データが Spread Sheet に【レース結果と払戻し情報】がきちんと格納されるように、作ってほしい。

    pass


if __name__ == '__main__':
    send('2021-03-14', {
        'tansho_payout': 22730,
        'umaren_payout': 13570,
        'umatan_payout': 62050,
        'fuku3_payout': 34650,
        'tan3_payout': 783010,
        'ranking1': 5,
        'ranking1_name': 'ギベオン',
        'ranking2': 1,
        'ranking2_name': 'デアリングタクト',
        'ranking3': 10,
        'ranking3_name': 'ポタジェ',
    })
