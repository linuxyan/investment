import requests
import os

def get_access_token(appid, secret):
    params = dict(grant_type='client_credential',
                  appid=appid,
                  secret=secret)
    resp = requests.get("https://api.weixin.qq.com/cgi-bin/token",params=params).json()
    if 'errcode' in resp:
        raise ValueError(resp['errmsg'])
    return resp['access_token']

def upload_image_to_wechat(access_token, imgpath):
    resp = requests.post('https://api.weixin.qq.com/cgi-bin/media/uploadimg',
                         params=dict(access_token=access_token),
                         files=dict(media=open(imgpath,'rb'))).json()
    if 'errcode' in resp:
        raise ValueError(resp['errmsg'])
    return resp['url']

def aaa():
    post_url = "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=ACCESS_TOKEN"


def push_context(date_str):
    appid = os.environ.get("WX_APPID")
    secret = os.environ.get("WX_SECRET")
    access_token = get_access_token(appid=appid, secret=secret)
    img_url = upload_image_to_wechat(access_token, f"static/{date_str}.png")
    print(img_url)


if __name__ == "__main__":
    pass
