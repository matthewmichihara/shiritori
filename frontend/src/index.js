import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

const API_URL = 'https://redmond-211121.appspot.com/api'

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      word_history: [],
      my_turn: true,
      should_match: ''
    };
  }

  handleKeyPress = (e) => {
    if (e.key !== 'Enter') {
      return;
    }

    const data = {
      'input_word': e.target.value,
      'should_match': this.state.should_match
    };

    const url = API_URL + '/playword'

    postData(url, data)
      .then(resp_json => {
        const response_type = resp_json.response_type
        if (response_type !== 'SUCCESS') {
          return;
        }

        const your_word = resp_json.your_word;
        const opponent_word = resp_json.opponent_word;
        const word_history = [ opponent_word, your_word, ...this.state.word_history ];
        this.setState({
          word_history: word_history,
          my_turn: this.state.my_turn, // TODO this makes no sense.
          should_match: opponent_word.last_romaji
        });
      });
  }

  render() {
    const word_cards = this.state.word_history.map(word => {
      return (
        <li key={word.id}>
          <WordCard kanji={word.kanji} kana={word.kana} english={word.english}/>
        </li>
      );
    });

    return (
      <div id='body'>
        <h1>Play Shiritori</h1>
        <input type='text' onKeyPress={this.handleKeyPress}/>
        <ul>
          {word_cards}
        </ul>
      </div>
    )
  }
}

class WordCard extends React.Component {
  format(kana, kanji, english) {
    if (kanji) {
      return kana + " (" + kanji + "): " + english;
    }

    return kana + ": " + english;
  }

  render() {
    return (
      <div className='word_card'>
        <p>{this.format(this.props.kana, this.props.kanji, this.props.english)}</p>
        <p>Kanji: {this.props.kanji}</p>
        <p>Kana: {this.props.kana}</p>
        <p>English: {this.props.english}</p>
      </div>
    )
  }
}

const postData = (url = '', data = {}) => {
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json; charset=utf-8'
    },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .catch(error => console.error('fetch error', error));
}

ReactDOM.render(<App />, document.getElementById('root'));

