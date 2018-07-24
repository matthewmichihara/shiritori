from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import namedtuple
import romkan
from google.cloud import datastore

Vocab = namedtuple('Vocab', 'kana kanji romaji english first last')

vocab_url = 'file:///Users/matt/Code/shiritori/resources/jlpt-n5-vocab.html'
page = urlopen(vocab_url)
soup = BeautifulSoup(page, 'html.parser')

vocab_table = soup.find('table', attrs={'class': 'listing vocab-list'})
rows = vocab_table.find_all('tr')

vocabs = []

# Skipping the first row because it is headers.
for row in rows[1:]:
    tds = row.find_all('td')
    td_texts = [td.text.strip() for td in tds]
    _, kana, kanji, _, english = td_texts
    romaji = romkan.to_roma(kana)
    first = kana[0]
    last = kana[-1]
    vocabs.append(Vocab(kana, kanji, romaji, english, first, last))

client = datastore.Client()
task_key = client.key("Vocabulary")

tasks = []
for v in vocabs:
    task = datastore.Entity(key=task_key)
    task['kana'] = v.kana
    task['kanji'] = v.kanji
    task['romaji'] = v.romaji
    task['english'] = v.english
    task['first'] = v.first
    task['last'] = v.last
    tasks.append(task)

    # Batch api only lets us send 500 at a time.
    if len(tasks) == 500:
        client.put_multi(tasks)
        tasks = []

client.put_multi(tasks)



