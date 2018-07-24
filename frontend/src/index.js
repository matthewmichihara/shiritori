import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      vocab_cards: []
    };
  }

  handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      const data = {
        'word': e.target.value,
        'first_needs_to_match': 'asdf'
      };

      const data1 = {
          "name": "matt",
          "job": "dev"
        };

      const url1 = "https://reqres.in/api/users"
      const url = "https://redmond-211121.appspot.com/nextwords"

      postData(url, data)
        .then(data => alert(JSON.stringify(data)));
    }
  }

  render() {
    return (
      <div id='body'>
        <h1>Play Shiritori</h1>
        <input type='text' onKeyPress={this.handleKeyPress}/>
      </div>
    )
  }
}

class VocabCard extends React.Component {
  render() {
    return (
      <div id='vocab_card'>
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

