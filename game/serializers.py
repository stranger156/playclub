from rest_framework import serializers
from django.contrib.auth import get_user_model

from user.models import UserProfile
from .models import Room, RoomIdentity, Player

User = get_user_model()


# 房间身份配置序列化器
class RoomIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomIdentity
        fields = ["id", "identity_name", "count"]


# 房间序列化器
class RoomSerializer(serializers.ModelSerializer):
    identities = RoomIdentitySerializer(many=True, read_only=True)
    player_count = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["id", "room_id", "name","creator","is_started", "created_at", "identities", "player_count"]

    def get_player_count(self, obj):
        return obj.players.count()



# 玩家序列化器
class PlayerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = ["id", "username", "identity_name", "joined_at", "avatar"]

    def get_username(self, obj):
        return obj.user_name

    def get_avatar(self, obj):
        try:
            user_profile = UserProfile.objects.get(user_name=obj.user_name)
            return user_profile.user_avatar
        except UserProfile.DoesNotExist:
            return None



# 创建房间请求序列化器（仅需身份配置）
class IdentityConfigRequestSerializer(serializers.Serializer):
    identity_name = serializers.CharField(max_length=50)
    count = serializers.IntegerField(min_value=1)


class CreateRoomRequestSerializer(serializers.Serializer):
    # 仅接收身份配置，无room_id/name/creator
    configs = IdentityConfigRequestSerializer(many=True)

# 加入房间请求序列化器（改为通过用户ID关联）
class JoinRoomRequestSerializer(serializers.Serializer):
    room_id = serializers.CharField(max_length=64)


# 开始游戏请求序列化器
class StartGameRequestSerializer(serializers.Serializer):
    room_id = serializers.CharField(max_length=64)


# 用户注册/登录序列化器
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "nickname", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            nickname=validated_data.get("nickname"),
            password=validated_data["password"]
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()