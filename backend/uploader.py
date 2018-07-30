#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen
from bs4 import BeautifulSoup
from collections import namedtuple
import romkan
from google.cloud import datastore
import sys

Word = namedtuple('Word', 'jmdict_id kanji kana romaji english first_romaji last_romaji')

def upload_to_datastore(words):
    print('Starting upload to datastore.')
    print('There are {} words.'.format(len(words)))

    client = datastore.Client()
    task_key = client.key('Word')

    tasks = []
    for i, w in enumerate(words):
        task = datastore.Entity(key=task_key)
        task['jmdict_id'] = w.jmdict_id
        task['kanji'] = w.kanji
        task['kana'] = w.kana
        task['romaji'] = w.romaji
        task['english'] = w.english
        task['first_romaji'] = w.first_romaji
        task['last_romaji'] = w.last_romaji
        tasks.append(task)

        # Batch api only lets us send 500 at a time.
        if len(tasks) == 500:
            print('Uploading...')
            client.put_multi(tasks)
            print('Uploaded {}/{} words.'.format(i, len(words)))
            tasks = []

    print('Uploading...')
    client.put_multi(tasks)
    print("Finished uploading.")

words = []
for line in sys.stdin:
    split_line = unicode(line, 'utf-8').rstrip('\n').split('\t')
    word = Word(*split_line)
    words.append(word)

upload_to_datastore(words)
