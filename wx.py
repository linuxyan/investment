import requests
import os


def get_access_token(appid, secret):
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(appid, secret)
    response = requests.get(url)
    data = response.json()
    return data


if __name__ == "__main__":
    appid = os.environ.get("WX_APPID")
    secret = os.environ.get("WX_SECRET")
    print(appid, secret)
    print(get_access_token(appid=appid, secret=secret))
