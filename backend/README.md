# Setup
1. `virtualenv --python python3.7 .env`
2. `source .env/bin/activate`
3. `pip install -r requirements.txt`
4. `gcloud app deploy --project redmond-211121 --version 1`

# Populating the datastore
1. `python jmdict_parser.py -f JMdict_e.xml | GOOGLE_APPLICATION_CREDENTIALS=../../Redmond-b4502b6fa7e9.json python uploader.py`

# API
- `/api/playword`

# Example curl
```
curl 'https://redmond-211121.appspot.com/api/playword' -H 'Content-Type: application/json; charset=utf-8' --data-binary '{"input_word":"dashi","should_match":"da"}' --compressed | python -m json.tool
```

# Request
```
{
  'input_word': 'aka',
  'should_match': 'あ',
  'used_ids': [
    12345,
    22222
  ]
}
```
  
# Response
```
{
  'response_type': 'SUCCESS' | 'INVALID_INPUT_WORD' | 'NO_MORE_WORDS' | ...

  'should_match': 'た',

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
```

# Special datastore fields
Rank the following entities higher because they are more common according to dictionary files.
news1, news2, ichi1, ichi2, spec1, spec2
- There are roughly 11,000 news1 matches
- 10,000 news2
- 8,000 ichi1
- 17 ichi2
- 1000 spec1
- 2000 spec2 
- Total there are 180,499 words.
