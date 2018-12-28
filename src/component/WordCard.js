import React from 'react';
import '../index.css';

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
          <a className='jisho_link' href={"https://jisho.org/search/" + this.props.kana}>
            {this.get_formatted_japanese(this.props.kanji, this.props.kana)} <span className='romaji'>{this.props.romaji}</span>: {this.props.english}
          </a>
        </span>
      </div>
    )
  }
}

export default WordCard;
