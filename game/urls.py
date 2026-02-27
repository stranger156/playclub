from django.urls import path
from . import views
from django.urls import path
from game.views import RoomView, PlayerView, StartGameView
urlpatterns = [
    # 房间接口
    path('room', RoomView.as_view()),
    # 玩家接口
    path('player', PlayerView.as_view()),
    # 开始游戏发牌接口
    path('start-game', StartGameView.as_view()),
]