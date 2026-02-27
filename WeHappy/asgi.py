"""
ASGI config for WeHappy project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
# 注释 AuthMiddlewareStack 导入，避免会话依赖 Redis
# from channels.auth import AuthMiddlewareStack
import game.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WeHappy.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(  # 直接用 URLRouter，去掉 AuthMiddlewareStack
        game.routing.websocket_urlpatterns
    ),
})