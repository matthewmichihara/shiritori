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

  updateState(word, used_ids) {
    const word_history = [ word, ...this.state.word_history ];
    this.setState({
      word_history: word_history,
      my_turn: !this.state.my_turn,
      should_match: word.last_romaji,
      used_ids: used_ids
    });
  }

  handleKeyPress(e) {
    if (e.key !== 'Enter') {
      return;
    }

    const data = {
      'input_word': e.target.value,
      'should_match': this.state.should_match,
      'used_ids': this.state.used_ids
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
        const used_ids = resp_json.used_ids;

        this.updateState(your_word, used_ids);
        setTimeout(() => this.updateState(opponent_word, used_ids), 500);
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
      <div className='body'>
        <h1>Play Shiritori</h1>
        <input type='text' className='searchbar' onKeyUp={(e) => this.handleKeyPress(e)}/>
        <ul>
          {word_cards}
        </ul>
      </div>
    )
  }
}

class WordCard extends React.Component {
  /**
   * Returns a furigana'd japanese string with first and last characters span'd. If
   * there is only one character, just span that one.
   */
  get_formatted_japanese(kanji, kana) {
    const len = kana.length;
    const first = kana[0];
    const middle = kana.substr(1, kana.length-2);
    const last = kana.slice(-1);

    if (kanji) {
      if (len === 1) {
        return (
          <span className='japanese'>
            <ruby>
              <rb>{kanji}</rb>
              <rt>
                <span className='kana_boundary'>{kana}</span>
              </rt>
            </ruby>
          </span>
        )
      }

      return (
        <span className='japanese'>
          <ruby>
            <rb>{kanji}</rb>
            <rt>
              <span className='kana_boundary'>{first}</span>
              {middle}
              <span className='kana_boundary'>{last}</span>
            </rt>
          </ruby>
        </span>
      )
    } else {
      if (len === 1) {
        return (
          <span className='japanese'>
            <span className='kana_boundary'>
              {kana}
            </span>
          </span>
        )
      }

      return (
        <span className='japanese'>
          <span className='kana_boundary'>{first}</span>
          {middle}
          <span className='kana_boundary'>{last}</span>
        </span>
      )
    }
  }

  render() {
    return (
      <div className='word_card'>
        <span className='word_line'>
          {this.get_formatted_japanese(this.props.kanji, this.props.kana)}: {this.props.english}
        </span>
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

