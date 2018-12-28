import React from 'react';
import '../index.css';
import Education from './Education';
import WordCard from './WordCard';
import Scores from './Scores';
import post from '../logic/http';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      response_type: 'SUCCESS',
      search_text: '',
      word_history: [],
      my_turn: true,
      should_match: '',
      error_message: null,
      used_ids: [],
      current_score: 0,
      best_score: 0
    };
  }

  updateSuccess(response_type, word, used_ids) {
    const word_history = [ word, ...this.state.word_history ];

    const updateScores = (current, best) => {
      if (!this.state.my_turn) {
        return {current: current, best: best};
      }
      const new_current = current + 1;
      return {current: new_current, best: Math.max(new_current, best)};
    };

    const new_scores = updateScores(this.state.current_score, this.state.best_score);

    // Update local storage.
    localStorage.setItem('best_score', new_scores.best);

    this.setState({
      response_type: response_type,
      search_text: '',
      word_history: word_history,
      my_turn: !this.state.my_turn,
      should_match: word.last_romaji,
      error_message: null,
      used_ids: used_ids,
      current_score: new_scores.current,
      best_score: new_scores.best
    });
  }

  updateError(response_type, raw_input_word, should_match, used_ids) {
    this.setState({
      response_type: response_type,
      should_match: should_match,
      error_message: this.get_error_message(response_type, raw_input_word, should_match),
      used_ids: used_ids
    });
  }
  
  updateSearchText(search_text) {
    this.setState({search_text: search_text});
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

  handleChange(e) {
    this.updateSearchText(e.target.value);
  }

  handleKeyPress(e) {
    if (e.key !== 'Enter') {
      return;
    }

    this.updateSearchText('');

    const data = {
      'input_word': this.state.search_text,
      'should_match': this.state.should_match,
      'used_ids': this.state.used_ids
    };

    const url = this.props.apiUrl + '/playword';

    post(url, data)
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

  componentDidMount() {
    const best_score = localStorage.getItem('best_score')
    if (best_score !== null) {
      this.setState({best_score: best_score});
    }
  }

  render() {
    const word_cards = this.state.word_history.map(word => {
      return (
        <li key={word.id}>
          <WordCard kanji={word.kanji} kana={word.kana} romaji={word.romaji} english={word.english}/>
        </li>
      );
    });
    
    return (
      <div className='body'>
        <span><h1>Shiritori</h1> <Scores current={this.state.current_score} best={this.state.best_score} /></span>
        <input type='text' 
          className='searchbar'
          value={this.state.search_text}
          onChange={(e) => this.handleChange(e)}
          onKeyPress={(e) => this.handleKeyPress(e)}/>
        {this.state.error_message !== null && <div className='error'><span>{this.state.error_message}</span></div>}
        {this.state.word_history.length === 0 && <Education />}
        <ul>
          {word_cards}
        </ul>
      </div>
    );
  }
}

export default App;
