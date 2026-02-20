# recruits/urls.py
from django.urls import path
from . import views
from .views import create_order, get_order, get_user_order, get_order_detail, add_order_user, get_history_order

urlpatterns = [
     path('create', create_order, name='recruit_create'), # 发布招募
     path("getOrder",get_order,name='recruit_getOrder'),
     path("getUserOrder",get_user_order,name='recruit_getUserOrder'),
     path("getOrderDetail",get_order_detail,name='recruit_getOrderDetail'),
     path("addOrderUser",add_order_user,name='recruit_addOrderUser'),
     path("getHistoryOrder",get_history_order,name='recruit_getHistoryOrder'),
    # path('list/', views.RecruitListView.as_view(), name='recruit_list'),       # 招募列表
    # path('join/', views.RecruitJoinView.as_view(), name='recruit_join'),       # 加入招募
]