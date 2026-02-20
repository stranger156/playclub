from django.urls import path
from .views import (WxLoginView, get_code, UserInfoView, change_username, change_birthday, change_gender, change_wx,
                    change_phone, change_school, upload_avatar, get_avatar, get_other_info, change_introduction)

urlpatterns = [
    path("login", WxLoginView.as_view(), name="login"),  # 登录接口
    path("info", UserInfoView.as_view(), name="user_info"),   # 获取用户信息接口
    path("changeUsername",change_username, name="change_username"),
    path("changeBirthday",change_birthday,name="change_birthday"),
    path("changeGender",change_gender,name="change_gender"),
    path("changeWx",change_wx,name="change_wx"),
    path("changeIntroduction",change_introduction,name="change_introduction"),
    path("changePhone",change_phone,name="change_phone"),
    path("changeSchool",change_school,name="change_school"),
    path("getCode",get_code,name="get_code"),
    path("avatar/upload",upload_avatar,name="upload_avatar"),
    path("avatar/get",get_avatar,name="get_avatar"),
    path("getOtherInfo",get_other_info,name="get_other_info"),
]