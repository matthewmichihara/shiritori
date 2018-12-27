from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from google.cloud import datastore
from collections import namedtuple
import romkan
import random

app = Flask(__name__)

# CORS is so stupid.
CORS(app, resources={r"/api/*": {"origins": "*"}})

Word = namedtuple('Word', 'id jmdict_id kanji kana romaji english first_romaji last_romaji')

def entity_to_word(entity):
    word = Word(
        entity.key.id,
        entity['jmdict_id'],
        entity['kanji'],
        entity['kana'],
        entity['romaji'],
        entity['english'],
        entity['first_romaji'],
        entity['last_romaji']
    )

    return word

def get_base_response(response_type, raw_input_word, should_match, used_ids, your_word=None, opponent_word=None):
    base_dict = {
        'response_type': response_type,
        'raw_input_word': raw_input_word,
        'should_match': should_match,
        'used_ids': list(used_ids)
    }

    if your_word is not None:
        base_dict['your_word'] = your_word._asdict()

    if opponent_word is not None:
        base_dict['opponent_word'] = opponent_word._asdict()

    return jsonify(base_dict)

def get_word_not_found_response(raw_input_word, should_match, used_ids):
    return get_base_response(
        response_type='INPUT_WORD_NOT_FOUND',
        raw_input_word=raw_input_word,
        should_match=should_match,
        used_ids=used_ids
    )

def get_word_does_not_match_previous_ending_response(raw_input_word, should_match, used_ids, your_word):
    return get_base_response(
        response_type='INPUT_WORD_DOES_NOT_MATCH_PREVIOUS_ENDING',
        raw_input_word=raw_input_word,
        should_match=should_match,
        used_ids=used_ids,
        your_word=your_word
    )

def get_word_already_used_response(raw_input_word, should_match, used_ids, your_word):
    return get_base_response(
        response_type='INPUT_WORD_ALREADY_USED',
        raw_input_word=raw_input_word,
        should_match=should_match,
        used_ids=used_ids,
        your_word=your_word
    )

def get_no_more_words_response(raw_input_word, should_match, used_ids, your_word, opponent_word):
    return get_base_response(
        response_type='NO_MORE_WORDS',
        raw_input_word=raw_input_word,
        should_match=should_match,
        used_ids=used_ids,
        your_word=your_word
    )

def get_success_response(raw_input_word, should_match, used_ids, your_word, opponent_word):
    return get_base_response(
        response_type='SUCCESS',
        raw_input_word=raw_input_word,
        should_match=should_match,
        used_ids=used_ids,
        your_word=your_word,
        opponent_word=opponent_word
    )

@app.route('/')
def hello():
    return "Running"

@app.route('/api/playword', methods=['POST'])
def play_word():
    client = datastore.Client()

    input_json = request.get_json()

    raw_input_word = input_json['input_word']
    if raw_input_word:
        raw_input_word = raw_input_word.lower()

    # If this is None, match anything (first move).
    should_match = input_json.get('should_match')
    if not should_match:
        should_match = None

    used_ids = set(input_json.get('used_ids', []))

    word_roma = romkan.to_roma(raw_input_word)
    word_kana = romkan.to_kana(raw_input_word)
    should_match_roma = None
    if should_match is not None:
        should_match_roma = romkan.to_roma(should_match)

    first_kana = word_kana[0]
    last_kana = word_kana[-1]

    # Back to romaji. Using this as a tokenizer.
    first_roma = romkan.to_roma(first_kana)
    last_roma = romkan.to_roma(last_kana)

    # Check that input word is a valid Japanese word.
    query = client.query(kind='Word')
    query.add_filter('romaji', '=', word_roma)
    your_word_results = list(query.fetch())

    if not your_word_results:
        return get_word_not_found_response(
            raw_input_word, 
            should_match_roma,
            used_ids
        )

    your_word = entity_to_word(your_word_results[0])

    # Check that the word beginning matches the previous word ending.
    word_does_not_match = should_match_roma is not None and should_match_roma != first_roma
    if word_does_not_match:
        return get_word_does_not_match_previous_ending_response(
            raw_input_word, 
            should_match_roma,
            used_ids,
            your_word
        )

    # Check that the word has not already been used.
    if your_word.id in used_ids:
        return get_word_already_used_response(
            raw_input_word, 
            should_match_roma, 
            used_ids,
            your_word
        )

    query = client.query(kind='Word')
    query.add_filter('first_romaji', '=', last_roma)
    opponent_words = list(query.fetch(limit=300))
    valid_opponent_words = []
    for word_entity in opponent_words:
        word = entity_to_word(word_entity)
        if word.id in used_ids:
            continue
        if word.last_romaji in ('n', '-'):
            continue
        valid_opponent_words.append(word)

    if not valid_opponent_words:
        return get_no_more_words_response(
            raw_input_word,
            should_match_roma,
            used_ids,
            your_word
        )

    opponent_word = random.choice(valid_opponent_words)
    new_should_match_roma = opponent_word.last_romaji
    used_ids.add(your_word.id)
    used_ids.add(opponent_word.id)
    return get_success_response(
        raw_input_word,
        new_should_match_roma,
        used_ids,
        your_word,
        opponent_word
    )

if __name__ == '__main__':
    app.run()
