import os
from pprint import pprint

import requests
from dotenv import load_dotenv

load_dotenv()


def get_comics() -> dict:
    """
    Запрос на получение json с данными о комиксе.
    """

    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_groups():
    """
    Запрос на получение групп.
    """

    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    url = 'https://api.vk.com/method/groups.get'
    payload = {
        'access_token': vk_access_token,
        'v': 5.131
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    # print(get_comics()['alt'])
    pprint(get_groups())
