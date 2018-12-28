import React from 'react';
import '../index.css';

class Education extends React.Component {
  render() {
    return (
      <div className='education'>
        <p>Try typing in a Japanese word above like 'neko'.</p>
        <p><a href="https://en.wikipedia.org/wiki/Shiritori">Shiritori</a> (しりとり) is a Japanese word game in which the players are required to say a word which begins with the final kana of the previous word.</p>
      </div>
    );
  }
}

export default Education;
