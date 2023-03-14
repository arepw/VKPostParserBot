import os
from dotenv import load_dotenv
import requests
import re
from models import *
from pydantic import ValidationError

load_dotenv()
vk_oauth = os.getenv('VK_OAUTH')


def get_post(post_id):
    url = f'https://api.vk.com/method/wall.getById?posts={post_id}&access_token={vk_oauth}&v=5.131'
    try:
        response = requests.get(url)
        current_post = Post(**response.json()['response'][0])
    except ValidationError as e:
        return e
    except requests.RequestException as e:
        return e
    return current_post


def get_post_attachments(post_item, attachment_type):
    """
    get post's attachments of a certain type.
    supported attachment types: 'photo', 'video'
    :return: list[Attachment]
    """
    attachments_list = list(filter(lambda item: item.type == attachment_type, post_item.attachments))
    return attachments_list


def get_post_attachment_types(post_item):
    """
    get post's attachment types.
    :return: list[str]: attachment types for the post
    """
    attachment_types = ['photo', 'video', 'audio']
    post_attachment_types = list()
    if post_item.attachments is not None:
        for attachment_type in attachment_types:
            if get_post_attachments(post_item, attachment_type):
                post_attachment_types.append(attachment_type)
        return post_attachment_types
    else:
        return False


def get_post_photos(post_item):
    """
    get urls of the post's photos
    :return: list[str]: urls for the photos
    """
    attachments_list = get_post_attachments(post_item, attachment_type='photo')
    photos = list()
    # The VK attachment with type 'photo' has multiple variations of sizes.
    # x, y, z, m (in ascending order) are the highest quality types.
    sizes_dict = {
        10: 'w',
        9: 'z',
        8: 'y',
        7: 'x'
    }
    for item in attachments_list:
        for size in item.photo.sizes:
            # getting length of photo.sizes to define max. size type of the photo
            # that we can get.
            if size.type == sizes_dict.get(len(item.photo.sizes)):
                photos.append(size.url)
    return photos


def get_post_videos(post_item):
    """
    get Video items from the post
    :return: VideoList
    """
    attachments_list = get_post_attachments(post_item, attachment_type='video')
    videos_ids = str()
    for item in attachments_list:
        videos_ids += f'{item.video.owner_id}_{item.video.id},'
    url = f'https://api.vk.com/method/video.get?videos={videos_ids}&access_token={vk_oauth}&v=5.131'
    try:
        response = requests.get(url)
        videos = VideosList(**response.json()['response'])
    except ValidationError as e:
        return e
    except requests.RequestException as e:
        return e
    return videos


def get_post_audios(post_item):
    attachments_list = get_post_attachments(post_item, attachment_type='audio')
    audio_ids = str()
    for item in attachments_list:
        audio_ids += f'{item.audio.owner_id}_{item.audio.id},'
    url = f'https://api.vk.com/method/audio.getById?audios={audio_ids}&access_token={vk_oauth}&v=5.131'
    try:
        response = requests.get(url)
        audios = AudiosList(**response.json())
    except ValidationError as e:
        return e
    except requests.RequestException as e:
        return e
    return audios
