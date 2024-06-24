import requests
import os
import json

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


def upload_thumb_to_wechat(access_token, imgpath):
    resp = requests.post('https://api.weixin.qq.com/cgi-bin/material/add_material',
                         params=dict(access_token=access_token,type='thumb'),
                         files=dict(media=open(imgpath,'rb'))).json()
    if 'errcode' in resp:
        raise ValueError(resp['errmsg'])
    return resp['media_id']


def upload_content_to_wechat(access_token, curr_date_str, html_context):
    content = {"articles": [
                {
                    "title":f"{curr_date_str}股票估值",
                    "author":"Robot",
                    "digest":f"{curr_date_str}股票估值",
                    "content":html_context,
                    "content_source_url":"https://linuxyan.github.io/investment",
                    "thumb_media_id":"hDIqbxBik3JzEsBmnzS0FUz7toCVFHil7wFJktrpg-zFiVy1RjnH5GAd6knNm7fB",
                    "need_open_comment":1,
                    "only_fans_can_comment":0,
                }
            ]}
    resp = requests.post('https://api.weixin.qq.com/cgi-bin/draft/add',
                         params=dict(access_token=access_token),
                         data=json.dumps(content, ensure_ascii=False).encode('utf-8')).json()
    if 'errcode' in resp:
        raise ValueError(resp)
    return resp['media_id']


def push_content(date_str):
    appid = os.environ.get("WX_APPID")
    secret = os.environ.get("WX_SECRET")
    access_token = get_access_token(appid=appid, secret=secret)
    img_url = upload_image_to_wechat(access_token, f"static/{date_str}.png")
    with open('docs/wechat_template.html') as f: content = f.read()
    content = content.replace('image_link',img_url).replace('image_date',date_str)
    # thumb_media_id = upload_thumb_to_wechat(access_token=access_token,imgpath='docs/WX_thumb.png')
    # print(f"thumb_media_id:{thumb_media_id}")
    content_media_id = upload_content_to_wechat(access_token=access_token, curr_date_str=date_str,html_context=content)
    print(content_media_id)

if __name__ == "__main__":
    pass
