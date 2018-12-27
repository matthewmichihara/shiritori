# Use the "big"(?) version of the small characters so that romkan doesn't prepend an 'x'.
NORMALIZE_DICT = {
    u"ぁ":u"あ",
    u"ぃ":u"い",
    u"ぅ":u"う",
    u"ぇ":u"え",
    u"ぉ":u"お",
    u"ゃ":u"や",
    u"ゅ":u"ゆ",
    u"ょ":u"よ",
    u"っ":u"つ",
    u"ァ":u"ア",
    u"ィ":u"イ",
    u"ゥ":u"ウ",
    u"ェ":u"エ",
    u"ォ":u"オ",
    u"ャ":u"ヤ",
    u"ュ":u"ユ",
    u"ョ":u"ヨ",
    u"ッ":u"ツ"
}

def normalize(kana):
    return NORMALIZE_DICT.get(kana, kana)
