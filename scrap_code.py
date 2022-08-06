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

#f'https://api.setlist.fm/rest/1.0/search/setlists?artistName={artist}&p=1&date={date}'
