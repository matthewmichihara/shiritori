Shiritori
=========
A [Japanese word game](https://en.wikipedia.org/wiki/Shiritori) built with Flask/React and deployed to Google App Engine.

Setup
-----
```
virtualenv --python python3.7 .env
source .env/bin/activate
pip install -r requirements.txt
npm install
```

Local Development
-----------------
```
// Start the Flask dev server.
python main.py

// Start the Node dev server.
npm run start

// Test out the API.
curl 'http://localhost:5000/api/playword' -H 'Content-Type: application/json; charset=utf-8' --data-binary '{"input_word":"neko"}' --compressed
```

Deploy
------
```
// Build and deploy to App Engine.
npm run deploy
```

Populating the datastore
------------------------
This parses the dictionary file from https://www.edrdg.org/jmdict/j_jmdict.html and uploads to Cloud Datastore.
```
python jmdict_parser.py -f dictionary_files/JMdict_e.xml | GOOGLE_APPLICATION_CREDENTIALS=../Redmond-b4502b6fa7e9.json python uploader.py
```

Special Fields
--------------
Rank the following entities higher because they are more common according to dictionary files.
`news1, news2, ichi1, ichi2, spec1, spec2`
- There are roughly 11,000 news1 matches
- 10,000 news2
- 8,000 ichi1
- 17 ichi2
- 1000 spec1
- 2000 spec2 
- Total there are 180,499 words.
