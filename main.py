import os
import requests
import re
from models import *
from vk_logic import get_post, get_post_photos, get_post_videos, get_post_audios, get_post_attachment_types
from pydantic import ValidationError
import telebot

tg_token = os.getenv('TG_TOKEN')
bot = telebot.TeleBot(tg_token)


def get_post_id(user_message):
    try:
        post_id = re.search(r'wall(.\d*_\d*)', user_message).group(1)
        return post_id
    except AttributeError:
        return False


def text_handler(vk_post):
    formatted_text = vk_post.text
    formatted_text = formatted_text.split()
    # TODO: format text to display links


def prefered_videofile(video):
    if video.files.mp4_480 is not None and video.duration < 90:
        return video.files.mp4_480
    elif video.files.mp4_360 is not None and video.duration < 120:
        return video.files.mp4_360
    elif video.files.mp4_240 is not None and video.duration < 180:
        return video.files.mp4_240
    elif video.files.mp4_144 is not None and video.duration < 240:
        return video.files.mp4_144
    else:
        raise AttributeError


@bot.message_handler(commands=["start"])
def bot_start(m, res=False):
    bot.send_message(m.chat.id, 'Привет! Пришли мне ссылку на пост из ВК и я преобразую его в сообщение. '
                                '\nНапример <code>https://vk.com/wall-58509583_543307</code>'
                                '\nИли <code>https://vk.com/feed?w=wall-58509583_549358</code>',
                     parse_mode='HTML'
                     )


@bot.message_handler(content_types=["text"])
def bot_handle_message(message):
    post_id = get_post_id(message.text)
    if post_id:
        try:
            vk_post = get_post(post_id)
        except IndexError:
            # response from API is empty
            return bot.send_message(message.chat.id, 'Не удалось получить доступ к записи!')
    else:
        return bot.send_message(
            message.chat.id, 'Ошибка. Пришлите ссылку на пост!'
                             '\nНапример <code>https://vk.com/wall-58509583_543307</code>'
                             '\nИли <code>https://vk.com/feed?w=wall-58509583_549358</code>',
            parse_mode='HTML'
        )
    post_attachment_types = get_post_attachment_types(vk_post)
    message_medias = list()
    message_audios = list()
    if post_attachment_types:
        if 'photo' in post_attachment_types:
            vk_post_photos = get_post_photos(vk_post)
            for photo_url in vk_post_photos:
                message_medias.append(telebot.types.InputMediaPhoto(photo_url))
        if 'video' in post_attachment_types:
            bot.send_message(message.chat.id, 'В посте есть видео, мне нужно загрузить их чтобы отправить вам.'
                                              '\nСекундочку...')
            vk_post_videos = get_post_videos(vk_post)
            try:
                for video in vk_post_videos.items:
                    # Just limitations
                    if video.platform is None and video.duration < 241:
                        try:
                            # Download video to send
                            response = requests.get(prefered_videofile(video))
                            message_medias.append(
                                telebot.types.InputMediaVideo(media=response.content, supports_streaming=True))
                        except requests.RequestException:
                            return bot.send_message(message.chat.id, f'Не удалось получить видео "<i>{video.title}</i>"'
                                                                     f' из поста!', parse_mode='HTML')
                        except AttributeError:
                            vk_post.text += f'\n{video.player} - "VK"'
                            bot.send_message(message.chat.id, f'Видео "<i>{video.title}</i>" выходит за ограничения '
                                                              f'бота, '
                                                              f'либо невозможно получить качество видео подходящее под '
                                                              f'ограничения.\nВидео будет добавлено в виде ссылки.',
                                             parse_mode='HTML'
                                             )
                    else:
                        vk_post.text += f'\n{video.player} - {"VK" if video.platform is None else video.platform}'
                        bot.send_message(message.chat.id, f'Видео "<i>{video.title}</i>" выходит за ограничения бота, '
                                                          f'либо '
                                                          f'размещено вне ВКонтакте!\nВидео будет добавлено в виде '
                                                          f'ссылки.', parse_mode='HTML')
            except AttributeError:
                return bot.send_message(message.chat.id, 'Не удалось получить видео из поста!')
        if 'audio' in post_attachment_types:
            vk_post_audios = get_post_audios(vk_post)
            for audio in vk_post_audios.items:
                message_audios.append(
                    telebot.types.InputMediaAudio(
                        media=audio.url, duration=audio.duration,
                        caption=f'{audio.artist} - {audio.title}'
                    )
                )
        # the text of the post should be added to the first InputMedia "caption" field.
        try:
            message_medias[0].caption = vk_post.text
            bot.send_media_group(message.chat.id, message_medias)
            if message_audios:
                bot.send_media_group(message.chat.id, message_audios)
        except IndexError:
            return bot.send_message(message.chat.id, vk_post.text)
    else:
        bot.send_message(message.chat.id, vk_post.text)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
