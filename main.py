import discord
from discord.ext import commands
import os
import requests
import json
from keep_alive import keep_alive
import musicbrainzngs

#CREDENTIALS & VARIABLES
APIKEY = os.environ['apikey']
TOKEN = os.environ['TOKEN']
client = discord.Client()
client = commands.Bot(command_prefix='$')
client.remove_command('help')
musicbrainzngs.set_useragent("User-Agent","nuDev/1.0.0 (nuDev@example.com) )",contact=None)

#Lets me know when logged in
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

#any setlist given date and artist (NOT PULLING SONGS)
@client.command()
async def set(ctx, *args):
  try:
    args = list(args)
    artist=" ".join(args[:-1])
    if not "-" in args[-1]:
      date = None
    else:
      date = args[-1]
    id_search = musicbrainzngs.search_artists(artist= artist)
    id= id_search['artist-list'][0]['id']
    print(id)
    
    url = f"https://api.setlist.fm/rest/1.0/search/setlists?artistMbid={id}&date={date}&p=1"
    headers = {'x-api-key': APIKEY, 'Accept': 'application/json'}
    r = requests.get(url, headers=headers)
    print(r.text)
    
    await sendSet(artist,date,ctx,r)
    
  except Exception:
    embed = discord.Embed(title="ERROR: Retreiving Data", color=discord.Color.red())
    embed.set_footer(text="Please make sure artist/ band is spelled correctly and date is in [DD-MM-YYYY] format")
    await ctx.send(embed=embed)

#Setlist for the Dead given date    
@client.command()
async def dead(ctx, args):
  try:
    date= args
    artist = "Grateful Dead"
      
    url = f"https://api.setlist.fm/rest/1.0/search/setlists?artistMbid=6faa7ca7-0d99-4a5e-bfa6-1fd5037520c6&date={date}&p=1"
    headers = {'x-api-key': APIKEY, 'Accept': "application/json"}
    r = requests.get(url, headers=headers)
    print(r.text)
    
    await sendSet(artist,date,ctx,r)
 
  except Exception:
      embed = discord.Embed(title="ERROR: Retreiving Data", color=discord.Color.red())
      embed.set_footer(text="Please make sure date is in [DD-MM-YYYY] format")
      await ctx.send(embed=embed)
    
#Setlist for Billy strings given date   
@client.command()
async def bmfs(ctx, args):
  try:
    date= args
    artist= "Billy Strings"
    
    url = f"https://api.setlist.fm/rest/1.0/search/setlists?artistMbid=640db492-34c4-47df-be14-96e2cd4b9fe4&date={date}&p=1"
    headers = {'x-api-key': APIKEY, 'Accept': "application/json"}
    r = requests.get(url, headers=headers)
    print(r.text)
    
    await sendSet(artist,date,ctx,r)
  
  except Exception:
    embed = discord.Embed(title="ERROR: Retreiving Data", color=discord.Color.red())
    embed.set_footer(text="Please make sure date is in [DD-MM-YYYY] format")
    await ctx.send(embed=embed)

#Method for Formatting JSON and sending setlist    
async def sendSet(artist,date,ctx,r):
  try:
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
      #PATCHING ERROR CAUSED BY $SET NON PERMANANT
      if songs == "":
        songs = "none"
      #END OF PATCH
      embed.add_field(name='Songs', value=songs, inline=False)
      try:
          embed.add_field(name='Tour Name', value=json.loads(r.text)["setlist"][0]["tour"]["name"], inline=False)
      except:
          pass 
      embed.add_field(name='Location', value=location, inline=False)
      await ctx.send(embed=embed)
  
  except Exception:
    embed = discord.Embed(title="ERROR: Assembling Setlist", color=discord.Color.red())
    embed.set_footer(text="Verify that your search is spelled correctly and date is in [DD-MM-YYYY]")
    await ctx.send(embed=embed)

#HELP
@client.command()
async def help(ctx):
  embed = discord.Embed(title="Help", color=discord.Color.blue())
  embed.add_field(name="$bmfs", value="Follow command with date [DD-MM-YYYY] to see the setlist from that date. i.e. $bmfs 29-06-2022", inline=False)
  embed.add_field(name="$dead", value="Follow command with date [DD-MM-YYYY] to see the setlist from that date. i.e. $dead 21-07-1990", inline=False)
  embed.add_field(name="$custy", value="All hail King Custy", inline=False)
  embed.add_field(name="$set", value="STILL IN DEVELOPMENT!!!Follow command with artist and date [DD-MM-YYYY] to see that artsits setlist from that day. i.e. $set widespread panic 25-07-2022", inline=False)
  await ctx.send(embed=embed)

#Easter egg  
@client.command()
async def custy(ctx):
  wook = discord.File("kingCust.jpg")
  embed = discord.Embed(title="King Custy", color=discord.Color.green())
  embed.set_image(url="attachment://kingCust.jpg")
  await ctx.send(embed=embed, file=wook)
 
#SERVER
keep_alive()
client.run(TOKEN)
