#!/usr/bin/env python3
import asyncio
import re
import os
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# ========== CONFIGURACIÓN ==========
API_ID = 33896444
API_HASH = "7e50bce51809a336fe0ca35cf2638fb"
BOT_TOKEN = "8521854091:AAEa2Yyc3mNmz4rNYWmiuDJsylwg8BpLBsI"
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

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(chats=SOURCE))
async def handler(event):
    try:
        mensaje = event.message
        texto = mensaje.text
        if not texto:
            return
        print(f"\n📩 Nuevo mensaje recibido: {texto[:100]}...")
        nuevo_texto = aumentar_precios(texto)
        if nuevo_texto != texto:
            print(f"💰 Precios aumentados: {INCREMENTO}%")
            await client.send_message(DEST, nuevo_texto)
            print(f"✅ Mensaje enviado a {DEST}")
        else:
            print(f"ℹ️ Sin precios, mensaje reenviado")
            await client.send_message(DEST, texto)
            print(f"✅ Mensaje reenviado a {DEST}")
    except FloodWaitError as e:
        print(f"⏳ Esperar {e.seconds} segundos")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    print("🔄 Iniciando clonador en tiempo real...")
    print(f"📡 Escuchando: {SOURCE}")
    print(f"📤 Publicando en: {DEST}")
    print(f"💰 Aumento: {INCREMENTO}% solo para precios con $ (redondeo arriba)")
    print("🔐 Iniciando sesión con Bot Token...")
    await client.start()
    me = await client.get_me()
    print(f"✅ Conectado como: @{me.username} (Bot)")
    print("👂 Esperando mensajes...\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
