import json
import datetime
import random
from telegram_api import Bot
from log import append_bot_operation_data
from json import JSONDecodeError


class User:
    __TIME_SEND_MESSAGE: datetime.datetime = datetime.datetime.now()

    def __init__(self, bot: Bot) -> None:
        self.time_of_last_saved_message: int = bot.get_updates()["result"][-1]["message"]["date"]
        self.bot = bot

    @staticmethod
    def time_to_sleep() -> bool:
        return datetime.datetime.now().hour < 10

    @staticmethod
    def get_word_to_remember() -> tuple[str, str, int] | None:
        """return translation word, english word and them index"""
        try:
            with open("words_to_remember.json", "r") as file:
                words_to_remember = json.load(file)["learning"]
                num = len(words_to_remember)
                index = random.randrange(0, num) if num else 0
                english_word: str = iter(words_to_remember[index][0]).__next__()  # take one random word adn translation
                translation: str = words_to_remember[index][0][english_word]  # take translation word(russian)
                return english_word, translation, index
        except FileNotFoundError:
            return None

    def answer_right(self, index: int) -> None:
        with open("words_to_remember.json", "r") as file:
            words_to_remember = json.load(file)
            count = words_to_remember["learning"][index][-1]["count"] + 1
            if count == 20:
                english_word, translation = words_to_remember["queue"].pop(0)
                words_to_remember["learning"][index] = [{english_word: translation}, {"count": 0}]
                self.bot.send_message("you has learned english word")
            else:
                words_to_remember["learning"][index][-1]["count"] = count

        with open("words_to_remember.json", "w") as file:
            json.dump(words_to_remember, file, ensure_ascii=False, indent=4)

    @staticmethod
    def answer_wrong(index: int) -> None:
        with open("words_to_remember.json", "r") as file:
            words_to_remember = json.load(file)
            words_to_remember["learning"][index][-1]["count"] = 0

        with open("words_to_remember.json", "w") as file:
            json.dump(words_to_remember, file)

    def check_user_answer(self, index: int, translation) -> None:
        while True:
            new_message = self.user_has_sent_a_new_massage()
            if new_message:
                text_of_the_message: str = new_message["message"]["text"]
                message_id: int = new_message["message"]["message_id"]
                chat_id: int = new_message["message"]["chat"]["id"]

                if text_of_the_message.lower() == translation.lower():
                    self.bot.send_message("right")
                    self.answer_right(index)
                    self.__TIME_SEND_MESSAGE = datetime.datetime.now() + datetime.timedelta(hours=1)
                    self.bot.delete_message(message_id=message_id, chat_id=chat_id)
                    break
                else:
                    self.bot.send_message("wrong, try again")
                    self.answer_wrong(index)
                    self.bot.delete_message(message_id=message_id, chat_id=chat_id)

    def asks_translation_of_english_word(self) -> None:
        """"ask the user to translation of english word """
        if self.__TIME_SEND_MESSAGE <= datetime.datetime.now():
            english_word__translation__index = self.get_word_to_remember()

            if english_word__translation__index:
                english_word, translation, index = english_word__translation__index
                self.bot.send_message(f"{english_word}")

                self.check_user_answer(index, translation)

    def user_has_sent_a_new_massage(self) -> dict | None:
        """if user has sent a new message then function return dic else return None"""
        updates: dict = self.bot.get_updates()
        time_of_the_last_message: int = updates["result"][-1]["message"]["date"]
        text_of_the_last_message: str = updates["result"][-1]["message"]["text"]

        if self.time_of_last_saved_message < time_of_the_last_message:
            self.time_of_last_saved_message = time_of_the_last_message
            append_bot_operation_data("BOT HAS GOT MESSAGE", text_of_the_last_message)
            return updates["result"][-1]

    def get_a_new_word(self) -> tuple[str, str]:
        """"return a new English word to remember -> tuple[english_word, translation]"""
        while True:
            new_message = self.user_has_sent_a_new_massage()
            if new_message:
                text_of_the_last_message = new_message["message"]["text"]
                if " : " in text_of_the_last_message:
                    english_word, translation = text_of_the_last_message.split(" : ")
                    return english_word, translation
                else:
                    self.bot.send_message("incorrect entry")

    def append_a_new_word(self) -> None:
        """"append to file a new word to remember """
        english_word, translation = self.get_a_new_word()

        try:
            with open("words_to_remember.json", "r") as file:
                words_to_remember: dict = json.load(file)
        except (FileNotFoundError, JSONDecodeError):
            words_to_remember: bool = False

        with open("words_to_remember.json", "w") as file:
            if words_to_remember:
                if 5 >= len(words_to_remember["learning"]):
                    words_to_remember["learning"].append([{english_word: translation}, {"count": 0}])
                else:
                    words_to_remember["queue"].append((english_word, translation))

                json.dump(words_to_remember, file, ensure_ascii=False, indent=4)
            else:
                words_to_remember = {"learning": [({english_word: translation}, {"count": 0})], "queue": []}
                json.dump(words_to_remember, file, ensure_ascii=False, indent=4)
            append_bot_operation_data("ADD A NEW WORD", f"english word: {english_word}, russian word{translation}")
            print("ADD A NEW WORD", f"english word: {english_word}, russian word{translation}")
