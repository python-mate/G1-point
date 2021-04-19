"""line_operator

LINE とのやりとりを行うスクリプトです。
"""

# Third-party modules.
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

# User modules.
import utils
import consts

# このモジュール用のロガーを作成します。
logger = utils.get_my_logger(__name__)

app = Flask(__name__)

line_bot_api = LineBotApi(consts.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(consts.LINE_CHANNEL_SECRET)


# 必須ではないけれど、サーバに上がったことを確認するためにトップページを追加しておきます。
@app.route('/')
def top_page():
    logger.debug('Here is root page.')
    return 'Here is root page.'


# ユーザがメッセージを送信したとき、この URL へアクセスが行われます。
@app.route('/callback', methods=['POST'])
def callback_post():

    # ここで行うことは……
    # - Push message を行うための送信先を取得。たぶん group id...??
    # - 誰の発言? を取得。(名前と user_id) user id は要らないか。
    # - メッセージの内容を取得。

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    logger.debug('Request body: ' + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def reply_message(event):
    # reply のテスト。
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Send from line_bot_api.reply_message, you sent...: ' + event.message.text))


if __name__ == '__main__':
    app.run()
