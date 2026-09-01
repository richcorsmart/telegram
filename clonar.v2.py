#!/usr/bin/env python3
import asyncio
import re
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

API_ID = 6
API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
BOT_TOKEN = "8841200359:AAGrz300mPcuJ559K4ywcYDxPmob8DGkS28"
SOURCE = "@tuhogarfelizgye"
DEST = "@llegolamerca"
INCREMENTO = 30

def aumentar_precios(texto):
    if not texto:
        return texto
    patron = r'\$([0-9,]+(?:\.[0-9]{1,2})?)'
    def reemplazo(match):
        try:
            precio_str = match.group(1).replace(',', '')
            precio = float(precio_str)
            nuevo_precio = precio * (1 + INCREMENTO / 100)
            nuevo_precio = int(nuevo_precio)
            return f'${nuevo_precio}'
        except:
            return match.group(0)
    return re.sub(patron, reemplazo, texto)

async def main():
    print("🔄 Iniciando clonador...")
    print(f"📡 Origen: {SOURCE}")
    print(f"📤 Destino: {DEST}")
    print(f"💰 Aumento: {INCREMENTO}%")
    
    client = TelegramClient('bot', API_ID, API_HASH)
    await client.start(bot_token=BOT_TOKEN)
    
    @client.on(events.NewMessage(chats=SOURCE))
    async def handler(event):
        try:
            texto = event.message.text
            if not texto:
                return
            print(f"\n📩 Mensaje: {texto[:50]}...")
            nuevo = aumentar_precios(texto)
            await client.send_message(DEST, nuevo)
            print(f"✅ Enviado a {DEST}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    me = await client.get_me()
    print(f"✅ Conectado como: @{me.username}")
    print("👂 Esperando mensajes...\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
