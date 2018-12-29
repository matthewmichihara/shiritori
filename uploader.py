#!/usr/bin/env python
# -*- coding: utf-8 -*-

import romkan
import sys
from bs4 import BeautifulSoup
from collections import namedtuple
from google.cloud import datastore
from word import Word
from urllib.request import urlopen

def upload_to_datastore(words):
    print('Starting upload to datastore.')
    print('There are {} words.'.format(len(words)))

    client = datastore.Client()
    task_key = client.key('Word3')

    tasks = []
    for i, w in enumerate(words):
        task = datastore.Entity(key=task_key)
        task['jmdict_id'] = int(w.jmdict_id)
        task['kanji'] = w.kanji
        task['kana'] = w.kana
        task['romaji'] = w.romaji
        task['english'] = w.english
        task['first_romaji'] = w.first_romaji
        task['last_romaji'] = w.last_romaji
        task['ichi1'] = w.ichi1 == 'True'
        task['ichi2'] = w.ichi2 == 'True'
        task['news1'] = w.news1 == 'True'
        task['news2'] = w.news2 == 'True'
        task['spec1'] = w.spec1 == 'True'
        task['spec2'] = w.spec2 == 'True'

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

if __name__ == '__main__':
    words = []
    for line in sys.stdin:
        split_line = line.rstrip('\n').split('\t')
        word = Word(0, *split_line)
        words.append(word)

    upload_to_datastore(words)
