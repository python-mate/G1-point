"""scheduled_worker

毎日発火することを想定しているスクリプトです。
いろいろな user 作成モジュールをコールする上位スクリプトという位置づけです。
"""

# Built-in modules.
import traceback

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
    today_yyyymmdd = '2021-12-19'
    race_information = netkeiba_scrape_arguments_retreiver.retreive(today_yyyymmdd)
    logger.debug(f'Result of "netkeiba_scrape_arguments_retreiver": {race_information}')

    # レースが無い日はこれでおしまいです。おつかれさまでした。
    # NOTE: どうやら netkeiba_scrape_arguments_retreiver は、レースない日は {'year': '', ...}
    #       を返すようだ。それを判断基準にします。
    if not race_information['year']:
        logger.debug(f'Nothing to do at {today_yyyymmdd}')
        return

    # レースがあった日のようです。レース結果を見に行きます。
    payout_information = netkeiba_scraper.scrape(
        year=race_information['year'],
        racetrack_code=race_information['racetrack_code'],
        times=race_information['times'],
        date=race_information['date'],
        race_number=race_information['race_number'],
    )
    logger.debug(f'Result of "netkeiba_scraper": {payout_information}')

    # レース結果を SpreadSheet へ保存します。
    spread_sheet_result_sender.send(today_yyyymmdd, payout_information)
    logger.debug('Result of "spread_sheet_result_sender": Done')

    # LINE へ送信する内容を取得します。
    message_for_line = spread_sheet_dataset_retreiver.retreive(today_yyyymmdd)
    logger.debug(f'Result of "spread_sheet_dataset_retreiver": {message_for_line}')

    # LINE へメッセージを送信します。
    line_sender.send(consts.LINE_G1_GROUP_ID, message_for_line)
    logger.debug('Result of "line_sender": Done')


if __name__ == '__main__':
    try:
        run()
    except Exception as ex:
        # サーバ側にもログは出ていてほしいので、出します。
        # NOTE: Slack へメッセージを送ったあとに raise ex するほうがキレイに見えます。
        #       しかし、 Slack でエラーが発生したとき怖い(何も解らなくなる)ので、
        #       ここで print_exc することにしました。
        logger.error('Error raised in scheduled_worker, print_exc below.')
        traceback.print_exc()

        # NOTE: str(ex) によりメッセージが出力されます。
        utils.send_slack_message(
            f'Error raised in scheduled_worker: {ex}\n'
            'Check the detail log: `heroku logs --num 1500 --app denuma-program --ps scheduler`'
        )
