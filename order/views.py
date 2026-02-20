import json
import time
import random
from datetime import date
from operator import itemgetter

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from order.models import RecruitOrder, RecruitUser
from user.models import UserProfile
from utils.wx_login import verify_token


def generate_order_id():
    # 格式：时间戳（13位） + 随机数（4位），确保唯一性
    timestamp = str(int(time.time() * 1000))  # 毫秒级时间戳，避免秒级重复
    random_num = str(random.randint(1000, 9999))
    return f"ORDER{timestamp}{random_num}"

@csrf_exempt
def create_order(request):
    if request.method != 'POST':
        return JsonResponse({"code": 405, "msg": "仅支持POST请求"}, status=405)

    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"code": 401, "msg": "未登录"})
    name = verify_token(token)
    try:
        user_profile = UserProfile.objects.get(user_name=name)
        req_data = json.loads(request.body)
        order_id=generate_order_id()
        RecruitOrder.objects.get_or_create(
            order_id=order_id,
            user_name=user_profile.user_name,
            order_introduction=req_data.get("introduction"),
            max_num=req_data.get("max_num"),
            current_num=1,
            order_time=req_data.get("order_time"),
            status=0,
        )
        RecruitUser.objects.get_or_create(
            order_id=order_id,
            user_name=name,
            is_owner=True
        )
    except UserProfile.DoesNotExist:
        return JsonResponse({"code": 404, "msg": "用户档案不存在"})

    return JsonResponse({"code": 200})

def get_order(request):
    if request.method != "GET":
        return JsonResponse({"code": 405, "msg": "仅支持GET请求"})
    recruit_orders = RecruitOrder.objects.filter(status=0 , order_time__gte=date.today() ).order_by("order_time")
    order_list = []
    for order in recruit_orders:
        user_profile = UserProfile.objects.get(user_name=order.user_name)
        avatar_url = user_profile.user_avatar
        order_list.append({
            "order_id": order.order_id,
            "name": order.user_name,
            "content": order.order_introduction,
            "max_num": order.max_num,
            "current_num": order.current_num,
            "date": order.order_date,
            "time": order.order_time,
            "avatar": avatar_url
        })
    return JsonResponse({"code": 200,
                         "msg": "查询成功",
                        "data": order_list })

def get_user_order(request):
    if request.method != "GET":
        return JsonResponse({"code": 405, "msg": "仅支持GET请求"})
    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"code": 401, "msg": "未登录"})
    name = verify_token(token)
    recruit_orders = RecruitOrder.objects.filter(user_name=name, order_time__gte=date.today()).order_by("order_date")
    add_orders=RecruitUser.objects.filter(user_name=name,is_owner=0)
    order_list = []
    for order in recruit_orders:
        order_list.append({
            "order_id": order.order_id,
            "content": order.order_introduction,
            "max_num": order.max_num,
            "current_num": order.current_num,
            "date": order.order_date,
            "time": order.order_time,
            "status": order.status,
        })
    for add_order in add_orders:
        add=RecruitOrder.objects.get(order_id=add_order.order_id)
        if add.order_time>=date.today():
            order_list.append({
            "order_id": add.order_id,
            "content": add.order_introduction,
            "max_num": add.max_num,
            "current_num": add.current_num,
            "date": add.order_date,
            "time": add.order_time,
            "status": add.status,
        })
    order_list.sort(key=itemgetter('time'))
    return JsonResponse({"code": 200,
                         "msg": "查询成功",
                         "data": order_list})


def get_history_order(request):
    if request.method != "GET":
        return JsonResponse({"code": 405, "msg": "仅支持GET请求"})
    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"code": 401, "msg": "未登录"})
    name = verify_token(token)
    recruit_orders =RecruitUser.objects.filter(user_name=name)
    order_list = []
    for recruit_order  in recruit_orders:
        order=RecruitOrder.objects.get(order_id=recruit_order.order_id)
        if order.order_time<date.today() or recruit_order.status==1:
            order_list.append({
            "order_id": order.order_id,
            "content": order.order_introduction,
            "date": order.order_date,
            "time": order.order_time,
            "status": '已取消' if recruit_order.status==1 else '已结束',
        })

    order_list.sort(key=itemgetter('time'))
    return JsonResponse({"code": 200,
                         "msg": "查询成功",
                         "data": order_list})



def get_order_detail(request):
    if request.method != "GET":
        return JsonResponse({"code": 405, "msg": "仅支持GET请求"})

    order=request.GET.get("id")
    recruit_order= RecruitOrder.objects.get(order_id=order)
    name=recruit_order.user_name
    user_profile = UserProfile.objects.get(user_name=name)
    users=RecruitUser.objects.filter(order_id=order).order_by("id")
    user_list=[]
    for user in users:
        user_avatar=UserProfile.objects.get(user_name=user.user_name).user_avatar
        user_list.append({
            "user_name": user.user_name,
            "avatar": user_avatar,
            "is_owner": user.is_owner
        })
    return JsonResponse({"code": 200,
                         'data': {
                             'name':recruit_order.user_name,
                             'content':recruit_order.order_introduction,
                             'avatar':user_profile.user_avatar,
                             'time':recruit_order.order_time,
                             'date':recruit_order.order_date,
                             'userList':user_list,
                             'current_num':recruit_order.current_num,
                             'max_num':recruit_order.max_num,
                         }})


@csrf_exempt
def add_order_user(request):
    if request.method != 'POST':
        return JsonResponse({"code": 405, "msg": "仅支持POST请求"}, status=405)
    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return JsonResponse({"code": 401, "msg": "未登录"})
    name = verify_token(token)
    req_body = json.loads(request.body)
    order_id = req_body.get("id")
    if RecruitUser.objects.filter(order_id=order_id,user_name=name).exists():
        return JsonResponse({"code":403,"msg":"不可重复加入"})
    order = RecruitOrder.objects.get(order_id=order_id)
    if order.current_num==order.max_num:
        return JsonResponse({"code":402,"msg":"招募人数已满"})
    order.current_num = order.current_num + 1
    order.save()
    if order.current_num == order.max_num:
        order.status = 1
        order.save()
    RecruitUser.objects.create(
                order_id=order_id,
                user_name=name,
                is_owner=False
            )

    return JsonResponse({"code": 200})





# def get_last_order(request):
#     if request.method != "GET":
#         return JsonResponse({"code": 405, "msg": "仅支持GET请求"})
#     token = request.META.get("HTTP_AUTHORIZATION")
#     if not token:
#         return JsonResponse({"code": 401, "msg": "未登录"})
#     name = verify_token(token)
#     recruit_orders = RecruitOrder.objects.filter(user_name=name)
#     order_list = []
#     for order in recruit_orders:
#         order_list.append({
#             "order_id": order.order_id,
#             "content": order.order_introduction,
#             "max_num": order.max_num,
#             "current_num": order.current_num,
#             "date": order.order_date,
#             "time": order.order_time,
#             "status": order.status,
#         })
#     return JsonResponse({"code": 200,
#                          "msg": "查询成功",
#                          "data": order_list})