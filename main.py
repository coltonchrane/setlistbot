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

#any setlist given date and artist
@client.command()
async def set(ctx, *args):
  try:
    args = list(args)
    artist=" ".join(args[:-1])
    if not "-" in args[-1]:
      date = None
    else:
      date = args[-1]

#using musicbrainz api gives search more robustness in search and formatting than setlist.fm artistname (typos,etc.)
    id_search = musicbrainzngs.search_artists(artist= artist)
    id= id_search['artist-list'][0]['id']
    artist= id_search['artist-list'][0]['name']
    url = f"https://api.setlist.fm/rest/1.0/search/setlists?artistMbid={id}&date={date}&p=1" 
    headers = {'x-api-key': APIKEY, 'Accept': 'application/json'}
    r = requests.get(url, headers=headers)
    await sendSet(artist,date,ctx,r)
    
  except Exception:
    fear = discord.File("images/fear.gif")
    embed = discord.Embed(title="ERROR: Retreiving Data", color=discord.Color.red())
    embed.add_field(name= "Suggestion", value="Please make sure the artist is spelled correctly and date is in [DD-MM-YYYY] format")
    embed.set_image(url='attachment://fear.gif')
    await ctx.send(embed=embed, file = fear)

#Setlist for the Dead given date    
@client.command()
async def dead(ctx, args):
  try:
    date= args
    artist = "Grateful Dead"
      
    url = f"https://api.setlist.fm/rest/1.0/search/setlists?artistMbid=6faa7ca7-0d99-4a5e-bfa6-1fd5037520c6&date={date}&p=1"
    headers = {'x-api-key': APIKEY, 'Accept': "application/json"}
    r = requests.get(url, headers=headers)
    await sendSet(artist,date,ctx,r)
 
  except Exception:
    fear = discord.File("images/fear.gif")
    embed = discord.Embed(title="ERROR: Retreiving Data", color=discord.Color.red())
    embed.add_field(name= "Suggestion", value="Please make sure date is in [DD-MM-YYYY] format")
    embed.set_image(url='attachment://fear.gif')
    await ctx.send(embed=embed, file = fear)
    
#Setlist for Billy strings given date   
@client.command()
async def bmfs(ctx, args):
  try:
    date= args
    artist= "Billy Strings"
    url = f"https://api.setlist.fm/rest/1.0/search/setlists?artistMbid=640db492-34c4-47df-be14-96e2cd4b9fe4&date={date}&p=1"
    headers = {'x-api-key': APIKEY, 'Accept': "application/json"}
    r = requests.get(url, headers=headers)
    await sendSet(artist,date,ctx,r)
  
  except Exception:
    fear = discord.File("images/fear.gif")
    embed = discord.Embed(title="ERROR: Retreiving Data", color=discord.Color.red())
    embed.add_field(name= "Suggestion", value="Please make sure date is in [DD-MM-YYYY] format")
    embed.set_image(url='attachment://fear.gif')
    await ctx.send(embed=embed, file = fear)

#Method for Formatting JSON and sending setlist    
async def sendSet(artist,date,ctx,r):
  try:
    songs = ""
    for setlist in json.loads(r.text)["setlist"]:
      if artist in setlist["artist"]["name"]:
        artist = "["+ artist +"](" + setlist["artist"]["url"] + ")"
        for set in setlist["sets"]["set"]:
          try:
            songs += "-- "+set["name"].replace(':', '') +" --\n"
          except:
            pass
          for song in set["song"]:
            songs += "**"+song["name"]+"**"
            if "info" in song:
              songs += " " +song["info"] +"\n"
            else:
              songs+= "\n"
            if "cover" in song:
              songs+= "*by " + song["cover"]["name"]+"*\n"
          songs += "\n"
          
      location = "[" +json.loads(r.text)["setlist"][0]["venue"]["name"] +", " +json.loads(r.text)["setlist"][0]["venue"]["city"]["name"]+", "+json.loads(r.text)["setlist"][0]["venue"]["city"]["state"] + "](" + setlist["venue"]["url"] +")"
      date = "["+date+"]("+ setlist["url"]+")"
      embed = discord.Embed(title="Setlist", color=discord.Color.gold())
      embed.add_field(name="Artist", value=artist, inline=True)
      embed.add_field(name='Date', value=date, inline=True)
      if songs == "":
        songs = "Song information not available"
      embed.add_field(name='Songs', value=songs, inline=False)
      try:
          embed.add_field(name='Tour Name', value=json.loads(r.text)["setlist"][0]["tour"]["name"], inline=False)
      except:
          pass 
      embed.add_field(name='Location', value=location, inline=False)
      await ctx.send(embed=embed)
  
  except Exception:
    fear = discord.File("images/fear2.gif")
    embed = discord.Embed(title="ERROR: Assembling Setlist", color=discord.Color.red())
    embed.add_field(name= "Suggestion", value="Verify that your search is spelled correctly and date is in [DD-MM-YYYY]")
    embed.set_image(url='attachment://fear2.gif')
    await ctx.send(embed=embed, file = fear)

#HELP
@client.command()
async def help(ctx):
  embed = discord.Embed(title="setlistbot Commands", color=discord.Color.blue())
  embed.add_field(name="$help", value="Displays setlistbot commands", inline=False)
  embed.add_field(name="$set {artist} {date}", value="Displays setlist given artist and date. [DD-MM-YYYY] i.e. $set widespread panic 25-07-2022", inline=False)
  embed.add_field(name="$bmfs {date}", value="Displays Billy Strings setlist given date. [DD-MM-YYYY] i.e. $bmfs 29-06-2022", inline=False)
  embed.add_field(name="$dead {date}", value="Displays the Grateful Dead setlist given date. [DD-MM-YYYY] i.e. $dead 21-07-1990", inline=False)
  embed.add_field(name="$custy", value="All hail King Custy", inline=False)
  embed.add_field(name="The Grateful Spunions Collection", value="[Click here for music](https://drive.google.com/drive/folders/1NSDvB7XjIrig_oGQN4dcyhehjTMJm9PP?usp=sharing)", inline=False)
  jerry = discord.File("images/jerry.gif")
  embed.set_image(url='attachment://jerry.gif')
  await ctx.send(embed=embed, file = jerry)

#Easter egg  
@client.command()
async def custy(ctx):
  wook = discord.File("images/kingCust.jpg")
  embed = discord.Embed(title="King Custy", color=discord.Color.green())
  embed.set_image(url="attachment://kingCust.jpg")
  await ctx.send(embed=embed, file=wook)
 
#SERVER
keep_alive()
client.run(TOKEN)


#SCRAP CODE

#search by artist name (less robust)
#f'https://api.setlist.fm/rest/1.0/search/setlists?artistName={artist}&p=1&date={date}'

#search by music brainz id (more robust)
#import musicbrainzngs
#musicbrainzngs.set_useragent("User-Agent","nuDev/1.0.0 (nuDev@example.com) )",contact=None)
#id_search = musicbrainzngs.search_artists(artist= artist)
#id= id_search['artist-list'][0]['id']
#print(id)
#url = f"https://api.setlist.fm/rest/1.0/search/setlists?artistMbid={id}&date={date}&p=1"
