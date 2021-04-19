"""
■ ご依頼その1
このプログラムを実行……

python spread_sheet_expectation_sender.py

したとき、一番下にある 1.4.6.18.89 のデータが Satou さんの「予想データ」として
Spread Sheet にきちんと格納されるように、関数 send を作ってください!
"""


def send(user_id, numbers_str):

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

    #上から２列目を無視上から１列目をカラムとする表として扱う。
    df = pd.DataFrame(data[2:],columns=data[1])

    print(df)







    # この関数が終わるとき、データが Spread Sheet の【各ユーザーのシートに予想印を】にきちんと格納されるように、作ってほしい。

    # SpreadSheet に格納したら、「どの日付の、どのレースの予想として格納したか」を return してください。
    return '2020-12-26', 'ホープフルステークス'


if __name__ == '__main__':
    send('sample-id-12345', '1.4.6.18.89')
