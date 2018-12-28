from flask import jsonify

def base_response(response_type, raw_input_word, should_match, used_ids, your_word=None, opponent_word=None):
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

def word_not_found_response(raw_input_word, should_match, used_ids):
    return base_response(
        response_type='INPUT_WORD_NOT_FOUND',
        raw_input_word=raw_input_word,
        should_match=should_match,
        used_ids=used_ids
    )

def word_does_not_match_previous_ending_response(raw_input_word, should_match, used_ids, your_word):
    return base_response(
        response_type='INPUT_WORD_DOES_NOT_MATCH_PREVIOUS_ENDING',
        raw_input_word=raw_input_word,
        should_match=should_match,
        used_ids=used_ids,
        your_word=your_word
    )

def word_already_used_response(raw_input_word, should_match, used_ids, your_word):
    return base_response(
        response_type='INPUT_WORD_ALREADY_USED',
        raw_input_word=raw_input_word,
        should_match=should_match,
        used_ids=used_ids,
        your_word=your_word
    )

def no_more_words_response(raw_input_word, should_match, used_ids, your_word):
    return base_response(
        response_type='NO_MORE_WORDS',
        raw_input_word=raw_input_word,
        should_match=should_match,
        used_ids=used_ids,
        your_word=your_word
    )

def success_response(raw_input_word, should_match, used_ids, your_word, opponent_word):
    return base_response(
        response_type='SUCCESS',
        raw_input_word=raw_input_word,
        should_match=should_match,
        used_ids=used_ids,
        your_word=your_word,
        opponent_word=opponent_word
    )
