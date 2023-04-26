from typing import Set

from .models import BannedWord


def get_banned_words() -> Set[str]:
    """Получить множество нецензурных слов."""
    bad_words = ({w.lower() for w in
                  BannedWord.objects.values_list('banned_word', flat=True)})
    return bad_words


def get_words_from_text(text_string: str) -> Set[str]:
    """Получить множество слов из текста."""
    return {w for w in text_string.lower().split()}


def has_bad_words(set_string: Set[str], bad_words_set: Set[str]) -> bool:
    """Определить пересекается ли множество bad_words_set с set_string."""
    return bool(bad_words_set & set_string)
