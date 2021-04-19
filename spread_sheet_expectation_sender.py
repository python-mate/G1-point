"""
■ ご依頼その1
このプログラムを実行……

python spread_sheet_expectation_sender.py

したとき、一番下にある 1.4.6.18.89 のデータが Satou さんの「予想データ」として
Spread Sheet にきちんと格納されるように、関数 send を作ってください!
"""


def send(user_id, numbers_str):

    # ここを埋めてほしい。

    # この関数が終わるとき、データが Spread Sheet にきちんと格納されるように、作ってほしい。

    # SpreadSheet に格納したら、「どの日付の、どのレースの予想として格納したか」を return してください。
    return '2020-12-26', 'ホープフルステークス'


if __name__ == '__main__':
    send('sample-id-12345', '1.4.6.18.89')
