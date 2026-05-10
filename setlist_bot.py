import discord
from discord.ext import commands
from discord import app_commands
import os
import aiohttp
import json
import logging
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# Load .env if it exists
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('setlistbot')

# --- KEEP ALIVE SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "SetlistBot is running!"

@app.route('/health')
def health():
    return {"status": "ok"}, 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Flask keep-alive on port {port}")
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
# -------------------------

# CREDENTIALS & VARIABLES
API_URL = os.environ.get('SETLIST_API_URL', 'http://localhost:5000/api/setlist')
TOKEN = os.environ.get('TOKEN') or os.environ.get('DISCORD_TOKEN')

class SetlistBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        # Slash commands don't technically need message_content, 
        # but we keep it for now if you want to add prefix commands back later.
        intents.message_content = True 
        super().__init__(command_prefix='$', intents=intents)

    async def setup_hook(self):
        # This copies the global commands over to your guild for instant testing
        # In production, you'd just use tree.sync() which can take an hour to propagate globally.
        logger.info("Syncing slash commands...")
        await self.tree.sync()
        logger.info("Slash commands synced.")

client = SetlistBot()
client.remove_command('help')

@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user} (ID: {client.user.id})')
    logger.info('------')

async def fetch_setlist(artist: str, date: str = None):
    params = {'artist': artist}
    if date:
        params['date'] = date
    
    logger.info(f"Fetching setlist for {artist} on {date} from {API_URL}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params) as response:
                if response.status == 200:
                    return await response.json(), None
                elif response.status == 404:
                    return None, "GONE FISHIN': No show record found for that date."
                else:
                    return None, f"Error from API: {response.status}"
    except Exception as e:
        logger.error(f"Error fetching setlist: {e}")
        return None, f"Connection error: {e}"

@client.tree.command(name="setlist", description="Get a setlist for an artist and date (DD-MM-YYYY)")
@app_commands.describe(artist="Name of the artist", date="Date of the show (DD-MM-YYYY)")
async def setlist(interaction: discord.Interaction, artist: str, date: str = None):
    # Acknowledge the interaction immediately to prevent timeout
    await interaction.response.defer()
    
    data, error = await fetch_setlist(artist, date)
    
    if error:
        await interaction.followup.send(error)
        return

    await send_formatted_setlist(interaction, data)

async def send_formatted_setlist(interaction, data):
    try:
        set_data = data["setlist"][0]
        artist_name = set_data["artist"]["name"]
        venue = set_data["venue"]["name"]
        city = set_data["venue"]["city"]["name"]
        state = set_data["venue"]["city"].get("state", "")
        date_str = set_data["eventDate"]
        
        embed = discord.Embed(title="Setlist", color=discord.Color.gold())
        embed.add_field(name="Artist", value=artist_name, inline=True)
        embed.add_field(name='Date', value=date_str, inline=True)
        
        songs_text = ""
        sets_data = set_data.get("sets", {}).get("set", [])
        
        if isinstance(sets_data, dict):
            sets_data = [sets_data]
            
        for s in sets_data:
            set_name = s.get('name') or "Set"
            songs_text += f"-- {set_name} --\n"
            for song in s.get("song", []):
                songs_text += f"**{song['name']}**\n"
        
        # Discord embed fields have a 1024 char limit
        if len(songs_text) > 1020:
            songs_text = songs_text[:1017] + "..."

        embed.add_field(name='Songs', value=songs_text or "No songs listed", inline=False)
        embed.add_field(name='Location', value=f"{venue}, {city}, {state}", inline=False)
        
        await interaction.followup.send(embed=embed)
    except Exception as e:
        logger.error(f"Error assembling setlist: {e}")
        await interaction.followup.send(f"Error assembling setlist: {e}")

if __name__ == "__main__":
    if TOKEN:
        keep_alive()
        logger.info("Starting Discord bot with Slash Commands...")
        client.run(TOKEN)
    else:
        logger.error("TOKEN not found in environment variables.")
