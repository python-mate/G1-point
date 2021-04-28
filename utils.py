"""
Python やるときにいつもあって欲しい自分用モジュールです。
これは使いまわしたいのでリポジトリのビジネスロジック入れないでね。
"""

# Built-in modules.
import logging
import datetime

# Third-party modules.
import pytz
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# User modules.
import consts


def get_my_logger(logger_name: str) -> logging.Logger:
    """モジュール用のロガーを作成します。
    logger = get_my_logger(__name__)

    Args:
        logger_name (str): getLogger にわたす名前。 __name__ を想定しています。

    Returns:
        logging.Logger: モジュール用のロガー。
    """

    # ルートロガーを作成します。ロガーはモジュールごとに分けるもの。
    logger = logging.getLogger(logger_name)
    # ルートロガーのログレベルは DEBUG。
    logger.setLevel(logging.DEBUG)
    # コンソールへ出力するハンドラを作成。
    handler = logging.StreamHandler()
    # ハンドラもログレベルを持ちます。
    handler.setLevel(logging.DEBUG)
    # ログフォーマットをハンドラに設定します。
    formatter = logging.Formatter(
        # NOTE: 改行は逆に見づらいので E501 を無視します。
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')  # noqa: E501
    handler.setFormatter(formatter)
    # ハンドラをロガーへセットします。
    logger.addHandler(handler)
    # 親ロガーへの伝播をオフにします。
    logger.propagate = False
    return logger


def get_today_jst(_format: str) -> str:
    """日本時間の現在時刻を取得します。
    NOTE: format はビルトインメソッドがあるので一応 underscore をつけています。
    """

    TZ_JAPAN = pytz.timezone('Asia/Tokyo')
    current_jst_time = datetime.datetime.now(tz=TZ_JAPAN)
    return current_jst_time.strftime(_format)


def send_slack_message(message: str) -> None:
    """Slack にメッセージを送ります。
    """

    slack_client = WebClient(token=consts.SLACK_BOT_TOKEN)
    try:
        # NOTE: unfurl_links は時折鬱陶しいと思っている「リンクの展開機能」です。不要です。 False.
        slack_client.chat_postMessage(
            channel=consts.SLACK_CHANNEL_NAME, text=message, unfurl_links=False)
        # 返却値の確認は行いません。
        # NOTE: Slack api のドキュメントにあるコードなので追加していましたが排除します。
        #       リンクの含まれるメッセージを送信すると、返却値が勝手に変更されるため絶対一致しないからです。
        #       - リンクの前後に <, > がつく
        #       - & -> &amp; エスケープが起こる
        # assert response['message']['text'] == message
    except SlackApiError as e:
        assert e.response['ok'] is False
        # str like 'invalid_auth', 'channel_not_found'
        assert e.response['error']
        logger.error(f'Got an error: {e.response["error"]}')


# utils モジュール用のロガーを作成します。
logger = get_my_logger(__name__)

if __name__ == '__main__':
    logger.debug('でばーぐ')
    logger.info('いんーふぉ')
    logger.warning('うぉーにん')
    logger.error('えろあ')
    logger.fatal('ふぇーたる(critical と同じっぽい)')
    logger.critical('くりてぃこぉ')
    logger.debug(get_today_jst('%Y-%m-%d %H:%M:%S'))
    send_slack_message('"utils.py" run for test. Sorry for the notification!')
