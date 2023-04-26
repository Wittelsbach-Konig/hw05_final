from django.contrib import admin

from .models import Group, Post

MAX_MESS_SIZE = 30  # Максимальный размер выводимого текста, при создании поста


class PostAdmin(admin.ModelAdmin):
    """Класс пост-админ
    Интерфейс администратора для списка постов"""

    list_display = ('pk',
                    'text',
                    'pub_date',
                    'author',
                    'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'

    def __str__(self) -> str:
        return self.text[:MAX_MESS_SIZE]


class GroupAdmin(admin.ModelAdmin):
    """Класс групп-админ
    Интерфейс администратора для списка групп"""

    list_display = ('pk',
                    'title',
                    'slug',
                    'description')
    search_fields = ('title',)
    list_filter = ('title',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
