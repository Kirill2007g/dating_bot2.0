import re
TLDS = (
    "com|net|org|info|biz|xyz|top|club|site|online|link|app|dev|co|tv|cc|io|me|"
    "ru|ua|by|kz|su|pw|tk|ml|ga|cf|gq|ly|gg|dog|рф|укр"
)
SOCIALS = "instagram|insta|inst|инстаграм|инста|инст"


LINK_PATTERNS = [
    re.compile(r"""
    \b              # Граница слова (а не начало! Конец слова тоже проверяется через \b)
    (?:             # Незапоминающая группа (выключает захват в match.groups() и работает быстрее)
    http|ftp|tg|ws) # Одно из указанных начал протокола
    s?              # Буква 's' может встречаться 0 или 1 раз (для https, ftps и т.д.)
    ://             # Буквальные символы ://
    \S+             # Один или более символов (Кроме пробельного символа)
    """, re.IGNORECASE | re.VERBOSE),
    re.compile(r"""
    \b              # Граница слова
    www             # Буквально www
    \.              # Буквально точка
    \S+             # Один или более символов (Кроме пробельного символа)
    """, re.IGNORECASE | re.VERBOSE),
    re.compile(rf"""
    \b              # Граница слова
    [\w-]+          # \w = буква/цифра/_ включая кириллицу и дефис, + =1 и больше
    (?:\.[\w-]+)*   # 0 или больше повторов "точка + слово"
    \.              # точка
    (?:{TLDS})      # одна из зон com|net...
    \b              # зона заканчивается на границе слова
    (?:/\S*)?       # необяз хвост / + любые не проблемы *=0 или больше
    """, re.IGNORECASE | re.VERBOSE),
    re.compile(r"""
    (?<![\w@])      # lookbehind не должно быть набора символов: букв|цифра|_|@
    @               # Граница слова
    [a-z]           #первый символ буква по правилам telegram
    [a-z0-9_]{4,31} # от 4до 31 символов буквы , цифры , _
    \b              # конец слова
    """, re.IGNORECASE | re.VERBOSE)

]
SOCIAL_PATTERNS = [
    re.compile(rf"""
        \b                  # начало слова
        (?:{SOCIALS})       # любое из слов
        \b                  # конец слова
    """, re.IGNORECASE | re.VERBOSE),
    re.compile(r"\b[\w.]+@[a-z0-9]+\.[a-z0-9.-]+\b", re.IGNORECASE)
]


