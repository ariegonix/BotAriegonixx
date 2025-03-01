import discord
import requests
import asyncio

# Configuración de tokens e IDs
TOKEN = "TU_DISCORD_BOT_TOKEN"
TWITCH_CLIENT_ID = "ifsouj6utz6vjz4eneu4jf324euyba"
TWITCH_CLIENT_SECRET = "7prkdgbkhcgqcx90rbndfjsu1dtl3e"
TWITCH_USER = "ariegonixx"
DISCORD_CHANNEL_DIRECTO = 1336102942046162985
DISCORD_CHANNEL_SALUDO = 1329137244891775016

# Inicializamos el bot con permisos para detectar nuevos usuarios
intents = discord.Intents.default()
intents.members = True  
client = discord.Client(intents=intents)

# Variables globales
TWITCH_ACCESS_TOKEN = None
stream_active = False  # Para evitar avisos repetidos

async def get_twitch_token():
    """Obtiene un nuevo access_token de Twitch."""
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
        print("❌ Error al obtener el token de Twitch:", data)

async def check_stream():
    """Consulta la API de Twitch y avisa solo si el usuario inicia directo."""
    global stream_active

    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_DIRECTO)

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

    try:
        data = response.json()
        is_live = len(data["data"]) > 0

        if is_live and not stream_active:
            await channel.send(f"🔴 ¡{TWITCH_USER} ha iniciado directo! \n🎥 https://twitch.tv/{TWITCH_USER}")
            stream_active = True  # Marcar el stream como activo

    except Exception as e:
        print(f"⚠️ Error al verificar el stream: {e}")

@client.event
async def on_ready():
    """Cuando el bot se conecta, revisa si hay stream activo y espera usuarios nuevos."""
    print(f"✅ Bot conectado como {client.user}")
    await check_stream()  # Solo revisa una vez al iniciar

@client.event
async def on_member_join(member):
    """Cuando un usuario se une, le damos la bienvenida."""
    channel = client.get_channel(DISCORD_CHANNEL_SALUDO)
    if channel:
        await channel.send(f"🎉 ¡Bienvenido/a {member.mention} al servidor! 🎊 Disfruta tu estadía.")

client.run(TOKEN)