from django.shortcuts import render

# Create your views here.
import json
import time
import random
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from order.models import RecruitOrder, RecruitUser
from school.models import SchoolList
from user.models import UserProfile
from utils.wx_login import verify_token


def get_school(request):
    if request.method != "GET":
        return JsonResponse({"code": 405, "msg": "仅支持GET请求"})
    schools = SchoolList.objects.all()
    school_list = []
    for school in schools:
        school_list.append(
           school.school_name
        )
    return JsonResponse({"code": 200,
                         "msg": "查询成功",
                        "data": school_list })

