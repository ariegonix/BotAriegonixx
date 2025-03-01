import discord
import requests
import asyncio


# Configuración de tokens, ids y movidas varias
TOKEN = "TU_DISCORD_BOT_TOKEN"
TWITCH_CLIENT_ID = "ifsouj6utz6vjz4eneu4jf324euyba"
TWITCH_CLIENT_SECRET = "7prkdgbkhcgqcx90rbndfjsu1dtl3e"
TWITCH_USER = "ariegonixx"
DISCORD_CHANNEL_ID = 1336102942046162985


# Inicializamos el bot de Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)


# Variable global para almacenar el token de Twitch
TWITCH_ACCESS_TOKEN = None

async def get_twitch_token():
    """Obtiene un nuevo access_token de Twitch cuando caduca el anterior."""
    global TWITCH_ACCESS_TOKEN
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    
    response = requests.post(url, params=params)
    data = response.json()

    if "access_token" in data:
        TWITCH_ACCESS_TOKEN = data["access_token"]
    else:
        print("Error al obtener el token de Twitch:", data)

async def check_stream():
    """Consulta la API de Twitch y envía un mensaje si el usuario está en vivo."""
    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_ID)

    if TWITCH_ACCESS_TOKEN is None:
        await get_twitch_token()

    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}"
    }
    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USER}"

    response = requests.get(url, headers=headers)
    
    # Si el token ha caducado, generamos uno nuevo y reintentamos
    if response.status_code == 401:
        await get_twitch_token()
        headers["Authorization"] = f"Bearer {TWITCH_ACCESS_TOKEN}"
        response = requests.get(url, headers=headers)

    data = response.json()
    is_live = len(data["data"]) > 0

    if is_live:
        await channel.send(f"¡gentecilla, {TWITCH_USER} ha iniciado directo! \nhttps://twitch.tv/{TWITCH_USER}")

    await client.close()

@client.event
async def on_ready():
    """Cuando el bot se conecta, inicia la verificación del stream."""
    await check_stream()

client.run(TOKEN)
