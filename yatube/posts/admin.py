from django.contrib import admin

from .models import Comment, Follow, Group, Post

MAX_MESS_SIZE = 30  # Максимальный размер выводимого текста, при создании поста


class PostAdmin(admin.ModelAdmin):
    """
    Класс пост-админ
    Интерфейс администратора для списка постов.
    """

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
    """
    Класс групп-админ
    Интерфейс администратора для списка групп.
    """

    list_display = ('pk',
                    'title',
                    'slug',
                    'description')
    search_fields = ('title',)
    list_filter = ('title',)


class FollowAdmin(admin.ModelAdmin):
    """
    Класс подписка-админ
    Интерфейс администратора для списка подписок.
    """

    list_display = ('pk',
                    'user',
                    'author',)
    search_fields = ('user',)
    list_filter = ('user',)


class CommentAdmin(admin.ModelAdmin):
    """
    Класс подписка-админ
    Интерфейс администратора для списка подписок.
    """

    list_display = ('pk',
                    'post',
                    'author',
                    'text',)
    search_fields = ('text',)
    list_filter = ('text',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Comment, CommentAdmin)
