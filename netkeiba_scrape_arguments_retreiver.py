"""
■ ご依頼その4
このプログラムを実行……

python netkeiba_scrape_arguments_retreiver.py

したとき、一番下で retreive 関数に渡している日付に、
(スクレイピングしてほしい)レースが存在するなら、
URL を作成するための情報を return してほしいです。
そんなことが出来る関数 retreive を作ってください!
"""


def retreive(yyyymmdd):

    # year: str, racetrack_code: str, times: str, date: str, race_number: str

    return {
        'year': '2020',
        'racetrack_code': '06',
        'times': '5',
        'date': '7',
        'race_number': '11',
    }


if __name__ == '__main__':
    retreive('2021-03-14')
