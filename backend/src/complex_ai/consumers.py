import json
from channels.generic.websocket import AsyncWebsocketConsumer


class StockConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        # Example: Send stock + recommendation when client connects
        data = {
            "symbol": "AAPL",
            "price": 185.42,
            "recommend": True  # from LLM later
        }
        await self.send(json.dumps(data))

    async def disconnect(self, close_code):
        print("WebSocket disconnected")
