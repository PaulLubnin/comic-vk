import requests


def get_comics() -> dict:
    """
    Запрос на получение json с данными о комиксе.
    """

    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    print(get_comics())
