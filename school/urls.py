# recruits/urls.py
from django.urls import path
from . import views
from .views import get_school

urlpatterns = [
    path('list', get_school, name='get_school'),
    # path('list/', views.RecruitListView.as_view(), name='recruit_list'),       # 招募列表
    # path('join/', views.RecruitJoinView.as_view(), name='recruit_join'),       # 加入招募
]