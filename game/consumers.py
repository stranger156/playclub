import json
from channels.generic.websocket import AsyncWebsocketConsumer


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 获取房间ID
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'

        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 接受连接
        await self.accept()

        # 发送连接成功消息
        await self.send(text_data=json.dumps({
            'type': 'connection_success',
            'message': f'已成功连接到房间 {self.room_id}'
        }))

    async def disconnect(self, close_code):
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 接收前端消息
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'ping':
            # 心跳响应
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'message': '连接正常'
            }))

    # 处理发牌结果推送
    async def deal_identity_result(self, event):
        # 发送消息到WebSocket
        await self.send(text_data=json.dumps({
            'type': 'deal_identity',
            'data': event['data']
        }))

    # 处理新玩家加入推送
    async def player_joined(self, event):
        # 发送消息到WebSocket
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'data': event['data']
        }))

    # 处理玩家离开推送
    async def player_left(self, event):
        # 发送消息到WebSocket
        await self.send(text_data=json.dumps({
            'type': 'player_left',
            'data': event['data']
        }))