import os
import requests
import re
from models import *
from vk_logic import get_post, get_post_photos
from pydantic import ValidationError
import telebot

tg_token = os.getenv('TG_TOKEN')

bot = telebot.TeleBot(tg_token)


@bot.message_handler(commands=["start"])
def bot_start(m, res=False):
    bot.send_message(m.chat.id, 'Привет! Пришли мне ссылку на пост из ВК и я преобразую его в сообщение. '
                                'Например - <code>https://vk.com/wall-58509583_543307</code>',
                     parse_mode='HTML'
                     )


@bot.message_handler(content_types=["text"])
def bot_handle_message(message):
    try:
        post_id = re.search(r'wall(.\d*_\d*)', message.text).group(1)
    except AttributeError:
        return bot.send_message(
            message.chat.id, 'Ошибка. Пришлите ссылку на пост! Например - '
                             '<code>https://vk.com/wall-58509583_543307</code>',
            parse_mode='HTML'
        )
    vk_post = get_post(post_id)
    vk_post_photos = get_post_photos(vk_post)
    message_medias = list()
    for count, photo_url in enumerate(vk_post_photos):
        if count == 0:
            message_medias.append(telebot.types.InputMediaPhoto(
                photo_url, caption=vk_post.text))
        else:
            message_medias.append(telebot.types.InputMediaPhoto(photo_url))
    return bot.send_media_group(message.chat.id, message_medias)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
