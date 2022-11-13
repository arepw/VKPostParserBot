import os
import requests
from models import *
from pydantic import ValidationError

vk_token = os.getenv('VK_SKEY')


def get_post(post_id):
    url = f'https://api.vk.com/method/wall.getById?posts={post_id}&access_token={vk_token}&v=5.131'
    try:
        response = requests.get(url)
        current_post = Post(**response.json()['response'][0])
    except ValidationError as e:
        return e
    except requests.RequestException:
        return 'Check your Internet connection'
    return current_post


def get_post_attachments(post_item, attachment_type):
    """
    get post's attachments of a certain type.
    supported attachment types: 'photo', 'video' (not yet)
    """
    attachments_list = list(filter(lambda item: item.type == attachment_type, post_item.attachments))
    return attachments_list


def get_post_photos(post_item):
    attachments_list = get_post_attachments(post_item, attachment_type='photo')
    photos = list()
    for item in attachments_list:
        for size in item.photo.sizes:
            # TODO: Do something if there's no size.type == 'z'
            if size.type == 'z':
                photos.append(size.url)
    return photos
