from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from google.appengine.ext import ndb
import romkan
import random

app = Flask(__name__)

# CORS is so stupid.
CORS(app, origins=['*'])

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

@app.route('/random')
def random_words():
    vocab_list = Vocabulary.query().fetch()

    kanas = [v.kana for v in vocab_list]

    return 'kanas: {}'.format(kanas)

@app.route('/nextwords', methods=['POST'])
def next_words():
    input_json = request.get_json()

    word = input_json['word']
    first_needs_to_match = input_json['first_needs_to_match']
    kana = romkan.to_kana(word)
    first = kana[0]
    last = kana[-1]

    # TODO: check validity of word.

    # Pass up all already used vocab ids.
    used_ids = set(input_json.get('used_ids', []))

    vocabs = Vocabulary.query(Vocabulary.first == last).fetch()
    # Filter out the vocabs we've already seen and turn these model objects into
    # dicts that can be jsonified.
    valid_vocabs = [v for v in vocabs if v.id not in used_ids]

    resp = None
    if vocabs:
        vocab = random.choice(valid_vocabs)
        resp = jsonify(vocab.to_dict())
    else:
        error_dict = {"error": "No more words!"}
        resp = jsonify(error_dict)

    resp.response_code = 200
    return resp

if __name__ == '__main__':
    app.run()
