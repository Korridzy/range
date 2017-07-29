import requests
import re
import json
import codecs
import pymorphy2
import logging

logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'/home/suprime/mylog.log')

reader = codecs.getreader("utf-8")

morph = pymorphy2.MorphAnalyzer()

TELEGRAM_BOT_TOKEN = 'get your own bot, sir!'
YANDEX_TRANSLATE_TOKEN = 'get your own token, bro!'
YANDEX_DICT_TOKEN = 'get your own token, dude!'

try:
    from local_settings import *
except:
    pass

class TeleBotApi():
    """
        Класс изолирующий работу с Telegram Bot API
    """
    def __init__(self):
        self.api_prefix = "https://api.telegram.org/bot{0}".format(TELEGRAM_BOT_TOKEN)

    def send_message(self, chat_id, message_text):
        data = {
            'chat_id': chat_id,
            'text': message_text
        }
        logging.debug(data)
        requests.post('{0}/sendMessage'.format(self.api_prefix), data=data)

class YandexDictApi():
    """
        Класс изолирующий работу с Яндекс.Словарями
    """
    def determ_speech_part(self, word):
        params = {'key': YANDEX_DICT_TOKEN, 'lang': 'ru-ru', 'text': word}
        result = requests.get('https://dictionary.yandex.net/api/v1/dicservice.json/lookup', params=params)
        result = result.json()
        if len(result["def"]) > 0:
            if "pos" in result["def"][0]:
                pos = result["def"][0]["pos"]
                if pos == 'adjective':
                    pos = 'adjf'
                return pos
        return ""

class YandexTranslateApi():
    """
        Класс изолирующий работу с Яндекс.Перевод
    """
    def is_text_russian(self, text):
        """
            Проверяет, русский ли текст
        """
        params = {'key': YANDEX_TRANSLATE_TOKEN, 'text': text}
        result = requests.get('https://translate.yandex.net/api/v1.5/tr.json/detect', params=params)
        result = result.json()
        if result['lang'] == 'ru':
            return True
        return False

class Message():
    """
        Здесь живёт всякая логика работы с сообщениями
    """
    def __init__(self, updateObject):
        self.chat_id = updateObject['message']['chat']['id']
        self.message_text = updateObject['message']['text']

    def is_message_russian(self):
        return YandexTranslateApi().is_text_russian(self.message_text)

    def determ_pos(self, word):
        parses = morph.parse(word)
        logging.debug(parses)
        if len(parses) > 0:
            first_parse = parses[0]
            return first_parse.tag.POS.lower()
        #Какбы на случай, если словари pymorph устарели
        return YandexDictApi().determ_speech_part(word)

    def get_message_stats(self, partsList):
        #Удаляем пунктуацию
        message = re.sub(r"[^А-Яа-яёЁ ]", '', self.message_text)
        #Разбиваем на слова
        words = message.split(' ')
        #Делаем заготовку ответа
        result = {}
        for key in partsList:
            result[key] = 0
        #Определяем количество заданных частей речи
        for word in words:
            logging.debug(word)
            pos = self.determ_pos(word)
            logging.debug(pos)
            if pos in partsList:
                result[pos] += 1
        return result

    def reply(self, replyText):
        TeleBotApi().send_message(self.chat_id, replyText)

class UpdatesReceiver():
    def on_post(self, req, resp):
        """
            Обработчик входящих событий
        """
        #Инициализиурем объект сообщение
        updateObject = json.load(reader(req.bounded_stream))
        message = Message(updateObject)
        #проверяем, русский ли пришёл текст
        if(message.is_message_russian()):
            stats = message.get_message_stats(['noun', 'adjf', 'verb'])
            message.reply("Существительных: {noun}, Прилагательных: {adj}, Глаголов: {verb}".format(noun=stats['noun'], adj=stats['adjf'], verb=stats['verb']))
        #Если текст не русский
        else:
            message.reply("Пишите на русском языке, плз")


        