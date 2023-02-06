import os
import random
from pathlib import Path

import requests
from dotenv import load_dotenv


def create_path(picture_name: str, folder_name: str, ) -> str:
    """
    Функция создает папку и возвращает путь до файла в этой папке.
    Args:
        picture_name: Название файла.
        folder_name: Название папки, куда нужно будет сложить файлы.
    """

    folder = Path.cwd() / folder_name
    Path(folder).mkdir(parents=True, exist_ok=True)
    return str(folder / picture_name)


def save_random_comics(filepath: str) -> dict:
    """
    Сохраняет рандомный комикс и возвращает словарь с информацией о комиксе.
    Args:
        filepath: путь к комиксу
    Returns:
        {
            'alt': описание комикса,
            'day': str,
            'img': ссылка на картинку,
            'link': str,
            'month': str,
            'news': str,
            'num': номер комикса,
            'safe_title': заголовок,
            'title': заголовок,
            'transcript': str,
            'year': 'str}
    """

    random_comic = random.randint(1, ALL_COMICS)

    url = f'https://xkcd.com/{random_comic}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comic = response.json()

    comic_book_picture = requests.get(comic['img'])
    comic_book_picture.raise_for_status()

    with open(filepath, 'wb') as file:
        file.write(comic_book_picture.content)

    return response.json()


def get_comic_upload_address(access_token: str, api_version: float, ) -> str:
    """
    Получение адреса для загрузки картинки.
    Args:
        access_token: токен доступа к сообществу в социальной сети "ВКонтакте".
        api_version: версия апи Вконтакте.
    """

    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {
        'access_token': access_token,
        'v': api_version
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def upload_comic_to_server(access_token: str, api_version: float, filepath: str, upload_url: str) -> dict:
    """
    Загрузка картинки на сервер.
    Args:
        access_token: токен доступа к сообществу в социальной сети "ВКонтакте".
        api_version: версия апи Вконтакте.
        filepath: путь к картинке, где она находится.
        upload_url: ссылка на загруженный комикс на сервере.
    """

    payload = {
        'access_token': access_token,
        'v': api_version,
    }
    with open(filepath, 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(upload_url, params=payload, files=files)
        response.raise_for_status()
    return response.json()


def save_comic_to_the_group_album(access_token: str, api_version: float, picture: dict) -> dict:
    """
    Сохранение картинки в альбоме группы.
    Args:
        access_token: токен доступа к сообществу в социальной сети "ВКонтакте".
        api_version: версия апи Вконтакте.
        picture: картинка, её хэш на сервере, сервер, полученные после загрузки на сервер.
    """

    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload = {
        'access_token': access_token,
        'v': api_version,
        'server': picture['server'],
        'photo': picture['photo'],
        'hash': picture['hash']
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    return response.json()


def post_comic_on_a_group_wall(access_token: str, api_version: float, picture_description: str, saved_picture: dict) -> dict:
    """
    Публикация картинки на стене группы.
    Args:
        access_token: токен доступа к сообществу в социальной сети "ВКонтакте".
        api_version: версия апи Вконтакте.
        picture_description: описание комикса.
        saved_picture: Данные о сохраненной картинке полученные из photos.saveWallPhoto.
    """

    owner_id = saved_picture['response'][0]['owner_id']
    media_id = saved_picture['response'][0]['id']

    url = 'https://api.vk.com/method/wall.post'
    payload = {
        'access_token': access_token,
        'v': api_version,
        'owner_id': -218466610,
        'from_group': True,
        'attachments': f'photo{owner_id}_{media_id}',
        'message': picture_description
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    return response.json()


def main():
    """
    Запуск программы.
    """

    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    vk_version_api = 5.131

    filepath_comic = create_path(picture_name='comic.png', folder_name='comics')
    comic = save_random_comics(filepath_comic)
    upload_address = get_comic_upload_address(vk_access_token, vk_version_api)
    upload_comic = upload_comic_to_server(vk_access_token, vk_version_api, filepath_comic,
                                          upload_address)
    Path(filepath_comic).unlink()
    save_comic = save_comic_to_the_group_album(vk_access_token, vk_version_api, upload_comic)
    post_comic = post_comic_on_a_group_wall(vk_access_token, vk_version_api, comic['alt'], save_comic)
    print(f'Комикс опубликован в группе')


if __name__ == '__main__':
    load_dotenv()
    ALL_COMICS = 2732
    main()
