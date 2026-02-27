# game/routing.py
from django.urls import re_path
from .consumers import RoomConsumer  # 显式导入，更清晰

# WebSocket 路由配置
websocket_urlpatterns = [
    # 优化点1：加 ^ 开头，避免匹配到类似 /xxx/ws/room/DF738K/ 的错误路径
    # 优化点2：用 \w+ 明确匹配字母/数字/下划线（和你的 room_id 格式完全匹配）
    # 优化点3：使 / 结尾成为可选，同时支持 ws/room/8X9BWG 和 ws/room/8X9BWG/
    re_path(r'^ws/room/(?P<room_id>\w+)/?$', RoomConsumer.as_asgi()),
]