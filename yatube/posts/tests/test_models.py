from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import MAX_LEN_TO_STR, Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    """Класс для тестирования моделей Post."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создаём экземпляр Post для теста"""
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name',
                                            email='test@yandex.ru',
                                            password='test_pass',),
            text='Тестовая запись для тестового поста.',
        )

    def test_models_have_correct_object_names(self):
        """Тестирование __str__ объекта Post"""
        post = PostModelTest.post
        expected_object_name = post.text[:MAX_LEN_TO_STR]
        self.assertEqual(
            expected_object_name,
            str(post),
            f'Метод str для {post}, работает не верно'
        )

    def test_help_text(self):
        """Тестирование help_text объекта Post"""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет отсносится пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text,
                    expected,
                    f'Параметр help_text у {value} неправильный'
                )

    def test_verbose_name(self):
        """Тестирование verbose_name объекта Post"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name,
                    expected,
                    f'Не правильные verboses объекта {post}'
                )


class GroupModelTest(TestCase):
    """Класс для тестирования моделей Group."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создаём экземпляр Group для теста"""
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        """Тестирование __str__ объекта Group"""
        group = GroupModelTest.group
        expected_object_name = group.title[:MAX_LEN_TO_STR]
        self.assertEqual(
            expected_object_name,
            str(group),
            f'Метод str для {group}, работает не верно'
        )

    def test_help_text(self):
        """Тестирование help_text объекта Group"""
        group = GroupModelTest.group
        expected = 'Введите название группы'
        self.assertEqual(
            group._meta.get_field('title').help_text,
            expected,
            (f'Параметр help_text у'
             f' {group._meta.get_field("title")} неправильный')
        )

    def test_verbose_name(self):
        """Тестирование verbose_name объекта Group"""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Уникальный фрагмент URL',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name,
                    expected,
                    f'Не правильные verboses объекта {group}'
                )


class CommentModelTest(TestCase):
    """Класс для тестирования моделей Comment."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создаём экземпляр Group для теста"""
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_name',
                                            email='test@yandex.ru',
                                            password='test_pass',),
            text='Тестовая запись для тестового поста.',
        )
        cls.user = User.objects.create_user(username='Alex_Beglov')
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Новый комментарий'
        )

    def test_models_have_correct_object_names(self):
        """Тестирование __str__ объекта Comment"""
        comment = CommentModelTest.comment
        expected_object_name = comment.text[:MAX_LEN_TO_STR]
        self.assertEqual(
            expected_object_name,
            str(comment),
            f'Метод str для {comment}, работает не верно'
        )

    def test_help_text(self):
        """Тестирование help_text объекта Comment"""
        comment = CommentModelTest.comment
        expected = 'Введите текст комментария'
        self.assertEqual(
            comment._meta.get_field('text').help_text,
            expected,
            (f'Параметр help_text у'
             f' {comment._meta.get_field("text")} неправильный')
        )

    def test_verbose_name(self):
        """Тестирование verbose_name объекта Comment"""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name,
                    expected,
                    f'Не правильные verboses объекта {comment}'
                )
