"""
#FINDS AND GRABS JSON DATA AND LOADS INTO PY DICTIONARY
def get_setlist(date):
    url = "https://api.setlist.fm/rest/1.0/search/setlists?artistMbid=640db492-34c4-47df-be14-96e2cd4b9fe4&date=" + date + "&p=1"
    headers = {'x-api-key': APIKEY, 'Accept': "application/json"}
    response = requests.get(url, headers=headers)
    print(response.text)

    #JSON INTO PY DICTIONARY
    json_data = json_extract(json.loads(response.text), "name")
    #setlist = json.loads(response.text)
    #Format data
    return json_data
    #return setlist

"""

'''@client.event
async def on_message(message):
    msg = message.content
    if message.author == client.user:
        return
    if msg.startswith("$sl"):
        #DATE VALIDATOR
        date = msg.split("$sl ", 1)[1]
        if '/' in date:
            await message.channel.send("Date must be in DD-MM-YYYY format.")
        else:
            day, month, year = date.split('-')
            isValidDate = True
            try:
                datetime.datetime(int(year), int(month), int(day))
            except ValueError:
                isValidDate = False
            if (isValidDate):

                #GET SETLIST
                setlist = get_setlist(date)

                #NO SHOW DATA
                if not setlist:
                    print(setlist)
                    await message.channel.send(
                        file=discord.File("gonfishn.jpg"))
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
        await message.channel.send(
            "Type the command followed by the date in this format '$sl DD-MM-YYYY' to get info"
        )
'''


"""Extract nested values from a JSON tree."""


'''def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values
    '''