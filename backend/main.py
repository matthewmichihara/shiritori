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

    word = input_json['input_word']
    attempting_to_match = input_json['attempting_to_match']

    word_roma = romkan.to_roma(word)
    word_kana = romkan.to_kana(word)
    attempting_to_match_roma = romkan.to_roma(attempting_to_match)

    first_kana = word_kana[0]
    last_kana = word_kana[-1]

    # Back to romaji. Using this as a tokenizer.
    first_roma = romkan.to_roma(first_kana)
    last_roma = romkan.to_roma(last_kana)

    # Check that word matches ending of previous word and
    # that it is a valid word TODO
    your_word = Word.query(Word.romaji == word_roma).get()
    word_matches = attempting_to_match_roma == first_roma
    
    if your_word is None or not word_matches:
        resp = jsonify({
            'response_type': 'INVALID_INPUT_WORD',
            'debug': {
                'your_word': your_word.to_dict(),
                'attempting_to_match_roma': attempting_to_match_roma,
                'first_roma': first_roma
            }
        });
        resp.response_code = 200;
        return resp;

    # Pass up all already used vocab ids.
    used_ids = set(input_json.get('used_ids', []))

    opponent_words = Word.query(Word.first_romaji == last_roma).fetch(limit=300)
    # Filter out the vocabs we've already seen and turn these model objects into
    # dicts that can be jsonified.
    valid_words = [w for w in opponent_words if w.id not in used_ids]

    resp = None
    if valid_words:
        opponent_word = random.choice(valid_words)
        need_to_match = opponent_word.last_romaji

        resp = jsonify({
            'response_type': 'SUCCESS',
            'need_to_match': need_to_match,
            'your_word': your_word.to_dict(),
            'opponent_word': opponent_word.to_dict()
        });
    else:
        resp = jsonify({
            'response_type': 'NO_MORE_WORDS',
            'your_word': your_word.to_dict()
        });

    resp.response_code = 200
    return resp

if __name__ == '__main__':
    app.run()
