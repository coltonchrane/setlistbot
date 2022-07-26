import discord
from discord.ext import commands
import os
import requests
import json
import datetime
from keep_alive import keep_alive
from extract import json_extract

#CREDENTIALS & VARIABLES
APIKEY = os.environ['apikey']
TOKEN = os.environ['TOKEN']
client = discord.Client()
client = commands.Bot(command_prefix='$')


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.command()
async def custy(ctx):
  wook = "kingCust.jpg"
  await ctx.channel.send(file=discord.File(wook))
  await ctx.channel.send("King Custy")

  
@client.command()
async def sl(ctx, *args):
  args = list(args)
  artist=" ".join(args[:-1])
  if not "-" in args[-1]:
    date = None
  else:
    date = args[-1]

  if not (artist and date):
    embed = discord.Embed(title=":warning: Please provide provide both a name and a date [YYYY-MM-DD]!", color=discord.Color.gold())
    embed.set_footer(text="Next Time Will Be Different, Until You Do It Again")
    await ctx.send(embed=embed)
    return

  headers = {'x-api-key': APIKEY, 'Accept': 'application/json'}
  r = requests.get(f"https://api.setlist.fm/rest/1.0/search/setlists?artistName=%7Bartist%7D&p=1&date=%7Bdate%7D", headers=headers)
  print(r.text)
  songs = ""
  for setlist in json.loads(r.text)["setlist"]:
    if artist in setlist["artist"]["name"]:
      for set in setlist["sets"]["set"]:
        try:
          songs += "-- "+set["name"].replace(':', '') +" --\n"
        except:
          pass
        for song in set["song"]:
          songs += song["name"]+"\n"
        songs += "\n"

    location = json.loads(r.text)["setlist"][0]["venue"]["name"] +", " +json.loads(r.text)["setlist"][0]["venue"]["city"]["name"]+", "+json.loads(r.text)["setlist"][0]["venue"]["city"]["state"]
    embed = discord.Embed(title="Setlist archive", color=discord.Color.gold())
    embed.add_field(name="Artist", value=artist, inline=True)
    embed.add_field(name='Date', value=date, inline=True)
    embed.add_field(name='Songs', value=songs, inline=False)
    try:
        embed.add_field(name='Tour Name', value=json.loads(r.text)["setlist"][0]["tour"]["name"], inline=False)
    except:
        pass 
    embed.add_field(name='Location', value=location, inline=False)
    embed.set_footer(text="Boy, Man, God, Shit")
    await ctx.send(embed=embed)


#SERVER
keep_alive()
client.run(TOKEN)






