"""flask_line_receiver

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
import mojimoji

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
    # NOTE: logger でも Heroku ログにちゃんと出る。
    logger.debug('Here is root page.')
    return 'Here is root page.'


# ユーザがメッセージを送信したとき、この URL へアクセスが行われます。
@app.route('/callback', methods=['POST'])
def callback_post():

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # NOTE: body の内容はこんな感じ。
    #       dict として扱い、値を取り出すこともできます。
    #       ただし handler によって add した関数内で利用するのが正道な気がする。
    # {
    #     "destination": "Uf2485b0560fd4931794caf4e4dab033d",
    #     "events": [
    #         {
    #             "type": "message",
    #             "message": {
    #                 "type": "text", "id": "13930066619344", "text": "HELLO"
    #             },
    #             "timestamp": 1619087553397,
    #             "source": {
    #                 "type": "group", "groupId": "C19709b8f8...acd9f538",
    #                 "userId": "U226ec6476abd.....e94a3fa9d3be56"
    #             },
    #             "replyToken": "f5bf4ee22dd54....4489279adb0",
    #             "mode": "active"
    #         }
    #     ]
    # }

    try:
        # NOTE: ドキュメント https://github.com/line/line-bot-sdk-python#webhookhandler
        #       handler は、別途 @handler.add を定義することで利用する。
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# NOTE: @handler.add した関数は、handler.handle 関数によって呼び出される、
#       ってイメージで多分 OK.
@handler.add(MessageEvent, message=TextMessage)
def on_get_message(event):
    """ここで行うことは……
    - G1 グループからのメッセージであることを確認。(event.source.group_id で検証可能。)
    - 発言者名を取得。(line_bot_api.get_profile で確認可能。)
    - メッセージの内容を取得し、「予想」メッセージであれば Spread Sheet へ格納。
    """

    # Group id を取得。
    # TODO: のちのち、 G1 グループの group id を取得して環境変数へ記録。
    group_id = event.source.group_id
    logger.debug(dict(group_id=group_id))

    # TODO: G1 グループからのメッセージであることを確認。

    # 発言者の id。
    user_id = event.source.user_id
    # 発言者の情報。
    # NOTE: ドキュメント https://github.com/line/line-bot-sdk-python#get_profileself-user_id-timeoutnone
    user_profile = line_bot_api.get_profile(user_id)
    logger.debug(dict(user_id=user_id))

    # 返答するための token。
    # NOTE: line_bot_api.reply_message(reply_token, TextSendMessage(text='...')) と使用。
    reply_token = event.reply_token

    # メッセージの内容。
    message_text = event.message.text
    # NOTE: スペースが混じっていたり、全角が混じっていたりするのは看過してやります。
    message_text = mojimoji.zen_to_han(message_text).replace(' ', '')
    logger.debug(dict(message_text=message_text))

    # 対象メッセージ(予想の書かれたメッセージ)かどうかを判別します。
    # 対象メッセージでなければ無視。
    if not is_target_messaage_text(message_text):
        logger.debug('This message is not a target.')
        return

    # TODO: 対象メッセージであれば、 SpreadSheet への格納を行います。
    race_date = '2021-04-22'
    race_name = 'なんちゃら記念レース'

    # どのレースの予想として格納されたか、発言者へ通知します。
    # NOTE: 「でないとどのレースの予想として扱われたのかわからないよね……」
    #       という意見が出たので、追加された機能です。そりゃそうだ。
    send_message = (
        f'{user_profile.display_name} さん\n'
        f'今回のメッセージ "{message_text}" は {race_date} {race_name} の予想として受理されました!'
    )
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=send_message),
    )


def is_target_messaage_text(inspection_target):

    # [int].[int].[int].[int].[int] の形式を、対象メッセージと判断しています。
    # その形式であれば True を返却します。
    splitted = inspection_target.split('.')
    if len(splitted) != 5:
        return False
    for s in splitted:
        if not is_int(s):
            return False
    return True


def is_int(string):
    try:
        float(string)
    except ValueError:
        return False
    else:
        return float(string).is_integer()


if __name__ == '__main__':
    app.run()
