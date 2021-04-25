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


def send(to: str, message: str):
    """LINE へメッセージを送信します。
    NOTE: to には user_id, group_id, room_id を指定可能です。
    Doc: https://developers.line.biz/ja/reference/messaging-api/#send-push-message
    """

    logger.debug(f'Send message to {repr(to)}')

    line_bot_api = LineBotApi(consts.LINE_CHANNEL_ACCESS_TOKEN)
    line_bot_api.push_message(
        to,
        TextSendMessage(text=message),
    )


if __name__ == '__main__':
    send(consts.LINE_G1_GROUP_ID, 'Message sent by Python.')
