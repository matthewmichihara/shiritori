# Setup
1. `virtualenv --python python2 .env`
2. `source .env/bin/activate`
3. `pip install -t lib -r requirements.txt`
4. `gcloud app deploy`

# API
/api/playword

# Request
{
  'input_word': 'aka',
  'attempting_to_match': 'あ',
  'used_ids': [
    12345,
    22222
  ]
}
  
# Response
{
  'response_type': 'SUCCESS' | 'INVALID_INPUT_WORD' | 'NO_MORE_WORDS'

  'need_to_match': 'た',

  'your_word': {
    'id': 1234,
    'kanji': '赤',
    'kana': 'あか',
    'english': 'red',
    'first': 'あ',
    'last': 'か'
  },

  'opponent_word': {
    'id': 22222,
    'kanji': null,
    'kana': 'かた',
    'english': 'person',
    'first': 'か',
    'last': 'た'
  }
}
 

