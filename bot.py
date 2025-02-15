import os
import requests
from flask import Flask, request, jsonify
import discord
from discord.ext import commands
import asyncio

# Configuración
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_BEARER_TOKEN = os.getenv("TWITCH_BEARER_TOKEN")  # Obtener manualmente
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))  # ID del servidor de Discord
DISCORD_VOICE_CHANNEL_ID = int(os.getenv("DISCORD_VOICE_CHANNEL_ID"))  # Canal de voz

# Inicializar Flask
app = Flask(__name__)

# Inicializar Bot de Discord
intents = discord.Intents.default()
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Evento de Twitch (Webhook)
@app.route('/twitch-webhook', methods=['POST'])
def twitch_webhook():
    data = request.json
    print("Evento recibido:", data)

    if 'subscription' in data and 'event' in data:
        event = data['event']
        reward_title = event.get('reward', {}).get('title', '')

        # Verificar si es la recompensa específica
        if reward_title == "Mutear a Franaki":
            username = event.get('user_name')  # Nombre del usuario que canjeó
            bot.loop.create_task(mute_user(username))  # Ejecutar en el loop de Discord

    return jsonify({"status": "received"}), 200

# Función para mutear usuario en Discord
async def mute_user(username):
    guild = bot.get_guild(DISCORD_GUILD_ID)
    if not guild:
        print("No se encontró el servidor de Discord")
        return

    member = discord.utils.get(guild.members, name=username)
    if not member:
        print(f"No se encontró al usuario {username} en el servidor")
        return

    try:
        await member.edit(mute=True)
        print(f"{username} ha sido muteado por 5 minutos")
        
        await bot.wait_for("ready")  # Esperar a que el bot se inicie
        await asyncio.sleep(300)  # 5 minutos
        await member.edit(mute=False)
        print(f"{username} ha sido desmuteado")

    except Exception as e:
        print(f"Error al mutear a {username}: {e}")

# Iniciar Flask y Discord Bot en paralelo
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()
    bot.run(DISCORD_BOT_TOKEN)
