from collections import namedtuple
import random
from concurrent.futures import ThreadPoolExecutor

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

def has_valid_ending(word):
    return word.last_romaji not in ('n', '-')

def pick_your_word(your_word_entities):
    if not your_word_entities:
        return None

    # Prioritize the common words.
    common_words = [word for word in your_word_entities if is_common(word)]
    if common_words:
        return random.choice(common_words)

    return random.choice(your_word_entities)

def fetch_opponent_word(last_roma, used_ids, parent_span, client):
    with parent_span.span(name='fetch opponent word') as span:
        jmdict_id = fetch_matching_jmdict_ids(last_roma, used_ids, span, client)
        if jmdict_id is None:
            return None

        with span.span(name='fetch opponent word by id'):
            query = client.query(kind='Word3')
            query.add_filter('jmdict_id', '=', jmdict_id)
            opponent_words = list(query.fetch(limit=1))
            if not opponent_words:
                return None
            return entity_to_word(opponent_words[0])

def fetch_matching_jmdict_ids(last_roma, used_ids, parent_span, client):
    with parent_span.span(name='fetch matching jmdict ids'):
        executor = ThreadPoolExecutor()
        try:
            common_future = executor.submit(fetch_matching_common_jmdict_ids, last_roma, used_ids, parent_span, client)
            uncommon_future = executor.submit(fetch_matching_uncommon_jmdict_ids, last_roma, used_ids, parent_span, client)

            common_result = common_future.result()
            if common_result is not None:
                return common_result

            return uncommon_future.result()
        finally:
            executor.shutdown(wait=False)

def fetch_matching_common_jmdict_ids(last_roma, used_ids, parent_span, client):
    jmdict_id = None
    with parent_span.span(name='fetch matching common jmdict ids'):
        query = client.query(kind='CommonJmDictIdsByFirstRomaji2')
        query.add_filter('first_romaji', '=', last_roma)
        results = list(query.fetch(limit=1))
        if not results:
            return None
        result = results[0]

        jmdict_ids = set(result['jmdict_ids'])

        candidate_jmdict_ids = list(jmdict_ids - used_ids)
        if not candidate_jmdict_ids:
            return None

        return random.choice(candidate_jmdict_ids)

def fetch_matching_uncommon_jmdict_ids(last_roma, used_ids, parent_span):
    jmdict_id = None
    with parent_span.span(name='fetch matching uncommon jmdict ids'):
        query = client.query(kind='UncommonJmDictIdsByFirstRomaji2')
        query.add_filter('first_romaji', '=', last_roma)
        results = list(query.fetch(limit=1))
        if not results:
            return None
        result = results[0]

        jmdict_ids = set(result['jmdict_ids'])
        candidate_jmdict_ids = list(jmdict_ids - used_ids)
        if not candidate_jmdict_ids:
            return None

        return random.choice(candidate_jmdict_ids)
