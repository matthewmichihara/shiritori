from flask import Flask
from flask import request
from flask import jsonify
from google.appengine.ext import ndb

app = Flask(__name__)

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
def random():
    vocab_list = Vocabulary.query().fetch()

    kanas = [v.kana for v in vocab_list]

    return 'kanas: {}'.format(kanas)

@app.route('/nextword', methods=['POST'])
def next_word():
    input_json = request.get_json()

    last = input_json['last']

    # Pass up all already used vocab ids.
    used_ids = set(input_json.get('used_ids', []))

    vocabs = Vocabulary.query(Vocabulary.last == last).fetch()

    # Filter out the vocabs we've already seen and turn these model objects into
    # dicts that can be jsonified.
    vocab_dicts = [v.to_dict() for v in vocabs if v.id not in used_ids]
        
    resp = jsonify(vocab_dicts)
    resp.response_code = 200
    return resp

if __name__ == '__main__':
    app.run()
