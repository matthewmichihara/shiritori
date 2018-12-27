import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

const API_URL = 'https://redmond-211121.appspot.com/api'

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      response_type: 'SUCCESS',
      word_history: [],
      my_turn: true,
      should_match: '',
      error_message: null
    };
  }

  updateSuccess(response_type, word, used_ids) {
    const word_history = [ word, ...this.state.word_history ];
    this.setState({
      response_type: response_type,
      word_history: word_history,
      error_message: null,
      my_turn: !this.state.my_turn,
      should_match: word.last_romaji,
      used_ids: used_ids
    });
  }

  updateError(response_type, raw_input_word, should_match, used_ids) {
    this.setState({
      response_type: response_type,
      word_history: this.state.word_history,
      error_message: this.get_error_message(response_type, raw_input_word, should_match),
      my_turn: this.state.my_turn,
      should_match: should_match,
      used_ids: used_ids
    });
  }

  get_error_message(response_type, raw_input_word, should_match) {
    switch(response_type) {
      case 'SUCCESS':
        return null;
      case 'INPUT_WORD_NOT_FOUND':
        return "I don't think '" + raw_input_word + "' is a valid Japanese word.";
      case 'INPUT_WORD_DOES_NOT_MATCH_PREVIOUS_ENDING':
        return "'" + raw_input_word + "' needs to begin with '" + should_match + "'";
      case 'INPUT_WORD_ALREADY_USED':
        return "'" + raw_input_word + "' was already used!";
      case 'NO_MORE_WORDS':
        // TODO fix this, this is a win condition.
        return 'There are no more words!';
      default:
        return 'Something went wrong.';
    }
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

    const url = API_URL + '/playword';

    postData(url, data)
      .then(resp_json => {
        const response_type = resp_json.response_type;
        const raw_input_word = resp_json.raw_input_word;
        const should_match = resp_json.should_match;
        const your_word = resp_json.your_word;
        const opponent_word = resp_json.opponent_word;
        const used_ids = resp_json.used_ids;

        if (response_type === 'SUCCESS') {
          this.updateSuccess(response_type, your_word, used_ids);
          setTimeout(() => this.updateSuccess(response_type, opponent_word, used_ids), 500);
        } else {
          this.updateError(response_type, raw_input_word, should_match, used_ids);
        }
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
        {this.state.error_message !== null && <div className='error'><span>{this.state.error_message}</span></div>}
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

