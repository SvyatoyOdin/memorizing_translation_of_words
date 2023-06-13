import os
from dotenv import load_dotenv
from log import append_bot_operation_data, append_exception_data
from telegram_api import Bot
from user import User


load_dotenv()
URL = f'https://api.telegram.org/bot{os.getenv("token")}'
USER_ID = int(os.getenv("user_id"))


def main():
    bot = Bot(url=URL, user_id=USER_ID)
    user = User(bot=bot)

    while True:
        if not user.time_to_sleep():
            user.asks_translation_of_english_word()

        new_message = user.user_has_sent_a_new_massage()
        if new_message:
            text_of_the_last_message = new_message["message"]["text"]
            if text_of_the_last_message in "/add words":
                bot.send_message("you can add a new word. <b>Write a new word in this format: word in English : "
                                 "translation</b>", parse_mode="HTML")
                user.append_a_new_word()
            else:
                bot.send_message("I don't understand")


if __name__ == '__main__':
    try:
        append_bot_operation_data("BOT STARTED")
        main()
        append_bot_operation_data("BOT HAS STOPPED SUCCESSFUL")
    except KeyboardInterrupt:
        append_bot_operation_data("BOT HAS STOPPED SUCCESSFUL")
    except BaseException as ex:
        exception_number = append_exception_data(ex)
        append_bot_operation_data(type_data="BOT HAS STOPPED UNSUCCESSFUL",
                                  data=f"{ex.__str__()}; EXCEPTION NUMBER - {exception_number}")
