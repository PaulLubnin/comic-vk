import os
from pathlib import Path
from pprint import pprint

import requests
from dotenv import load_dotenv

load_dotenv()
VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')


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
        'v': 5.131
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


def get_comic_upload_address() -> dict:
    """
    Запрос на получение адреса для загрузки фото.
    """

    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {
        'access_token': VK_ACCESS_TOKEN,
        'v': 5.131
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


def uploading_comic_to_server(filepath: str) -> dict:
    """
    Загрузка картинки на сервер.
    Args:
        filepath: путь к файлу, где он находится.    """

    url = 'https://pu.vk.com/c850720/ss2290/upload.php?act=do_add&mid=102306997&aid=-14&gid=0&hash=ea18508455fa043a0a0de68f2794c124&rhash=5047f84126a688f122f00db34fd93f25&swfupload=1&api=1&wallphoto=1'

    payload = {
        'access_token': VK_ACCESS_TOKEN,
        'v': 5.131,
    }
    with open(filepath, 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(url, params=payload, files=files)
        response.raise_for_status()
    return response.json()


def save_comic_to_the_group_album(picture: dict) -> dict:
    """
    Сохранение картинки на стене группы.
    """

    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {
        'access_token': VK_ACCESS_TOKEN,
        'v': 5.131,
        'server': picture['server'],
        'photo': picture['photo'],
        'hash': picture['hash']
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    # pprint(get_comics())
    # pprint(get_groups())
    # pprint(get_photo_upload_address())
    # pprint(uploading_comic_to_server())

    file_path = create_path(picture_name='comic1.png', folder_name='comics')
    comic_file = fetch_comic_file()
    save_to_file(comic_file, file_path)
    comic = uploading_comic_to_server(file_path)
    pprint(save_comic_to_the_group_album(comic))
