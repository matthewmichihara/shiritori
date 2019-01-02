from collections import namedtuple
from flask import Flask
from flask import request
from flask_cors import CORS
from google.cloud import datastore
from word import entity_to_word
from word import pick_your_word
from word import pick_opponent_word
from word import Word
from romaji_normalizer import normalize
import random
import responses
import romkan
from opencensus.trace.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.exporters import stackdriver_exporter
from opencensus.trace import tracer as tracer_module
from opencensus.trace.exporters.transports.background_thread import BackgroundThreadTransport
from opencensus.trace.tracers import noop_tracer
from opencensus.trace import config_integration

SHOULD_TRACE = True

app = Flask(__name__)

exporter = stackdriver_exporter.StackdriverExporter(
        project_id='redmond-211121',
        transport=BackgroundThreadTransport)

CORS(app, resources={r"/api/*": {"origins": "*"}})

client = datastore.Client()

@app.route('/')
def hello():
    return "Running"

@app.route('/api/playword', methods=['POST'])
def play_word():
    tracer = get_tracer(SHOULD_TRACE)
    
    with tracer.span(name='/api/playword') as play_word_span:
        input_json = request.get_json()

        raw_input_word = input_json['input_word']
        if raw_input_word:
            raw_input_word = raw_input_word.lower()
        print('raw_input_word: {}'.format(raw_input_word))

        # If this is None, match anything (first move).
        should_match = input_json.get('should_match')
        if not should_match:
            should_match = None
        print('should_match: {}'.format(should_match))

        used_ids = set(input_json.get('used_ids', []))
        print('used_ids: {}'.format(used_ids))

        word_roma = romkan.to_roma(raw_input_word)
        word_kana = romkan.to_kana(raw_input_word)
        should_match_roma = None
        if should_match is not None:
            should_match_roma = romkan.to_roma(should_match)
        print('word_roma: {} word_kana: {} should_match_roma: {}'.format(word_roma, word_kana, should_match_roma))

        first_kana = normalize(word_kana[0])
        last_kana = normalize(word_kana[-1])
        print('first_kana: {} last_kana: {}'.format(first_kana, last_kana))

        # Back to romaji. Using this as a tokenizer.
        first_roma = romkan.to_roma(first_kana)
        last_roma = romkan.to_roma(last_kana)
        print('first_roma: {} last_roma: {}'.format(first_roma, last_roma))

        your_word_entities = []
        with play_word_span.span(name='query_your_word') as query_your_word_span:
            # Check that input word is a valid Japanese word.
            query = client.query(kind='Word3')
            query.add_filter('romaji', '=', word_roma)
            your_word_results = list(query.fetch())
            your_word_entities = [entity_to_word(word) for word in your_word_results]
            print('num your_word_entities: {}'.format(len(your_word_entities)))

        if not your_word_entities:
            return responses.word_not_found_response(
                raw_input_word, 
                should_match_roma,
                used_ids
            )

        your_word = pick_your_word(your_word_entities)

        # Check that the word beginning matches the previous word ending.
        word_does_not_match = should_match_roma is not None and should_match_roma != first_roma
        if word_does_not_match:
            return responses.word_does_not_match_previous_ending_response(
                raw_input_word, 
                should_match_roma,
                used_ids,
                your_word
            )

        # Check that the word has not already been used.
        if your_word.id in used_ids:
            return responses.word_already_used_response(
                raw_input_word, 
                should_match_roma, 
                used_ids,
                your_word
            )

        opponent_word_entities = []
        with play_word_span.span(name='query_opponent_word') as query_opponent_word_span:
            query = client.query(kind='Word3')
            query.add_filter('first_romaji', '=', last_roma)
            opponent_words = list(query.fetch(limit=100))
            opponent_word_entities = [entity_to_word(word) for word in opponent_words]
        print('num opponent_word_entities: {}'.format(len(opponent_word_entities)))
        opponent_word = pick_opponent_word(opponent_word_entities, used_ids)

        if not opponent_word:
            return responses.no_more_words_response(
                raw_input_word,
                should_match_roma,
                used_ids,
                your_word
            )

        new_should_match_roma = opponent_word.last_romaji
        used_ids.add(your_word.id)
        used_ids.add(opponent_word.id)
        return responses.success_response(
            raw_input_word,
            new_should_match_roma,
            used_ids,
            your_word,
            opponent_word
        )

def get_tracer(should_trace):
    if (should_trace):
        return tracer_module.Tracer(exporter=exporter)
    return noop_tracer.NoopTracer()

if __name__ == '__main__':
    app.run()
