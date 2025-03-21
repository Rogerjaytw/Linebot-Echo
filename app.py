from flask import Flask, request, abort
import logging
import os

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

logging.basicConfig(level=logging.INFO)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    app.logger.info("Signature: " + str(signature))

    try:
        handler.handle(body, signature)
        return 'OK'  # 確保在成功處理後返回 'OK'
    except InvalidSignatureError as e:
        app.logger.error("Invalid signature. Please check your channel access token/channel secret.")
        app.logger.error(f"Error: {e}")
        abort(400)
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        abort(500)  # 處理其他可能的錯誤


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )

if __name__ == "__main__":
    app.run()