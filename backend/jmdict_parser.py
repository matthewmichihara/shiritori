#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import romkan
from argparse import ArgumentParser

def get_kanji(entry):
    k_ele = entry.find('k_ele')
    if k_ele is None:
        return ''

    keb = k_ele.find('keb')
    if keb is None:
        return ''

    return keb.text

def get_kana(entry):
    r_ele = entry.find('r_ele')
    if r_ele is None:
        return ''

    reb = r_ele.find('reb')
    if reb is None:
        return ''

    return reb.text

def get_romaji(kana):
    romaji = romkan.to_roma(kana)

    # Get rid of these things.
    return romaji.replace('\'', '')

# There are multiple `sense` elements. Just grabbing the first for now.
def get_english(entry):
    sense = entry.find('sense')
    if sense is None:
        return ''

    # There are multiple of these too.
    gloss = sense.find('gloss')
    if gloss is None:
        return ''

    return gloss.text

# Use the "big"(?) version of the small characters so that romkan doesn't prepend an 'x'.
NORMALIZE_DICT = {
    u"ぁ":u"あ",
    u"ぃ":u"い",
    u"ぅ":u"う",
    u"ぇ":u"え",
    u"ぉ":u"お",
    u"ゃ":u"や",
    u"ゅ":u"ゆ",
    u"ょ":u"よ",
    u"っ":u"つ",
    u"ァ":u"ア",
    u"ィ":u"イ",
    u"ゥ":u"ウ",
    u"ェ":u"エ",
    u"ォ":u"オ",
    u"ャ":u"ヤ",
    u"ュ":u"ユ",
    u"ョ":u"ヨ",
    u"ッ":u"ツ"
}

def get_first_romaji(kana):
    first_kana = kana[0]
    normalized = NORMALIZE_DICT.get(first_kana, first_kana)
    return romkan.to_roma(normalized)

def get_last_romaji(kana):
    last_kana = kana[-1]
    normalized = NORMALIZE_DICT.get(last_kana, last_kana)
    return romkan.to_roma(normalized)

parser = ArgumentParser()
parser.add_argument("-f", "--file", dest="filename", help="The JMDict file to parse", required=True)
args = parser.parse_args()
tree = ET.parse(args.filename)
root = tree.getroot()

for entry in root:
    jmdict_id = int(entry.find('ent_seq').text)
    kanji = get_kanji(entry)
    kana = get_kana(entry)
    romaji = get_romaji(kana)
    english = get_english(entry)
    first_romaji = get_first_romaji(kana)
    last_romaji = get_last_romaji(kana)
    
    line = "\t".join((str(jmdict_id), kanji, kana, romaji, english, first_romaji, last_romaji))
    print(line)
 
