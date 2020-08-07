from googlesearch import search
from bs4 import BeautifulSoup
import requests

SOURCES = {
    'default': ('letras.com', '.cnt-letra'),
    'cat': ('cancioneros.com', '.lletra_can'),
    'jp': ('j-lyric.net', '#Lyric')
}

def find(query, source='default'):
    host, selector = SOURCES[source]
    try:
        url = next(search(f'{query} site:{host}'))
    except StopIteration:
        return None

    r = requests.get(url)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, features='lxml')
    lyrics = soup.select_one(selector)
    if not lyrics:
        return None
    return list(lyrics.stripped_strings)
