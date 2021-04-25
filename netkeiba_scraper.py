"""netkeiba_scraper

netkeiba ウェブサイトからレース結果を取得するスクリプトです。
"""

# Third-party modules.
import requests
from bs4 import (
    BeautifulSoup, element
)

# User modules.
import utils

# このモジュール用のロガーを作成します。
logger = utils.get_my_logger(__name__)


def scrape(year: str, racetrack_code: str, times: str, date: str, race_number: str):

    # 引数チェックです。
    __scrape_arguments_check(year, racetrack_code, times, date, race_number)
    logger.debug('Arguments checking passed.')

    # 対象の race_id を構築します。
    # NOTE: おそらく [西暦][競馬場コード][第何回][何日][何レース] のフォーマットだと予想されています。
    race_id = year + racetrack_code + times + date + race_number
    logger.debug(f'Run with race_id {race_id}')

    # Web ページを取得します。
    # NOTE: この URL は情報がなくとも 200 が返ります。
    #       情報のないページのときの対応は __pick_payout_details の中で行っています。
    url = f'https://race.netkeiba.com/race/result.html?race_id={race_id}'
    logger.debug(f'Target page is {url}')
    html_source = __get_euc_jp_html_source(url)

    # NOTE: テスト中に何度もスクレイピングをかけるのは気が引けるので、
    #       開発中はコレ使ってー。そして上の html_source はコメントアウトを。
    # html_source = __get_dummy_html_source()

    # HTML から「払い戻し」情報を抽出します。
    payout_information = __pick_payout_details(html_source)
    logger.debug('Successfully got payout information.')

    return payout_information


def __scrape_arguments_check(
        year: str, racetrack_code: str, times: str, date: str, race_number: str):

    # NOTE: 引数チェックが行数をくうのがイヤで、分離した関数です。

    # 引数チェックです。桁数をチェック。
    assert len(year) == 4, 'Argument "year" must be 4 characters.'
    assert len(racetrack_code) == 2, 'Argument "racetrack_code" must be 2 characters.'
    assert len(times) == 2, 'Argument "times" must be 2 characters.'
    assert len(date) == 2, 'Argument "date" must be 2 characters.'
    assert len(race_number) == 2, 'Argument "race_number" must be 2 characters.'


def __get_euc_jp_html_source(url: str):

    response = requests.get(url)
    assert response.status_code == 200, f'Failed to get {url}'

    # NOTE: このページには <meta charset="EUC-JP"> が設定されています。 encoding をそれに合わせます。
    response.encoding = response.apparent_encoding

    return response.text


def __get_dummy_html_source():
    """テスト中に何度もスクレイピングをかけるのは気が引けるので、
    ローカルに DL した html source を返します。
    """

    with open('./dummy.html', 'r') as f:
        return f.read()


def __pick_payout_details(html_source: str) -> dict:
    """html source から、抽出したい情報を取得して dict で返します。
    今回、 html から取得する情報が多く、
    ビジネスロジックが複雑になるので関数を分けています。

    必要なのは
    - 単勝の価格 --> tr.Tansho > td.Payout > span
    - 馬連の価格 --> tr.Umaren > td.Payout > span
    - 馬単の価格 --> tr.Umatan > td.Payout > span
    - 3連複の価格 --> tr.Fuku3 > td.Payout > span
    - 3連単の価格 --> tr.Tan3 > td.Payout > span
    - 順位 --> 複勝から取得 tr.Fukusho > td.Result > (複数の) div > span
    """

    soup = BeautifulSoup(html_source, 'lxml')

    # 適切な html source かどうかを確認します。
    assert soup.select_one('tr.Tansho > td.Payout > span') is not None, (
        'Can not get "Tansho" value.'
        ' HTML structure is not what we expect. or requested page does not have payout information.'
    )

    # 「単勝」の価格を取得します。
    tansho_payout = soup.select_one('tr.Tansho > td.Payout > span')
    # 「馬連」の価格を取得します。
    umaren_payout = soup.select_one('tr.Umaren > td.Payout > span')
    # 「馬単」の価格を取得します。
    umatan_payout = soup.select_one('tr.Umatan > td.Payout > span')
    # 「3連複」の価格を取得します。
    fuku3_payout = soup.select_one('tr.Fuku3 > td.Payout > span')
    # 「3連単」の価格を取得します。
    tan3_payout = soup.select_one('tr.Tan3 > td.Payout > span')

    # 金額は int が扱いやすいと思うので、 int にします。
    def foo(span: element.Tag) -> int:
        return int(span.get_text().replace(',', '').replace('円', ''))
    tansho_payout = foo(tansho_payout)
    umaren_payout = foo(umaren_payout)
    umatan_payout = foo(umatan_payout)
    fuku3_payout = foo(fuku3_payout)
    tan3_payout = foo(tan3_payout)

    # 1,2,3位の情報を取得します。
    # tr.FirstDisplay > td.Result_Num > div.Rank --> 順位
    #                 > td.Num.Txt_C > div --> 馬番
    #                 span.Horse_Name > a --> 馬名
    rows = soup.select('tr.FirstDisplay')

    # tr.FirstDisplay は1,2,3位に付与されている想定です。一応確認します。
    assert len(rows) == 3, f'More than three tr.FirstDisplay detected: {len(rows)}'

    # 1,2,3位の要素が取得できたので、具体的な値を取り出します。
    # {1:1位の情報, 2:2位の情報, 3:3位の情報} の形式で dict にします。
    ranking = {}
    for tr in rows:
        rank = int(tr.select_one('td.Result_Num > div.Rank').get_text())
        horse_number = int(tr.select_one('td.Num.Txt_C > div').get_text())
        horse_name = tr.select_one('span.Horse_Name > a').get_text()
        ranking[rank] = dict(
            horse_number=horse_number,
            horse_name=horse_name,
        )

    # NOTE: これは、いつ構造が変わってもおかしくない html から情報を取得する処理です。
    #       予測せぬエラーに備え、結果のチェックを行っています。
    assert tansho_payout >= 0, f'tansho_payout is invalid: {repr(tansho_payout)}'
    assert umaren_payout >= 0, f'umaren_payout is invalid: {repr(umaren_payout)}'
    assert umatan_payout >= 0, f'umatan_payout is invalid: {repr(umatan_payout)}'
    assert fuku3_payout >= 0, f'fuku3_payout is invalid: {repr(fuku3_payout)}'
    assert tan3_payout >= 0, f'tan3_payout is invalid: {repr(tan3_payout)}'
    assert len(ranking.keys()) == 3, f'ranking does not contain 3 elements: {repr(ranking.keys())}'

    return {
        'tansho_payout': tansho_payout,
        'umaren_payout': umaren_payout,
        'umatan_payout': umatan_payout,
        'fuku3_payout': fuku3_payout,
        'tan3_payout': tan3_payout,
        'ranking1': ranking[1]['horse_number'],
        'ranking1_name': ranking[1]['horse_name'],
        'ranking2': ranking[2]['horse_number'],
        'ranking2_name': ranking[2]['horse_name'],
        'ranking3': ranking[3]['horse_number'],
        'ranking3_name': ranking[3]['horse_name'],
    }


if __name__ == '__main__':
    payout_information = scrape(
        year='2021',
        racetrack_code='06',
        times='03',
        date='08',
        race_number='11',
    )
    logger.debug(payout_information)
