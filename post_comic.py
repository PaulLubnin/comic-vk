import os
import random
from pathlib import Path

import requests
from dotenv import load_dotenv


class VKErrors(requests.HTTPError):
    pass


def check_vk_server_response(response: dict, message: str):
    """
    Проверяет ответ сервера ВКонтакте.
    """

    if 'error' in response:
        raise VKErrors(message)


def get_file_path_in_created_folder(file_name: str, folder_name: str, ) -> str:
    """
    Функция создает папку и возвращает путь до файла в этой папке.
    Args:
        file_name: Название файла.
        folder_name: Название папки, куда нужно будет сложить файлы.
    Return:
        Путь до файла в созданной папке.
    """

    folder = Path.cwd() / folder_name
    Path(folder).mkdir(parents=True, exist_ok=True)
    return str(folder / file_name)


def save_random_comics(filepath: str) -> dict:
    """
    Сохраняет рандомный комикс и возвращает словарь с информацией о комиксе.
    Args:
        filepath: путь к комиксу
    Returns:
        {
            'alt': описание комикса,
            'day': str,
            'img': str (ссылка на картинку),
            'link': str,
            'month': str,
            'news': str,
            'num': int (номер комикса),
            'safe_title': str (заголовок),
            'title': str (заголовок),
            'transcript': str,
            'year': 'str
        }
    """

    all_comics = 2732
    random_comic = random.randint(1, all_comics)

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
    Returns:
        Возвращает строку с ссылкой на загруженную на сервер картинку.
    """

    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {
        'access_token': access_token,
        'v': api_version
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_vk_server_response(response.json(), 'Не удалось получить адрес для загрузки комикса.')
    return response.json()['response']['upload_url']


def upload_comic_to_server(access_token: str, api_version: float, filepath: str, upload_url: str) -> dict:
    """
    Загрузка картинки на сервер.
    Args:
        access_token: токен доступа к сообществу в социальной сети "ВКонтакте".
        api_version: версия апи Вконтакте.
        filepath: путь к картинке, где она находится.
        upload_url: ссылка на загруженный комикс на сервере.
    Returns:
        Словарь с данными о загрузке. Ключи - 'server', 'photo', 'hash'.
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
    check_vk_server_response(response.json(), 'Не удалось загрузить комикс на сервер ВК.')
    return response.json()


def save_comic_to_the_group_album(access_token: str, api_version: float, server: str, link: str,
                                  hash: str) -> dict:
    """
    Сохранение картинки в альбоме группы.
    Args:
        access_token: токен доступа к сообществу в социальной сети "ВКонтакте".
        api_version: версия апи Вконтакте.
        server: сервер загрузки картинки.
        link: ссылка на картинку на сервере.
        hash: хэш картинки.
    Returns:
        Возращает словарь с данными о сохранённой картинке. Ключ - 'response'
    """

    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload = {
        'access_token': access_token,
        'v': api_version,
        'server': server,
        'photo': link,
        'hash': hash
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    check_vk_server_response(response.json(), 'Не удалось сохранить комикс в альбоме группы.')
    return response.json()


def post_comic_on_a_group_wall(access_token: str, api_version: float, picture_description: str, owner_id: int,
                               media_id: int) -> None:
    """
    Публикация картинки на стене группы.
    Args:
        access_token: токен доступа к сообществу в социальной сети "ВКонтакте".
        api_version: версия апи Вконтакте.
        picture_description: описание комикса.
        owner_id: идетификационный номер того кто сохранил картинку.
        media_id: идентификационный номер картинки на сервере.
    """

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
    check_vk_server_response(response.json(), 'Не удалось опубликовать комикс на стене сообщества.')


def main():
    """
    Запуск программы.
    """

    load_dotenv()
    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    vk_api_version = 5.131

    comic_filepath = get_file_path_in_created_folder(file_name='comic.png', folder_name='comics')
    try:
        comic = save_random_comics(comic_filepath)
        upload_address = get_comic_upload_address(vk_access_token, vk_api_version)
        upload_comic = upload_comic_to_server(vk_access_token,
                                              vk_api_version,
                                              comic_filepath,
                                              upload_address)
        save_comic = save_comic_to_the_group_album(vk_access_token,
                                                   vk_api_version,
                                                   upload_comic['server'],
                                                   upload_comic['photo'],
                                                   upload_comic['hash'], )
        post_comic_on_a_group_wall(vk_access_token,
                                   vk_api_version,
                                   comic['alt'],
                                   save_comic['response'][0]['owner_id'],
                                   save_comic['response'][0]['id'], )
        print('Комикс опубликован на стене сообщества.')
    except VKErrors as error:
        print(f'Ошибка в ответе от ВКонтакте. {error}')
    except requests.HTTPError:
        print('Не удалось загрузить комикс.')
    finally:
        Path(comic_filepath).unlink()


if __name__ == '__main__':
    main()
