from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from google.appengine.ext import ndb
import romkan
import random

app = Flask(__name__)

# CORS is so stupid.
#CORS(app, origins=['*'])
CORS(app, resources={r"/api/*": {"origins": "*"}})

class Vocabulary(ndb.Model):
    # Include the entity id in here.
    id = ndb.ComputedProperty(lambda self: self.key.id())
    kana = ndb.StringProperty()
    kanji = ndb.StringProperty()
    romaji = ndb.StringProperty()
    english = ndb.StringProperty()
    first = ndb.StringProperty()
    last = ndb.StringProperty()

@app.route('/')
def hello():
    return "hellllloooooooooooooooooooooooooooooooooo world!"

@app.route('/api/random')
def random_words():
    vocab_list = Vocabulary.query().fetch()

    kanas = [v.kana for v in vocab_list]

    return 'kanas: {}'.format(kanas)

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
    your_word = Vocabulary.query(Vocabulary.romaji == word_roma).get()
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

    opponent_words = Vocabulary.query(Vocabulary.first == last_kana).fetch()
    # Filter out the vocabs we've already seen and turn these model objects into
    # dicts that can be jsonified.
    valid_words = [w for w in opponent_words if w.id not in used_ids]

    resp = None
    if valid_words:
        opponent_word = random.choice(valid_words)
        need_to_match = opponent_word.last

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
