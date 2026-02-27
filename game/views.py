import random
import string

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from user.models import UserProfile
from utils.wx_login import verify_token
from .models import Room, RoomIdentity, Player
from .serializers import (
    RoomSerializer, PlayerSerializer,
    CreateRoomRequestSerializer, JoinRoomRequestSerializer,
    StartGameRequestSerializer
)
# 生成随机房间ID（6位大写字母+数字）
def generate_room_id(length=6):
    chars = string.ascii_uppercase + string.digits
    while True:
        room_id = ''.join(random.choice(chars) for _ in range(length))
        if not Room.objects.filter(room_id=room_id).exists():
            return room_id

# 生成默认房间名称
def generate_room_name(name):
    return f"{name}的桌游房"

# 房间相关操作
# 房间相关操作（核心改造）
class RoomView(APIView):
    # 创建房间（仅需身份配置）
    @transaction.atomic
    def post(self, request):
        serializer = CreateRoomRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return JsonResponse({"code": 401, "msg": "未登录"})
        name = verify_token(token)

        # 自动生成房间ID和名称
        room_id = generate_room_id()
        room_name = generate_room_name(name)

        # 创建房间（创建者为当前用户）
        room = Room.objects.create(
            room_id=room_id,
            name=room_name,
            creator=name
        )

        # 将创建者添加到玩家列表
        Player.objects.create(
            room=room,
            user_name=name
        )
        # 创建身份配置
        for config in data["configs"]:
            RoomIdentity.objects.create(
                room=room,
                identity_name=config["identity_name"],
                count=config["count"]
            )

        # 返回房间信息
        room_serializer = RoomSerializer(room)
        return Response(room_serializer.data, status=status.HTTP_201_CREATED)

    # 获取房间详情
    def get(self, request):
        room_id = request.query_params.get("room_id")
        if not room_id:
            return Response({"error": "缺少room_id参数"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = Room.objects.get(room_id=room_id)
            serializer = RoomSerializer(room)
            return Response(serializer.data)
        except Room.DoesNotExist:
            return Response({"error": "房间不存在"}, status=status.HTTP_404_NOT_FOUND)


# 玩家相关操作
class PlayerView(APIView):
    # 加入房间
    @transaction.atomic
    def post(self, request):
        serializer = JoinRoomRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return JsonResponse({"code": 401, "msg": "未登录"})
        name = verify_token(token)

        try:
            room = Room.objects.get(room_id=data["room_id"])

            # 检查是否已加入
            if Player.objects.filter(room=room, user_name=name).exists():
                return Response({"error": "已加入该房间"}, status=status.HTTP_400_BAD_REQUEST)

            # 创建玩家
            player = Player.objects.create(
                room=room,
                user_name=name
            )

            # WebSocket推送新玩家加入消息
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'room_{room_id}',
                {
                    'type': 'player_joined',
                    'data': {
                        'success': True,
                        'message': f'玩家 {name} 加入了房间',
                        'player': {
                            'id': player.id,
                            'username': player.user_name,
                            'joined_at': player.joined_at.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    }
                }
            )

            serializer = PlayerSerializer(player)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Room.DoesNotExist:
            return Response({"error": "房间不存在"}, status=status.HTTP_404_NOT_FOUND)

    # 获取房间玩家列表
    def get(self, request):
        room_id = request.query_params.get("room_id")
        if not room_id:
            return Response({"error": "缺少room_id参数"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = Room.objects.get(room_id=room_id)
            players = room.players.all()
            serializer = PlayerSerializer(players, many=True)
            return Response(serializer.data)
        except Room.DoesNotExist:
            return Response({"error": "房间不存在"}, status=status.HTTP_404_NOT_FOUND)


# 开始游戏并发牌
class StartGameView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = StartGameRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        room_id = serializer.validated_data["room_id"]
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return JsonResponse({"code": 401, "msg": "未登录"})
        user = verify_token(token)

        try:
            room = Room.objects.get(room_id=room_id)

            # 检查是否是创建者
            if room.creator != user:
                return Response({"error": "只有房主可以开始游戏"}, status=status.HTTP_403_FORBIDDEN)

            if room.is_started:
                return Response({"error": "游戏已开始"}, status=status.HTTP_400_BAD_REQUEST)

            # 获取房间玩家
            players = room.players.all()
            player_count = players.count()
            if player_count == 0:
                return Response({"error": "房间暂无玩家"}, status=status.HTTP_400_BAD_REQUEST)

            # 获取身份配置并生成身份池
            configs = room.identities.all()
            if not configs:
                return Response({"error": "房间未配置身份"}, status=status.HTTP_400_BAD_REQUEST)

            identity_pool = []
            total_identity_count = 0
            for config in configs:
                for _ in range(config.count):
                    identity_pool.append(config.identity_name)
                    total_identity_count += 1

            # 检查身份数量是否匹配玩家数量
            if total_identity_count != player_count:
                return Response({
                    "error": f"身份总数({total_identity_count})与玩家数({player_count})不匹配"
                }, status=status.HTTP_400_BAD_REQUEST)

            # 洗牌
            random.shuffle(identity_pool)

            # 为玩家分配身份
            players_data = []
            for i, player in enumerate(players):
                player.identity_name = identity_pool[i]
                player.save()
                
                # 获取玩家头像
                avatar = None
                try:
                    user_profile = UserProfile.objects.get(user_name=player.user_name)
                    avatar = user_profile.user_avatar
                except UserProfile.DoesNotExist:
                    pass
                
                players_data.append({
                    'id': player.id,
                    'username': player.user_name,
                    'identity_name': player.identity_name,
                    'avatar': avatar,
                    'joined_at': player.joined_at.strftime('%Y-%m-%d %H:%M:%S'),
                })

            # 标记游戏已开始
            room.is_started = True 
            room.save()

            # WebSocket推送发牌结果
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'room_{room_id}',
                {
                    'type': 'deal_identity_result',
                    'data': {
                        'success': True,
                        'message': '发牌成功',
                        'players': players_data,
                        'room_id': room_id
                    }
                }
            )

            # 返回响应
            return Response({
                "success": True,
                "message": "发牌成功，已通过WebSocket推送结果"
            })
        except Room.DoesNotExist:
            return Response({"error": "房间不存在"}, status=status.HTTP_404_NOT_FOUND)