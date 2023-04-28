from django.core.validators import MaxLengthValidator
from django.db import models

MAX_WORD_SIZE = 50  # Максимальный размер нецензурного слова
MAX_COMMENTS_SIZE = 75  # Максимальный размер комментария


class BannedWord(models.Model):
    """ Модель слов обсценной лексики. """

    banned_word = models.CharField('Запрещенное слово',
                                   max_length=MAX_WORD_SIZE,
                                   unique=True)
    word_type = models.CharField('Тип слова',
                                 max_length=MAX_WORD_SIZE)
    comments = models.TextField(
        'Комментарий',
        blank=True,
        validators=[MaxLengthValidator(MAX_COMMENTS_SIZE)]
    )

    class Meta:
        ordering = ('banned_word',)
        verbose_name = 'Запрещенное слово'
        verbose_name_plural = 'Запрещенные слова'
