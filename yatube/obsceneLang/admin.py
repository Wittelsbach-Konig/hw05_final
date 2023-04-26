from django.contrib import admin

from .models import BannedWord

MAX_MESS_SIZE = 30  # Максимальный размер выводимого текста


class BannedWordAdmin(admin.ModelAdmin):
    """ Интерфейс администратора для списка обсценной лексики. """

    list_display = (
        'pk',
        'banned_word',
        'word_type',
        'comments',
    )
    search_fields = (
        'banned_word',
    )
    list_filter = ('word_type',)
    list_editable = ('word_type',)
    empty_value_display = '-пусто-'

    def __str__(self) -> str:
        return self.banned_word[:MAX_MESS_SIZE]


admin.site.register(BannedWord, BannedWordAdmin)
