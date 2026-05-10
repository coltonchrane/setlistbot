import discord
from discord.ext import commands
import os
import aiohttp
import json
import logging
from flask import Flask
from threading import Thread

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
    # Azure App Service provides a PORT env var. Default to 8080.
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

# Define Intents (Required for discord.py 2.0+)
intents = discord.Intents.default()
intents.message_content = True  # Allows bot to read message content for commands

client = commands.Bot(command_prefix='$', intents=intents)
client.remove_command('help')

@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user} (ID: {client.user.id})')
    logger.info('------')

async def fetch_setlist(artist, date=None):
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

@client.command()
async def set(ctx, *args):
    args = list(args)
    if not args:
        await ctx.send("Please provide an artist name.")
        return
        
    artist = " ".join(args[:-1]) if "-" in args[-1] else " ".join(args)
    date = args[-1] if "-" in args[-1] else None

    data, error = await fetch_setlist(artist, date)
    
    if error:
        await ctx.send(error)
        return

    await send_formatted_setlist(ctx, data)

async def send_formatted_setlist(ctx, data):
    try:
        setlist = data["setlist"][0]
        artist_name = setlist["artist"]["name"]
        venue = setlist["venue"]["name"]
        city = setlist["venue"]["city"]["name"]
        state = setlist["venue"]["city"].get("state", "")
        date_str = setlist["eventDate"]
        
        embed = discord.Embed(title="Setlist", color=discord.Color.gold())
        embed.add_field(name="Artist", value=artist_name, inline=True)
        embed.add_field(name='Date', value=date_str, inline=True)
        
        songs_text = ""
        sets_data = setlist.get("sets", {}).get("set", [])
        
        # Ensure sets_data is a list
        if isinstance(sets_data, dict):
            sets_data = [sets_data]
            
        for s in sets_data:
            set_name = s.get('name') or "Set"
            songs_text += f"-- {set_name} --\n"
            for song in s.get("song", []):
                songs_text += f"**{song['name']}**\n"
        
        embed.add_field(name='Songs', value=songs_text or "No songs listed", inline=False)
        embed.add_field(name='Location', value=f"{venue}, {city}, {state}", inline=False)
        
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error assembling setlist: {e}")
        await ctx.send(f"Error assembling setlist: {e}")

@client.command()
async def help(ctx):
    embed = discord.Embed(title="SetlistBot (Powered by .NET)", color=discord.Color.blue())
    embed.add_field(name="$set {artist} {date}", value="e.g. $set widespread panic 25-07-2022", inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    if TOKEN:
        keep_alive()
        logger.info("Starting Discord bot...")
        client.run(TOKEN)
    else:
        logger.error("TOKEN not found in environment variables (tried TOKEN and DISCORD_TOKEN).")
