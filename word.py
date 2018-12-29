from collections import namedtuple
import random

Word = namedtuple('Word', 'id jmdict_id kanji kana romaji english first_romaji last_romaji ichi1 ichi2 news1 news2 spec1 spec2')

def entity_to_word(entity):
    word = Word(
        entity.key.id,
        entity['jmdict_id'],
        entity['kanji'],
        entity['kana'],
        entity['romaji'],
        entity['english'],
        entity['first_romaji'],
        entity['last_romaji'],
        entity['ichi1'],
        entity['ichi2'],
        entity['news1'],
        entity['news2'],
        entity['spec1'],
        entity['spec2']
    )

    return word

def is_common(word):
    return word.ichi1 or word.ichi2 or word.news1 or word.news2 or word.spec1 or word.spec2

def pick_your_word(your_word_entities):
    if not your_word_entities:
        return None

    # Prioritize the common words.
    common_words = [word for word in your_word_entities if is_common(word)]
    if common_words:
        return random.choice(common_words)

    return random.choice(your_word_entities)

def pick_opponent_word(opponent_word_entities, used_ids):
    # Get the valid words.
    valid_opponent_words = []
    for word in opponent_word_entities:
        if word.id in used_ids:
            continue
        if word.last_romaji in ('n', '-'):
            continue
        valid_opponent_words.append(word)

    # No valid words.
    if not valid_opponent_words:
        return None

    # Get the common words.
    common_words = [word for word in valid_opponent_words if is_common(word)]
    if common_words:
        return random.choice(common_words)

    return random.choice(valid_opponent_words)

