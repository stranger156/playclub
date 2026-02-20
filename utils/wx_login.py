# WeHappy/utils/wx_login.py
import requests
import jwt
import time
from django.conf import settings

def get_wx_openid(code):
    """
    用小程序的code换取openid和session_key
    :param code: 小程序wx.login获取的临时code
    :return: dict {"openid": "", "session_key": ""} 或 None（失败）
    """
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WX_APP_ID,
        "secret": settings.WX_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        res_data = response.json()
        # 微信返回错误（比如code无效）
        if "errcode" in res_data:
            print(f"微信接口错误：{res_data}")
            return None
        return res_data  # 包含openid和session_key
    except Exception as e:
        print(f"调用微信接口失败：{e}")
        return None

def generate_token(openid):
    """
    用openid生成JWT token（供前端后续请求携带）
    :param openid: 用户唯一标识
    :return: str token字符串
    """
    payload = {
        "openid": openid,
        "exp": int(time.time()) + settings.JWT_EXPIRATION_DELTA  # 过期时间
    }
    # 生成token
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    # 兼容Python3的bytes转字符串
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def verify_token(token):
    """
    验证token有效性，解析出openid
    :param token: 前端携带的token
    :return: str openid（验证成功）/ None（验证失败）
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload.get("openid")
    except jwt.ExpiredSignatureError:
        print("token已过期")
        return None
    except Exception as e:
        print(f"验证token失败：{e}")
        return None