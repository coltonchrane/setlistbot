import discord
from discord.ext import commands
import os
import requests
import json
import datetime
from keep_alive import keep_alive
from extract import json_extract

#CREDENTIALS & VARIABLES
APIKEY = "x-tZ3HcHUpy5e8UZWqjdCsDi_LFk5uJHGGjG"
TOKEN = os.environ['TOKEN']
client = discord.Client()
date = "21-08-2021"
client = commands.Bot(command_prefix="!")


#FINDS AND GRABS JSON DATA AND LOADS INTO PY DICTIONARY
def get_setlist(date):
  url = "https://api.setlist.fm/rest/1.0/search/setlists?artistMbid=640db492-34c4-47df-be14-96e2cd4b9fe4&date="+date+"&p=1"
  headers = {
          'x-api-key': APIKEY ,
          'Accept': "application/json"
  }
  response = requests.get(url, headers=headers)
  print(response.text)

#JSON INTO PY DICTIONARY
  json_data = json_extract(json.loads(response.text),"name") 
  #setlist = json.loads(response.text)   
  #Format data

  return json_data
  #return setlist

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    msg = message.content
    if message.author == client.user:
        return
    if msg.startswith("$sl"):
#DATE VALIDATOR
      date = msg.split("$sl ",1)[1]  
      if '/' in date:
        await message.channel.send("Date must be in DD-MM-YYYY format.")
      else:
        day,month,year = date.split('-')
        isValidDate = True
        try:
          datetime.datetime(int(year),int(month), int(day))
        except ValueError:
          isValidDate = False
        if(isValidDate):

#GET SETLIST
          setlist = get_setlist(date)

#NO SHOW DATA
          if not setlist:
            print(setlist)
            await message.channel.send(file=discord.File("gonfishn.jpg"))
            await message.channel.send("No setlist for that day")
          else:
            print(setlist)
            await message.channel.send(setlist)
        else:
          await message.channel.send("Date must be in DD-MM-YYYY format.")
      
#EPIC TROLL       
    if msg.startswith("$Billycord"):
      wook = "kingCust.jpg"  
      await message.channel.send(file=discord.File(wook))
      await message.channel.send("King Custy")

#HELP
    if msg.startswith("$help"):
      await message.channel.send("Type the command followed by the date in this format '$sl DD-MM-YYYY' to get info")


#ALTERNATE METHOD
"""@client.command()
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
"""
#SERVER
keep_alive()
client.run(TOKEN)
