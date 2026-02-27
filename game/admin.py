from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Room, RoomIdentity, Player

# 注册模型到后台
admin.site.register(Room)
admin.site.register(RoomIdentity)
admin.site.register(Player)