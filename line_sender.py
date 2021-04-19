"""line_sender

LINE へメッセージを送るスクリプトです。
"""

# Third-party modules.
from linebot import LineBotApi
from linebot.models import TextSendMessage

# User modules.
import utils
import consts

# このモジュール用のロガーを作成します。
logger = utils.get_my_logger(__name__)


def send(user_id: str, message: str):
    """
    TODO: まだいっかいもテストしてない。とりあえずベースだけ作成しただけの関数です。
    Doc: https://developers.line.biz/ja/reference/messaging-api/#send-push-message
    """

    logger.debug(f'Send message to {repr(user_id)}')

    line_bot_api = LineBotApi(consts.LINE_CHANNEL_ACCESS_TOKEN)
    line_bot_api.push_message(
        user_id,
        TextSendMessage(text=message),
    )


if __name__ == '__main__':
    send('', 'test message')
