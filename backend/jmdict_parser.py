#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import romkan
from argparse import ArgumentParser
from romaji_normalizer import normalize

def get_kanji(entry):
    k_ele = entry.find('k_ele')
    if k_ele is None:
        return ''

    keb = k_ele.find('keb')
    if keb is None:
        return ''

    return keb.text

VALID_FREQUENCY_ANNOTATIONS = set(['ichi1', 'ichi2', 'news1', 'news2', 'spec1', 'spec2'])
def get_frequency_annotations(entry):
    r_ele = entry.find('r_ele')
    if r_ele is None:
        return ''

    frequency_annotations = set()
    re_pris = r_ele.findall('re_pri')
    for re_pri in re_pris:
        annotation = re_pri.text
        if annotation in VALID_FREQUENCY_ANNOTATIONS:
            frequency_annotations.add(annotation)

    return frequency_annotations

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

def get_first_romaji(kana):
    first_kana = kana[0]
    normalized = normalize(first_kana)
    return romkan.to_roma(normalized)

def get_last_romaji(kana):
    last_kana = kana[-1]
    normalized = normalize(last_kana)
    return romkan.to_roma(normalized)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename", help="The JMDict file to parse", required=True)
    args = parser.parse_args()
    tree = ET.parse(args.filename)
    root = tree.getroot()

    for entry in root:
        annotations = get_frequency_annotations(entry)
        jmdict_id = entry.find('ent_seq').text
        kanji = get_kanji(entry)
        kana = get_kana(entry)
        romaji = get_romaji(kana)
        english = get_english(entry)
        first_romaji = get_first_romaji(kana)
        last_romaji = get_last_romaji(kana)
        ichi1 = str('ichi1' in annotations)
        ichi2 = str('ichi2' in annotations)
        news1 = str('news1' in annotations)
        news2 = str('news2' in annotations)
        spec1 = str('spec1' in annotations)
        spec2 = str('spec2' in annotations)

        
        line = "\t".join((jmdict_id, kanji, kana, romaji, english, first_romaji, last_romaji, ichi1, ichi2, news1, news2, spec1, spec2))
        print(line)
