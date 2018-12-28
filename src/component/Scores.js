import React from 'react';
import '../index.css';

class Scores extends React.Component {
  render() {
    return (
      <span className='scores'>Current: {this.props.current} Best: {this.props.best}</span>
    );
  }
}

export default Scores;
