"""
■ ご依頼その2
このプログラムを実行……

python spread_sheet_result_sender.py

したとき、一番下にあるデータが「レース 65 の着順」として
Spread Sheet にきちんと格納されるように、関数 send を作ってください!
"""


def send(race_number, numbers_str):

    # ここを埋めてほしい。

    # この関数が終わるとき、データが Spread Sheet にきちんと格納されるように、作ってほしい。

    pass


if __name__ == '__main__':
    send('65', {
        'tansho_payout': 360,
        'umaren_payout': 670,
        'umatan_payout': 1280,
        'fuku3_payout': 2660,
        'tan3_payout': 10400,
        'ranking1': 4,
        'ranking2': 18,
        'ranking3': 2,
    })


