"""scheduled_worker

毎日発火することを想定しているスクリプトです。
いろいろな user 作成モジュールをコールする上位スクリプトという位置づけです。
"""

# User modules.
import utils
import consts
import netkeiba_scrape_arguments_retreiver
import netkeiba_scraper
import spread_sheet_result_sender
import spread_sheet_dataset_retreiver
import line_sender

# このモジュール用のロガーを作成します。
logger = utils.get_my_logger(__name__)


def run():

    # レース有無を取得します。
    # NOTE: 本スクリプトは毎日の定期発火を想定しています。
    #       ただし、レース結果の出ていない日にはやることが無いです。
    #       その是非を、 netkeiba_scraper_arguments_retreiver に尋ねています。
    today_yyyymmdd = utils.get_today_jst('%Y-%m-%d')
    race_information = netkeiba_scrape_arguments_retreiver.retreive(today_yyyymmdd)

    # レースが無い日はこれでおしまいです。おつかれさまでした。
    if not race_information:
        logger.debug(f'Nothing to do at {today_yyyymmdd}')

    # レースがあった日のようです。レース結果を見に行きます。
    payout_information = netkeiba_scraper.scrape(race_information)

    # レース結果を SpreadSheet へ保存します。
    spread_sheet_result_sender.send(today_yyyymmdd, payout_information)

    # LINE へ送信する内容を取得します。
    message_for_line = spread_sheet_dataset_retreiver.retreive(today_yyyymmdd)

    # LINE へメッセージを送信します。
    line_sender.send(consts.LINE_G1_GROUP_ID, message_for_line)


if __name__ == '__main__':
    run()
