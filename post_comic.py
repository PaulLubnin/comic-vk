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


def save_random_comics(filepath: str) -> str:
    """
    Сохраняет рандомный комикс и возвращает описание комиксе.
    Args:
        filepath: путь к комиксу
    Returns:
        Описание комикса.
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
    return response.json()['alt']


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


def upload_comic_to_server(access_token: str, api_version: float, filepath: str, upload_url: str) -> tuple:
    """
    Загрузка картинки на сервер.
    Args:
        access_token: токен доступа к сообществу в социальной сети "ВКонтакте".
        api_version: версия апи Вконтакте.
        filepath: путь к картинке, где она находится.
        upload_url: ссылка на загруженный комикс на сервере.
    Returns:
        Кортеж с данными о загрузке - (server, photo, hash)
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
    return response.json()['server'], response.json()['photo'], response.json()['hash']


def save_comic_to_the_group_album(access_token: str, api_version: float, server: str, link: str,
                                  comic_hash: str) -> tuple:
    """
    Сохранение картинки в альбоме группы.
    Args:
        access_token: токен доступа к сообществу в социальной сети "ВКонтакте".
        api_version: версия апи Вконтакте.
        server: сервер загрузки картинки.
        link: ссылка на картинку на сервере.
        comic_hash: хэш картинки.
    Returns:
        Возращает кортеж с данными о сохранённой картинке - (owner_id, media_id)
    """

    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload = {
        'access_token': access_token,
        'v': api_version,
        'server': server,
        'photo': link,
        'hash': comic_hash
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    check_vk_server_response(response.json(), 'Не удалось сохранить комикс в альбоме группы.')
    return response.json()['response'][0]['owner_id'], response.json()['response'][0]['id']


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

    group_id = os.getenv('GROUP_ID')
    url = 'https://api.vk.com/method/wall.post'
    payload = {
        'access_token': access_token,
        'v': api_version,
        'owner_id': -int(group_id),
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
        description_comic = save_random_comics(comic_filepath)
        upload_address = get_comic_upload_address(vk_access_token, vk_api_version)
        uploaded_comic = upload_comic_to_server(vk_access_token,
                                                vk_api_version,
                                                comic_filepath,
                                                upload_address)
        server, photo, comic_hash = uploaded_comic
        saved_comic = save_comic_to_the_group_album(vk_access_token,
                                                    vk_api_version,
                                                    server,
                                                    photo,
                                                    comic_hash)
        owner_id, media_id = saved_comic
        post_comic_on_a_group_wall(vk_access_token,
                                   vk_api_version,
                                   description_comic,
                                   owner_id,
                                   media_id)
        print('Комикс опубликован на стене сообщества.')
    except VKErrors as error:
        print(f'Ошибка в ответе от ВКонтакте. {error}')
    except requests.HTTPError:
        print('Не удалось загрузить комикс.')
    finally:
        Path(comic_filepath).unlink()


if __name__ == '__main__':
    main()
