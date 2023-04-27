from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

MAX_LEN_TO_STR = 200  # Максимальный размер строки
User = get_user_model()


class Group(models.Model):
    """Модель групп
    Атрибуты:
        title : Название
        slug : Уникальный фрагмент URL
        description : Описание
    """

    title = models.CharField('Название',
                             max_length=MAX_LEN_TO_STR,
                             help_text='Введите название группы')
    slug = models.SlugField('Уникальный фрагмент URL',
                            unique=True)
    description = models.TextField('Описание')

    class Meta:
        ordering = ('title',)
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return self.title[:MAX_LEN_TO_STR]


class Post(CreatedModel):
    """Модель постов
    Атрибуты:
        text : Текст
        pub_date : Дата публикации
        author : Автор
        group : Группа
    """

    text = models.TextField('Текст',
                            help_text='Введите текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет отсносится пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:MAX_LEN_TO_STR]


class Comment(CreatedModel):
    """Модель комментариев
    Атрибуты:
        post : Пост
        author : Автор
        text : Текст
        created : Группа
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name='Автор'
    )
    text = models.TextField('Текст',
                            help_text='Введите текст комментария')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text[:MAX_LEN_TO_STR]


class Follow(models.Model):
    """Модель подписки
    Атрибуты:
        user : Пользователь
        author : Автор
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        get_latest_by = ['author']
