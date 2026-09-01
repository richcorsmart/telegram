#!/usr/bin/env python3
import asyncio
import re
import os
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# Configuración desde variables de entorno
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN no configurado")
    exit(1)

API_ID = 6
API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"
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
    print("🔄 Iniciando clonador en tiempo real...")
    print(f"📡 Escuchando: {SOURCE}")
    print(f"📤 Publicando en: {DEST}")
    print(f"💰 Aumento: {INCREMENTO}% solo para precios con $ (redondeo arriba)")
    print("🔐 Iniciando sesión con Bot Token...")
    
    client = TelegramClient('bot', API_ID, API_HASH)
    
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
            print(f"⏳ FloodWait: Esperar {e.seconds} segundos")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    try:
        await client.start(bot_token=BOT_TOKEN)
        me = await client.get_me()
        print(f"✅ Conectado como: @{me.username} (Bot)")
        print("👂 Esperando mensajes...\n")
        await client.run_until_disconnected()
    except FloodWaitError as e:
        print(f"⏳ Telegram pide esperar {e.seconds} segundos")
        print("🔄 Esperando antes de reintentar...")
        await asyncio.sleep(e.seconds)
        print("✅ Espera completada, reintentando...")
        await main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
