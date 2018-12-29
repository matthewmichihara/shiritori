import React from 'react';
import { List, Transition } from 'semantic-ui-react';
import './word_list.css'

const WordList = ({words}) => {
  /**
   * Returns a furigana'd japanese string with first and last characters span'd. If
   * there is only one character, just span that one.
   */
  const formatted_japanese = (kanji, kana) => {
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
  };

  const formatted_romaji = (romaji, first_romaji, last_romaji) => {
    // It's a one syllable string.
    if (romaji.length === first_romaji.length) {
      return (
        <span className='japanese'>
          <span className='kana_boundary'>{romaji}</span>
        </span>
      );
    }

    const middle = romaji.substring(first_romaji.length, romaji.length - last_romaji.length);
    return (
      <span className='japanese'>
        <span className='kana_boundary'>{first_romaji}</span>
        {middle}
        <span className='kana_boundary'>{last_romaji}</span>
      </span>
    );
  };

  return (
    <Transition.Group as={List} animated animation='fly right' duration={500} divided size='huge' relaxed='very' verticalAlign='middle'>
      {words.map(word => (
        <List.Item key={word.id}>
          <List.Content>
            <a className='jisho_link' href={"https://jisho.org/search/" + word.kana}>
              {formatted_japanese(word.kanji, word.kana)} <span className='romaji'>
                [{formatted_romaji(word.romaji, word.first_romaji, word.last_romaji)}]
              </span> - "{word.english}"
            </a>
          </List.Content>
        </List.Item>
      ))}
    </Transition.Group>
  );
};

export default WordList
