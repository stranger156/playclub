import json
from django.shortcuts import render
from django.views import View
# 关键新增：导入关闭CSRF防护的装饰器
from django.utils.decorators import method_decorator
# user/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
# Create your views here.
# WeHappy/users/views.py
from utils.wx_login import  generate_token
from .models import UserLoginInfo, UserProfile
from utils.wx_login import verify_token

# 关键修改：给类视图添加 @method_decorator 装饰器，关闭CSRF防护
@method_decorator(csrf_exempt, name='dispatch')
class WxLoginView(View):
    """微信小程序匿名登录接口"""
    # 登录
    def get(self, request):
        # 1. 获取前端传的code
        name=request.GET.get("name")
        if not name:
            return JsonResponse({"code": 400, "msg": "缺少用户名参数"})

        try:
            user_login = UserLoginInfo.objects.get(user_name=name)
            password = request.GET.get("password")
            if password != user_login.user_password:
                return JsonResponse({
            "code": 401,
            "msg": "用户名/密码输入错误"
        })
        except UserProfile.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"})

        # 4. 生成token返回给前端
        token = generate_token(name)

        # 5. 返回结果（匿名登录无需返回用户信息，仅返回token）
        return JsonResponse({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "token": token
            }
        })

    # 注册
    def post(self, request):
        req_data = json.loads(request.body)
        name = req_data.get("name")
        password = req_data.get("password")
        if not name:
            return JsonResponse({"code": 400, "msg": "缺少用户名参数"})

        user_query = UserLoginInfo.objects.filter(user_name=name)
        if not user_query.exists():
            UserLoginInfo.objects.create(user_name=name, user_password=password)
            UserProfile.objects.create(user_name=name)
        else:
            return JsonResponse({"code": 401, "msg": "用户名已存在"})

        return JsonResponse({"code": 200,"msg":"注册成功"})



# 可选：如果UserInfoView也需要关闭CSRF（GET请求默认不校验，POST/PUT才需要）
# @method_decorator(csrf_exempt, name='dispatch')
class UserInfoView(View):
    """获取用户信息（需要验证token）"""

    def get(self, request):
        # 从请求头获取token

        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return JsonResponse({"code": 401, "msg": "未登录"})
        name=verify_token(token)
        # 查询用户信息（匿名登录只返回基础信息）
        try:
            user_profile = UserProfile.objects.get(user_name=name)
            return JsonResponse({
                "code": 200,
                "data": {
                    "username": user_profile.user_name,
                    "sex":user_profile.user_sex,
                    "birthday": user_profile.user_birthday,
                    "avatar": user_profile.user_avatar,
                    "introduction": user_profile.user_introduction,
                    "school": user_profile.user_school,
                    "wx":user_profile.user_wx_num,
                    "phone":user_profile.user_phone_num,
                }
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"})

   # 得到他人用户信息
def get_other_info(request):
    name=request.GET.get("name")
    try:
        user_profile = UserProfile.objects.get(user_name=name)
        return JsonResponse({
            "code": 200,
            "data": {
                "user_name": user_profile.user_name,
                "sex":user_profile.user_sex,
                "avatar": user_profile.user_avatar,
                "introduction": user_profile.user_introduction,
                "school": user_profile.user_school,
                }
            })
    except UserProfile.DoesNotExist:
            return JsonResponse({"code": 404, "msg": "用户不存在"})


@csrf_exempt
def change_username(request):
    if request.method != 'POST':
        return JsonResponse({"code": 405, "msg": "仅支持POST请求"}, status=405)

    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"code": 401, "msg": "未登录"})
    name = verify_token(token)

    try:
        user_profile = UserProfile.objects.get(user_name=name)
        req_data = json.loads(request.body)
        nickname = req_data.get("nickname")
        user_profile.user_name = nickname
        user_profile.save()
    except UserProfile.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户档案不存在"})

    return JsonResponse({"code": 200})


@csrf_exempt
def change_birthday(request):
    if request.method != 'POST':
        return JsonResponse({"code": 405, "msg": "仅支持POST请求"}, status=405)

    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"code": 401, "msg": "未登录"})
    name = verify_token(token)

    try:
        user_profile = UserProfile.objects.get(user_name=name)
        req_data = json.loads(request.body)
        birthday = req_data.get("birthday")
        user_profile.user_birthday = birthday
        user_profile.save()
    except UserProfile.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户档案不存在"})

    return JsonResponse({"code": 200})

@csrf_exempt
def change_gender(request):
    if request.method != 'POST':
        return JsonResponse({"code": 405, "msg": "仅支持POST请求"}, status=405)

    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"code": 401, "msg": "未登录"})
    name = verify_token(token)

    try:
        user_profile = UserProfile.objects.get(user_name=name)
        req_data = json.loads(request.body)
        gender = req_data.get("gender")
        user_profile.user_sex = gender
        user_profile.save()
    except UserProfile.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户档案不存在"})

    return JsonResponse({"code": 200})


@csrf_exempt
def change_wx(request):
    if request.method != 'POST':
        return JsonResponse({"code": 405, "msg": "仅支持POST请求"}, status=405)
    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"code": 401, "msg": "未登录"})
    name = verify_token(token)
    try:
        user_profile = UserProfile.objects.get(user_name=name)
        req_data = json.loads(request.body)
        wx = req_data.get("wx")
        user_profile.user_wx_num = wx
        user_profile.save()
    except UserProfile.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户档案不存在"})

    return JsonResponse({"code": 200})

@csrf_exempt
def change_introduction(request):
    if request.method != 'POST':
        return JsonResponse({"code": 405, "msg": "仅支持POST请求"}, status=405)
    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"code": 401, "msg": "未登录"})
    name = verify_token(token)
    try:
        user_profile = UserProfile.objects.get(user_name=name)
        req_data = json.loads(request.body)
        introduction = req_data.get("introduction")
        user_profile.user_introduction= introduction
        user_profile.save()
    except UserProfile.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户档案不存在"})

    return JsonResponse({"code": 200})

@csrf_exempt
def change_school(request):
    if request.method != 'POST':
        return JsonResponse({"code": 405, "msg": "仅支持POST请求"}, status=405)
    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"code": 401, "msg": "未登录"})
    name = verify_token(token)
    try:
        user_profile = UserProfile.objects.get(user_name=name)
        req_data = json.loads(request.body)
        school = req_data.get("school")
        user_profile.user_school = school
        user_profile.save()
    except UserProfile.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户档案不存在"})

    return JsonResponse({"code": 200})


@csrf_exempt
def change_phone(request):
    if request.method != 'POST':
        return JsonResponse({"code": 405, "msg": "仅支持POST请求"}, status=405)
    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"code": 401, "msg": "未登录"})
    name = verify_token(token)
    try:
        user_profile = UserProfile.objects.get(user_name=name)
        req_data = json.loads(request.body)
        phone = req_data.get("phone")
        user_profile.user_phone_num = phone
        user_profile.save()
    except UserProfile.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户档案不存在"})

    return JsonResponse({"code": 200})

def get_code(request):
    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"code": 401, "msg": "未登录"})

    name=verify_token(token)
    try:
        user_profile = UserLoginInfo.objects.get(user_name=name)
        print(request.user)
        user_time_date = user_profile.user_time.strftime("%Y-%m-%d") if user_profile.user_time else ""
        return JsonResponse({
            "code": 200,
            "data": {
                "time": user_time_date,
                "name": user_profile.user_name,
                "star":user_profile.user_star,
            }
        })
    except UserLoginInfo.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户档案不存在"})



@csrf_exempt
def upload_avatar(request):
    if request.method != 'POST':
        return JsonResponse({'code': 400, 'msg': '仅支持POST请求'})

    # 获取上传的头像文件
    file = request.FILES.get('avatar')
    if not file:
        return JsonResponse({'code': 400, 'msg': '请选择要上传的头像'})

    # 限制文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
    if file.content_type not in allowed_types:
        return JsonResponse({'code': 400, 'msg': '仅支持jpg/png格式的图片'})

    token = request.META.get("HTTP_AUTHORIZATION")
    name=verify_token(token)
    try:
        # 获取当前登录用户的Profile（假设 user_name 与登录用户名一致，需根据你的逻辑调整）
        # 注意：需替换为你实际的用户关联逻辑（比如通过user_id/手机号关联）
        user_profile = UserProfile.objects.get(user_name=name)

        # 保存头像文件（会自动调用 save() 方法同步 user_avatar 字段）
        user_profile.avatar = file
        user_profile.save()

        # 返回头像URL（兼容原有接口返回格式）
        return JsonResponse({
            'code': 200,
            'msg': '头像上传成功',
            'data': {'avatar_url': user_profile.user_avatar}  # 用原有字段返回
        })
    except Exception as e:
        return JsonResponse({'code': 500, 'msg': f'上传失败：{str(e)}'})

def get_avatar(request):
    token = request.META.get("HTTP_AUTHORIZATION")
    name = verify_token(token)
    try:
        user_profile = UserProfile.objects.get(user_name=name)
        return JsonResponse({
            'code': 200,
            'data': {'avatar_url': user_profile.user_avatar}
        })
    except UserProfile.DoesNotExist:
        # 返回默认头像URL
        default_avatar = request.build_absolute_uri(settings.MEDIA_URL + 'avatars/default.jpg')
        return JsonResponse({
            'code': 200,
            'data': {'avatar_url': default_avatar}
        })
    except Exception as e:
        return JsonResponse({'code': 500, 'msg': f'获取失败：{str(e)}'})