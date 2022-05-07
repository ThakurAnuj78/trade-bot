import logging
import os

import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - {%(pathname)s:%(lineno)d} - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))
APP_NAME = os.getenv('APP_URL')
TOKEN = os.getenv('TOKEN')
LOGIN_URL = 'get_authcode_url'
STOCK_DATA_URL = 'get_data'


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('TradeBot has started. Enter stock name to get quote.')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Click below link for stock names.')


def login(update, context):
    url = f'{APP_NAME}{LOGIN_URL}'
    response = requests.get(url)
    chat_id = update.message.chat_id
    if response.status_code == 200:
        text=response.content
    else:
        text='No url found'
    context.bot.send_message(chat_id=chat_id, text=text)


def post_stock_data(update, context):
    url = f'{APP_NAME}{STOCK_DATA_URL}?stock={update.message.text}'
    response = requests.get(url)
    chat_id = update.message.chat_id
    text = 'No such stock found'
    # print(response.__dict__)
    if response.status_code == 200:
        response_json = response.json()
        data = response_json['data']
        if data:
            data = data[0]
            name = data['n']
            change = data['v']['ch']
            change_percentage = data['v']['chp']
            open_price = data['v']['open_price']
            previous_close = data['v']['prev_close_price']
            high = data['v']['high_price']
            low = data['v']['low_price']
            ltp = data['v']['lp']
            text = f'**Name:** {name}\nLTP: ₹{ltp}\n**Change:** ₹{change}\n**Change Percentage:** {change_percentage}%\n**Previous Close:** ₹{previous_close}\n**Open:** ₹{open_price}\n**High:** ₹{high}\n**Low:** ₹{low}'
    context.bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=update.message.message_id)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler('login', login))

    # on non command i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, post_stock_data))

    # log all errors
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=APP_NAME + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()