import discord
from discord.ext import commands
import os
import aiohttp
import json
from flask import Flask
from threading import Thread

# --- KEEP ALIVE SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "SetlistBot is running!"

def run_flask():
    # Azure App Service usually provides a PORT env var
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
# -------------------------

# CREDENTIALS & VARIABLES
# In Azure, these will be App Service Environment Variables
API_URL = os.environ.get('SETLIST_API_URL', 'http://localhost:5000/api/setlist')
TOKEN = os.environ.get('TOKEN')

client = commands.Bot(command_prefix='$')
client.remove_command('help')

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

async def fetch_setlist(artist, date=None):
    params = {'artist': artist}
    if date:
        params['date'] = date
    
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL, params=params) as response:
            if response.status == 200:
                return await response.json(), None
            elif response.status == 404:
                return None, "GONE FISHIN': No show record found for that date."
            else:
                return None, f"Error from API: {response.status}"

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
        for s in setlist.get("sets", {}).get("set", []):
            songs_text += f"-- {s.get('name', 'Set')} --\n"
            for song in s.get("song", []):
                songs_text += f"**{song['name']}**\n"
        
        embed.add_field(name='Songs', value=songs_text or "No songs listed", inline=False)
        embed.add_field(name='Location', value=f"{venue}, {city}, {state}", inline=False)
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error assembling setlist: {e}")

@client.command()
async def dead(ctx, date):
    data, error = await fetch_setlist("Grateful Dead", date)
    if error: await ctx.send(error)
    else: await send_formatted_setlist(ctx, data)

@client.command()
async def bmfs(ctx, date):
    data, error = await fetch_setlist("Billy Strings", date)
    if error: await ctx.send(error)
    else: await send_formatted_setlist(ctx, data)

@client.command()
async def help(ctx):
    embed = discord.Embed(title="SetlistBot (Powered by .NET)", color=discord.Color.blue())
    embed.add_field(name="$set {artist} {date}", value="e.g. $set widespread panic 25-07-2022", inline=False)
    await ctx.send(embed=embed)

if __name__ == "__main__":
    if TOKEN:
        keep_alive()
        client.run(TOKEN)
    else:
        print("TOKEN not found in environment variables.")
