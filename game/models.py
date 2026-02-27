from django.db import models


# 房间模型
class Room(models.Model):
    room_id = models.CharField(max_length=64, unique=True, verbose_name="房间ID")
    name = models.CharField(max_length=100, verbose_name="房间名称", default='')
    creator = models.CharField(max_length=100, verbose_name="创建者昵称")
    is_started = models.BooleanField(default=False, verbose_name="游戏是否开始")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "房间"
        verbose_name_plural = "房间"

    def __str__(self):
        return f"{self.name}({self.room_id})"


# 房间身份配置模型（前端自定义身份）
class RoomIdentity(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="所属房间", related_name="identities")
    identity_name = models.CharField(max_length=50, verbose_name="身份名称")
    count = models.PositiveIntegerField(default=1, verbose_name="身份数量")

    class Meta:
        verbose_name = "房间身份配置"
        verbose_name_plural = "房间身份配置"
        unique_together = ("room", "identity_name")  # 一个房间的同一种身份只能配置一次

    def __str__(self):
        return f"{self.room.room_id} - {self.identity_name} × {self.count}"


# 玩家模型
class Player(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="所属房间", related_name="players")
    user_name = models.CharField(max_length=100, verbose_name="用户昵称")
    identity_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="分配的身份")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")

    class Meta:
        verbose_name = "玩家"
        verbose_name_plural = "玩家"
        unique_together = ("room", "user_name")  # 一个用户在一个房间只能有一条记录

    def __str__(self):
        return f"{self.username} - {self.identity_name or '未分配'}"