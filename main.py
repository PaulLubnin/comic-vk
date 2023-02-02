import os
from pathlib import Path
from pprint import pprint

import requests
from dotenv import load_dotenv

load_dotenv()
VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')
VK_VERSION_API = 5.131


def create_path(picture_name: str, folder_name: str, ) -> str:
    """
    Функция создает папку и возвращает её путь.
    Args:
        picture_name: Название файла.
        folder_name: Название папки, куда нужно будет сложить файлы.
    """

    folder = Path.cwd() / folder_name
    Path(folder).mkdir(parents=True, exist_ok=True)
    return str(folder / picture_name)


def save_to_file(content: bytes, filepath: str) -> None:
    """
    Функция для сохранения книг, обложек книг.
    Args:
        content: Контент в байтах.
        filepath: Путь к файлу.
    """

    with open(filepath, 'wb') as file:
        file.write(content)


def get_comics() -> dict:
    """
    Запрос на получение json с данными о комиксе.
    """

    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def fetch_comic_file() -> bytes:
    """
    Получение картинки.
    """

    url = 'https://imgs.xkcd.com/comics/planet_killer_comet_margarita.png'
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def get_groups() -> dict:
    """
    Запрос на получение групп пользователя.
    """

    url = 'https://api.vk.com/method/groups.get'
    payload = {
        'access_token': VK_ACCESS_TOKEN,
        'v': VK_VERSION_API
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


def get_comic_upload_address() -> dict:
    """
    Получение адреса для загрузки картинки.
    """

    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {
        'access_token': VK_ACCESS_TOKEN,
        'v': VK_VERSION_API
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


def uploading_comic_to_server(filepath: str, upload_url: str) -> dict:
    """
    Загрузка картинки на сервер.
    Args:
        filepath: путь к картинке, где она находится.
        upload_url: ссылка на загруженный комикс на сервере.
    """

    payload = {
        'access_token': VK_ACCESS_TOKEN,
        'v': VK_VERSION_API,
    }
    with open(filepath, 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(upload_url, params=payload, files=files)
        response.raise_for_status()
    return response.json()


def save_comic_to_the_group_album(picture: dict) -> dict:
    """
    Сохранение картинки в альбоме группы.
    args:
        picture: картинка, её хэш на сервере, сервер, полученные после загрузки на сервер.
    """

    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload = {
        'access_token': VK_ACCESS_TOKEN,
        'v': VK_VERSION_API,
        'server': picture['server'],
        'photo': picture['photo'],
        'hash': picture['hash']
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    return response.json()


def posting_comic_on_a_group_wall(picture: dict, saved_picture: dict) -> dict:
    """
    Публикация картинки на стене группы.
    args:
        picture: картинка полученая с xkcd.com.
        saved_picture: Данные о сохраненной картинке полученные из photos.saveWallPhoto.
    """

    owner_id = saved_picture['response'][0]['owner_id']
    media_id = saved_picture['response'][0]['id']

    url = 'https://api.vk.com/method/wall.post'
    payload = {
        'access_token': VK_ACCESS_TOKEN,
        'v': VK_VERSION_API,
        'owner_id': -218466610,
        'from_group': True,
        'attachments': f'photo{owner_id}_{media_id}',
        'message': picture['alt']
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    comic = get_comics()
    # print('comic')
    # pprint(comic)

    groups = get_groups()
    # print('groups')
    # pprint(groups)

    upload_address = get_comic_upload_address()
    # print('upload_address')
    # pprint(upload_address)

    file_path = create_path(picture_name='comic2.png', folder_name='comics')
    comic_file = fetch_comic_file()
    save_to_file(comic_file, file_path)

    upload_comic = uploading_comic_to_server(file_path, upload_address['response']['upload_url'])
    # print('upload_comic')
    # pprint(upload_comic)

    save_comic = save_comic_to_the_group_album(upload_comic)
    # print('save_comic')
    # pprint(save_comic)

    post_comic = posting_comic_on_a_group_wall(comic, save_comic)
    # print('post_comic')
    # pprint(post_comic)
