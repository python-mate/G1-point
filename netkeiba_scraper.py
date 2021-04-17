"""netkeiba_scraper

netkeiba ウェブサイトからレース結果を取得するスクリプトです。
"""

# Third-party modules.
import requests
from bs4 import BeautifulSoup

# User modules.
import utils

# utils モジュール用のロガーを作成します。
logger = utils.get_my_logger(__name__)


def scrape(year: str, racetrack_code: str, times: str, date: str, race_number: str):

    # 引数チェックです。桁数をチェック。
    assert len(year) == 4, 'Argument "year" must be 4 characters.'
    assert len(racetrack_code) == 2, 'Argument "racetrack_code" must be 2 characters.'
    assert len(times) == 2, 'Argument "times" must be 2 characters.'
    assert len(date) == 2, 'Argument "date" must be 2 characters.'
    assert len(race_number) == 2, 'Argument "race_number" must be 2 characters.'

    # 対象の race_id を構築します。
    # NOTE: おそらく [西暦][競馬場コード][第何回][何日][何レース] のフォーマットだと予想されています。
    race_id = year + racetrack_code + times + date + race_number
    logger.debug(f'Run with race_id {race_id}')

    # Web ページを取得します。
    # response = requests.get(f'https://race.netkeiba.com/race/result.html?race_id={race_id}')
    # assert response.status_code == 200, f'Failed to get information of race_id={race_id}'

    # NOTE: このページには <meta charset="EUC-JP"> が設定されています。 encoding をそれに合わせます。
    # response.encoding = response.apparent_encoding

    # TODO: この URL は情報がなくとも 200 が返ります。
    #       情報のないページにアクセスしてしまったら何らかの方法で検知したい。

    html_source = get_dummy_html_source()
    print(html_source)


def get_dummy_html_source():
    """テスト中に何度もスクレイピングをかけるのは気が引けるので、
    ローカルに DL した html source を返します。
    """

    with open('./dummy.html', 'r') as f:
        return f.read()


if __name__ == '__main__':
    scrape(
        year='2021',
        racetrack_code='09',
        times='02',
        date='06',
        race_number='11',
    )
