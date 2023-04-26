from django.forms import ModelForm, ValidationError

from obsceneLang.utils import (get_banned_words, get_words_from_text,
                               has_bad_words)

from .models import Post, Comment, Follow


class PostForm(ModelForm):
    """PostForm
    форма для создания постов. Поля формы:
        text,
        group (необзятально),
    """
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        help_texts = {
            'group': 'Выберите группу',
            'text': 'Введите текст',
            'image': 'Вставьте картинку',
        }

    def clean_text(self):
        """Валидация формы."""
        data = self.cleaned_data['text']
        text = get_words_from_text(data)
        if has_bad_words(text, get_banned_words()):
            raise ValidationError(
                "Использование запрещенных слов не допустимо. "
                "Ну и ну вы разочаровали партию. "
                "-10000 социального рейтинга."
            )
        return data


class CommentForm(ModelForm):
    """CommentForm
    Форма для создания комментариев. Поля формы:
        text
    """

    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {'text': 'Текст комментария'}


class FollowForm(ModelForm):
    """FollowForm
    Форма для подписки на авторов. Поля формы:
        user
    """

    class Meta:
        model = Follow
        labels = {'user': 'Подписка на:', 'author': 'Автор записи'}
        fields = ('user',)
