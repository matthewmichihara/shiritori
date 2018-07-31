from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from google.appengine.ext import ndb
import romkan
import random

app = Flask(__name__)

# CORS is so stupid.
CORS(app, resources={r"/api/*": {"origins": "*"}})

class Word(ndb.Model):
    # Include the entity id in here.
    id = ndb.ComputedProperty(lambda self: self.key.id())
    jmdict_id = ndb.IntegerProperty()
    kanji = ndb.StringProperty()
    kana = ndb.StringProperty()
    romaji = ndb.StringProperty()
    english = ndb.StringProperty()
    first_romaji = ndb.StringProperty()
    last_romaji = ndb.StringProperty()

def get_base_response(response_type, raw_input_word, should_match, used_ids, your_word=None, opponent_word=None):
    base_dict = {
        'response_type': response_type,
        'raw_input_word': raw_input_word,
        'should_match': should_match,
        'used_ids': list(used_ids)
    }

    if your_word is not None:
        base_dict['your_word'] = your_word.to_dict()

    if opponent_word is not None:
        base_dict['opponent_word'] = opponent_word.to_dict()

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

@app.route('/api/random')
def random_word():
    random_word = Word.query().get()
    return jsonify(random_word.to_dict())

@app.route('/api/playword', methods=['POST'])
def play_word():
    input_json = request.get_json()

    raw_input_word = input_json['input_word']

    # If this is None, match anything (first move).
    should_match = input_json.get('should_match')
    if not should_match:
        should_match = None

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
    your_word = Word.query(Word.romaji == word_roma).get()
    if your_word is None:
        return get_word_not_found_response(
            raw_input_word, 
            should_match_roma,
            used_ids
        )

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
    used_ids = set(input_json.get('used_ids', []))
    if your_word.id in used_ids:
        return get_word_already_used_response(
            raw_input_word, 
            should_match_roma, 
            used_ids,
            your_word
        )

    opponent_words = Word.query(Word.first_romaji == last_roma).fetch(limit=300)
    valid_opponent_words = []
    for word in opponent_words:
        if word.id in used_ids:
            continue
        if word.last_romaji == 'n':
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
