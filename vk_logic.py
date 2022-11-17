import os
import requests
from models import *
from pydantic import ValidationError

vk_token = os.getenv('VK_SKEY')


def get_post(post_id):
    url = f'https://api.vk.com/method/wall.getById?posts={post_id}&access_token={vk_token}&v=5.131'
    try:
        response = requests.get(url)
        print(response.json())
        current_post = Post(**response.json()['response'][0])
    except ValidationError as e:
        return e
    except requests.RequestException as e:
        return e
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


def get_post_videos(post_item, vk_oauthkey):
    attachments_list = get_post_attachments(post_item, attachment_type='video')
    videos_ids = str()
    for item in attachments_list:
        videos_ids += f'{item.video.owner_id}_{item.video.id},'
    url = f'https://api.vk.com/method/video.get?videos={videos_ids}&access_token={vk_oauthkey}&v=5.131'
    try:
        response = requests.get(url)
        videos = VideosList(**response.json()['response'])
    except ValidationError as e:
        return e
    except requests.RequestException as e:
        return e
    videos_urls = list()
    for video in videos.items:
        videos_urls.append(video.player)
    return videos_urls
