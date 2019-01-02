#!/usr/bin/env python
# -*- coding: utf-8 -*-

import romkan
import sys
from bs4 import BeautifulSoup
from collections import namedtuple
from google.cloud import datastore
from word import Word, is_common, has_valid_ending
from urllib.request import urlopen
from itertools import groupby

def upload(client, task_key, items, item_to_task_mapper):
    print('Starting upload to datastore.')
    print('There are {} items.'.format(len(items)))

    tasks = []
    for i, item in enumerate(items):
        task = item_to_task_mapper(item)
        tasks.append(task)

        # Batch api only lets us send 500 at a time.
        if len(tasks) == 500:
            print('Uploading...')
            client.put_multi(tasks)
            print('Uploaded {}/{} items.'.format(i, len(items)))
            tasks = []

    print('Uploading...')
    client.put_multi(tasks)
    print("Finished uploading.")


def upload_words_to_datastore(client, words):
    print("Words")
    task_key = client.key('Word3')

    def mapper(word):
        task = datastore.Entity(key=task_key)
        task['jmdict_id'] = w.jmdict_id
        task['kanji'] = w.kanji
        task['kana'] = w.kana
        task['romaji'] = w.romaji
        task['english'] = w.english
        task['first_romaji'] = w.first_romaji
        task['last_romaji'] = w.last_romaji
        task['ichi1'] = w.ichi1
        task['ichi2'] = w.ichi2
        task['news1'] = w.news1
        task['news2'] = w.news2
        task['spec1'] = w.spec1
        task['spec2'] = w.spec2
        return task

    upload(client, task_key, words, mapper)

def upload_jmdict_ids_by_first_romaji_to_datastore(client, ids_by_first_romaji, task_key):
    def mapper(item):
        task = datastore.Entity(key=task_key)
        task['first_romaji'] = item[0]
        task['jmdict_ids'] = item[1]
        return task

    upload(client, task_key, ids_by_first_romaji, mapper)

def get_jmdict_ids_by_first_romaji(words):
    sorted_words = sorted(words, key=lambda w: w.first_romaji)
    jmdict_ids_by_first_romaji = []
    for first_romaji, words in groupby(sorted_words, lambda w: w.first_romaji):
        jmdict_ids = [int(word.jmdict_id) for word in words]
        jmdict_ids_by_first_romaji.append((first_romaji, jmdict_ids))

    return jmdict_ids_by_first_romaji

if __name__ == '__main__':
    words = []
    for line in sys.stdin:
        split_line = line.rstrip('\n').split('\t')
        (jmdict_id, kanji, kana, romaji, english, first_romaji, last_romaji, ichi1, ichi2, news1, news2, spec1, spec2) = split_line
        word = Word(0, int(jmdict_id), kanji, kana, romaji, english, first_romaji, last_romaji,
            ichi1 == 'True', ichi2 == 'True', news1 == 'True', news2 == 'True', spec1 == 'True', spec2 == 'True')
        words.append(word)

    client = datastore.Client()

    # Upload all words.
    upload_words_to_datastore(client, words)

    # Filter to words with valid endings.
    words_with_valid_endings = []
    for word in words:
        if not has_valid_ending(word):
            continue
        words_with_valid_endings.append(word)
    
    # Filter to common words.
    common_words_with_valid_endings = []
    for word in words_with_valid_endings:
        if not is_common(word):
            continue
        common_words_with_valid_endings.append(word)

    # Upload common
    print("Common JMDict IDs by first romaji")
    common_jmdict_ids_by_first_romaji = get_jmdict_ids_by_first_romaji(common_words_with_valid_endings)
    common_key = client.key('CommonJmDictIdsByFirstRomaji2')
    upload_jmdict_ids_by_first_romaji_to_datastore(client, common_jmdict_ids_by_first_romaji, common_key)

    # Upload uncommon
    print("Uncommon JMDict IDs by first romaji")
    uncommon_words_with_valid_endings = list(set(words_with_valid_endings) - set(common_words_with_valid_endings))
    uncommon_jmdict_ids_by_first_romaji = get_jmdict_ids_by_first_romaji(uncommon_words_with_valid_endings)
    uncommon_key = client.key('UncommonJmDictIdsByFirstRomaji2')
    upload_jmdict_ids_by_first_romaji_to_datastore(client, uncommon_jmdict_ids_by_first_romaji, uncommon_key)
