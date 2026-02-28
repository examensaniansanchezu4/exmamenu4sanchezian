import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Libro


class NotificacionesConsumer(AsyncWebsocketConsumer):
    """Consumer para notificaciones en tiempo real"""
    
    async def connect(self):
        """Cuando un cliente se conecta"""
        self.room_group_name = 'notificaciones'
        
        # Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Mensaje de bienvenida
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': '✅ Conectado a notificaciones en tiempo real'
        }))
    
    async def disconnect(self, close_code):
        """Cuando un cliente se desconecta"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Recibir mensaje del cliente"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'libro_update':
            libro_id = data.get('libro_id')
            await self.notificar_cambio_libro(libro_id)
    
    async def notificar_cambio_libro(self, libro_id):
        """Notificar a todos sobre cambio en libro"""
        libro_data = await self.get_libro_data(libro_id)
        
        # Broadcast a todo el grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'libro_actualizado',
                'libro': libro_data
            }
        )
    
    async def libro_actualizado(self, event):
        """Enviar notificación al cliente"""
        await self.send(text_data=json.dumps({
            'type': 'libro_actualizado',
            'libro': event['libro']
        }))
    
    @database_sync_to_async
    def get_libro_data(self, libro_id):
        """Obtener datos del libro (sync to async)"""
        try:
            libro = Libro.objects.get(pk=libro_id)
            return {
                'id': libro.id,
                'titulo': libro.titulo,
                'stock': libro.stock,
                'disponible': libro.esta_disponible
            }
        except Libro.DoesNotExist:
            return None


class ChatConsumer(AsyncWebsocketConsumer):
    """Consumer para chat de biblioteca"""
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notificar que alguien se conectó
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'message': f'Un usuario se unió al chat'
            }
        )
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data.get('username', 'Anónimo')
        
        # Enviar mensaje a todos en la sala
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )
    
    async def chat_message(self, event):
        """Recibir mensaje del grupo y enviarlo al WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username']
        }))
    
    async def user_join(self, event):
        """Usuario se unió"""
        await self.send(text_data=json.dumps({
            'type': 'system',
            'message': event['message']
        }))