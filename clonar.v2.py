import asyncio
import re
import os
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# ============ CONFIGURACIÓN ============
API_ID = 33896444
API_HASH = "7e50bce51809a336fe0ca35fc2638fbe"
SOURCE = "@tuhogarfelizgye"
DEST = "@llegolamerca"
INCREMENTO = 30
# =======================================

def aumentar_precios(texto):
    """
    Aumenta en un 30% y redondea hacia arriba SOLO los números que tengan
    el símbolo $ (ej: $12, $12.50). No modifica números sin $.
    """
    if not texto:
        return texto

    def reemplazo(match):
        # match.group(0) contiene todo: el símbolo $ y el número
        # match.group(1) contiene solo el número con posibles decimales
        numero_completo = match.group(0)
        num_str = match.group(1).replace(',', '.')
        try:
            valor = float(num_str)
        except ValueError:
            return match.group(0)

        nuevo = valor * (1 + INCREMENTO / 100)
        nuevo_redondeado = int(nuevo) if nuevo == int(nuevo) else int(nuevo) + 1

        # Devolver con el símbolo $ (el match original ya lo tiene)
        return f"${nuevo_redondeado}"

    # Patrón: busca un $ (opcionalmente con espacio) seguido de un número
    # Captura el número en el grupo 1 para modificarlo
    patron = r'\$\s*(\d{1,3}(?:[.,]\d{1,2})?)'
    nuevo_texto = re.sub(patron, reemplazo, texto)
    return nuevo_texto

async def main():
    print("🔄 Iniciando clonador en tiempo real...")
    print(f"📡 Escuchando: {SOURCE}")
    print(f"📤 Publicando en: {DEST}")
    print(f"💰 Aumento: {INCREMENTO}% solo para precios con $ (redondeo arriba)\n")
    print("🔐 Iniciando sesión...")

    client = TelegramClient("sesion_usuario", API_ID, API_HASH)

    @client.on(events.NewMessage(chats=SOURCE))
    async def handler(event):
        mensaje = event.message
        if not mensaje:
            return

        # Obtener texto (para mensajes con o sin media, .text funciona para ambos)
        texto_original = mensaje.text or ""
        print(f"\n📩 Nuevo mensaje ID: {mensaje.id}")
        print(f"   Texto original: '{texto_original}'")

        # Modificar precios (solo los que tengan $)
        texto_modificado = aumentar_precios(texto_original)

        if texto_modificado != texto_original:
            print(f"   ➡️ Texto modificado: '{texto_modificado}'")
        else:
            print("   ℹ️ No se detectaron precios con $ para modificar.")

        try:
            # Si hay multimedia (foto, video, documento)
            if mensaje.media:
                # Descargar el archivo temporal
                ruta = await client.download_media(mensaje, file="temp_media")
                if ruta:
                    # Enviar el archivo con el caption modificado
                    await client.send_file(
                        DEST,
                        ruta,
                        caption=texto_modificado if texto_modificado else None
                    )
                    # Eliminar archivo temporal
                    try:
                        os.remove(ruta)
                    except:
                        pass
                    print("   ✅ Multimedia copiada con nuevo caption.")
                else:
                    # Fallback: enviar solo texto
                    await client.send_message(DEST, texto_modificado or " ")
                    print("   ⚠️ No se pudo descargar la media, se envió solo texto.")
            else:
                # Solo texto
                await client.send_message(DEST, texto_modificado or " ")
                print("   ✅ Mensaje de texto copiado.")

        except FloodWaitError as e:
            print(f"⏳ Esperando {e.seconds}s por límite de velocidad...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"❌ Error al copiar mensaje: {e}")

    try:
        await client.start()
        print("✅ Sesión iniciada. Esperando mensajes...\n")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Error en el cliente: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Bot detenido por el usuario.")
    except Exception as e:
        print(f"💥 Error fatal: {e}")
    finally:
        input("\n🔴 Presiona ENTER para cerrar...")