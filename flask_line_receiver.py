"""flask_line_receiver

LINE とのやりとりを行うスクリプトです。
"""

# Built-in modules.
import traceback

# Third-party modules.
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import mojimoji

# User modules.
import utils
import consts
import spread_sheet_expectation_sender
import spread_sheet_hot_race_sender

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
    try:
        on_get_message_main(event)
    except Exception as ex:

        # サーバ側にもログは出ていてほしいので、出します。
        # NOTE: Slack へメッセージを送ったあとに raise ex するほうがキレイに見えます。
        #       しかし、 Slack でエラーが発生したとき怖い(何も解らなくなる)ので、
        #       ここで print_exc することにしました。
        logger.error('Error raised in flask_line_receiver, print_exc below.')
        traceback.print_exc()

        # NOTE: str(ex) によりメッセージが出力されます。
        utils.send_slack_message(
            f'Error raised in flask_line_receiver: {ex}\n'
            'Check the detail log: `heroku logs --num 1500 --app denuma-program --ps web`'
        )

    # NOTE: 新しい機能でエラーが発生しても、もとの機能に影響を及ぼさないように、
    #       「もとの機能のあとに」新しい関数を呼んでいます。
    try:
        on_get_message_sub(event)
    except Exception as ex:
        raise ex


def on_get_message_main(event):
    """on_get_message のメイン処理です。コレ自体を try でかこうため、分離
    ここで行うことは……
    - G1 グループからのメッセージであることを確認。(event.source.group_id で検証可能。)
    - 発言者名を取得。(line_bot_api.get_profile で確認可能。)
    - メッセージの内容を取得し、「予想」メッセージであれば Spread Sheet へ格納。
    """

    # event から抜くべき情報を抜きます。まずは Group id です。
    group_id = event.source.group_id

    # 返答するための token です。
    # NOTE: line_bot_api.reply_message(reply_token, TextSendMessage(text='...')) と使用。
    reply_token = event.reply_token

    # 発言者の id です。
    user_id = event.source.user_id

    # メッセージの内容です。
    # NOTE: スペースが混じっていたり、全角が混じっていたりするのは看過してやります。
    message_text = mojimoji.zen_to_han(event.message.text).replace(' ', '')

    # メッセージが処理対象でなければ、この先の処理はまったく不要です。
    # 処理対象メッセージの条件はこちら↓
    #     - G1 group からの post である。
    #     - 処理対象メッセージである。

    if group_id != consts.LINE_G1_GROUP_ID:
        logger.debug(f'This message is sent from unexpected group. group_id: {group_id}')
        return

    if not is_target_messaage_text(message_text):
        logger.debug(f'This message is not a target. But user id is... {user_id}')
        return

    # ここまで来たら、処理対象です。
    logging_dict = dict(
        group_id=group_id,
        reply_token=reply_token,
        user_id=user_id,
        message_text=message_text,
    )
    logger.debug(f'This message is a target. {logging_dict}')

    # 発言者の情報を取得します。。
    # NOTE: ドキュメント https://github.com/line/line-bot-sdk-python#get_profileself-user_id-timeoutnone
    try:
        user_profile = line_bot_api.get_profile(user_id)
    except LineBotApiError as ex:
        # NOTE: 発言者が Messaging API channel と友達でない場合は 404 エラーが発生します。
        #       その場合は友達登録を促します。
        if ex.status_code == 404:
            send_message = (
                'xxx さん\n'
                'ゴメンなさい! 今回のメッセージは受理されませんでした!\n'
                '私をご利用になるためには、私を友達登録してください!'
            )
            reply_or_push_message(reply_token, group_id, send_message)
            return

        # そうでないエラーの場合は、フツーに打ち上げます。
        raise ex

    # 対象メッセージであれば、 SpreadSheet への格納を行います。
    race_date, race_name = spread_sheet_expectation_sender.send(user_id, message_text)

    # どのレースの予想として格納されたか、発言者へ通知します。
    # NOTE: 「でないとどのレースの予想として扱われたのかわからないよね……」
    #       という意見が出たので、追加された機能です。そりゃそうだ。
    send_message = (
        f'{user_profile.display_name} さん\n'
        f'今回のメッセージ "{message_text}" は {race_date} {race_name} の予想として受理されました!'
    )
    reply_or_push_message(reply_token, group_id, send_message)


def on_get_message_sub(event):
    """
    この関数は、LINEのメーセージが'勝負'のみの内容だった時のみ動き出します。
    -'勝負'メッセージが届くと spread_sheet_hot_race_sender.py に user_id を引数に渡します。
    -処理が終わると空リターン
    """

    # ここに書いていくと、グループからメッセージが送られたときに
    # 呼び出されます。
    # こちら↓に、この関数内で使える変数を列挙しますので、それを使って仕上げてください。
    # たぶんこの関数の中でエラーが出ても、すでに動いている「予想登録機能」には影響ないと思います。
    # ガンガンテストしちゃってください。
    # Heroku にアップしてテストした場合は
    #     heroku logs --num 500 --tail --app denuma-program
    # このコマンドで、 print の内容が出ます。

    group_id = event.source.group_id
    reply_token = event.reply_token
    user_id = event.source.user_id
    message_text = mojimoji.zen_to_han(event.message.text).replace(' ', '')
    print(dict(
        group_id=group_id,
        reply_token=reply_token,
        user_id=user_id,
        message_text=message_text,
    ))

    # 発言者の情報を取得します。（パクる）
    # NOTE: ドキュメント https://github.com/line/line-bot-sdk-python#get_profileself-user_id-timeoutnone
    try:
        user_profile = line_bot_api.get_profile(user_id)
    except LineBotApiError as ex:
        # NOTE: 発言者が Messaging API channel と友達でない場合は 404 エラーが発生します。
        #       その場合は友達登録を促します。
        if ex.status_code == 404:
            send_message = (
                'xxx さん\n'
                'ゴメンなさい! 今回のメッセージは受理されませんでした!\n'
                '私をご利用になるためには、私を友達登録してください!'
            )
            reply_or_push_message(reply_token, group_id, send_message)
            return

    #メッセージ内容が'勝負'なら処理を実行してメッセージを返す。
    if message_text == '勝負':
        return_data = spread_sheet_hot_race_sender.send_game(user_id)
        print(return_data)

        #is_gameが Trueであるならば、勝負レースとしてメッセージを作成する。
        if return_data["is_game"]:
            send_message = (
            f'{user_profile.display_name} さんが\n'
            f'{return_data["date"]} {return_data["race_name"]}を\n'
            '🔥勝負レース🔥に指定しました!!'
            )
        else:
            send_message = (
            f'{user_profile.display_name} さん\n'
            f'{return_data["date"]} {return_data["race_name"]}の\n'
            '勝負レースをキャンセルしました。'
            )

        reply_or_push_message(reply_token, group_id, send_message)

    else:
        return
    # 試しにむりやりエラーを起こして、元機能に影響がないことを確認します。
    # raise Exception('むりやり起こしたエラーだよー。')


def is_target_messaage_text(inspection_target: str) -> bool:
    """処理対象メッセージであれば True を返します。
    [int].[int].[int].[int].[int] の形式を、対象メッセージと判断しています。
    """

    splitted = inspection_target.split('.')
    if len(splitted) != 5:
        return False
    for s in splitted:
        if not is_int(s):
            return False
    return True


def is_int(string: str) -> bool:
    """int 形式の string であれば True を返します。
    NOTE: これくらいビルトインであってほしいよねえ。
    """

    try:
        float(string)
    except ValueError:
        return False
    else:
        return float(string).is_integer()


def reply_or_push_message(reply_token: str, to: str, send_message: str):
    """reply_message を試し、ダメなら push_message を試します。
    NOTE: reply_message で "Invalid reply token" が発生したので追加した関数です。
          発生原因はおそらくこれ。
          > 応答トークンは一定の期間が経過すると無効になるため、メッセージを受信したらすぐに応答を返す必要があります。
          > https://developers.line.biz/ja/reference/messaging-api/#send-reply-message
          しかし現在の無料 Heroku 運用では仕方ない……絶対発生しうるエラーです。
          なので、 push_message でフォローを行うことにした、という流れです。
    NOTE: 最初から push_message で良いような気もしますが、
          処理の流れとしては reply_message が正道だと考えます。
          (Heroku が常時起動していれば気にする必要のないもの)
          なので reply_message を排除することはしていません。
    """

    try:
        # とりあえず reply_message を試みます。
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=send_message),
        )
    except LineBotApiError:

        # 一応ロギングはしておきます。
        logger.error(
            'Error raised when reply_message, will try push_message.'
            ' But print_exc below anyways.'
        )
        traceback.print_exc()

        # reply に失敗したら、 reply_token 指定ではなく group_id 指定……
        # (一応 user_id でも可能なので to という変数名にしています)
        # ……でのメッセージ送信を試みます。
        line_bot_api.push_message(
            to,
            TextSendMessage(text=send_message),
        )


if __name__ == '__main__':
    app.run()
