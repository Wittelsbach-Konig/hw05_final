import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from core.assert_func.assert_func import assert_func

from ..models import Follow, Group, Post, Comment
from ..forms import CommentForm

User = get_user_model()
POST_NUMBER_1 = 10  # Кол-во выводимых постов на первой стр
POST_NUMBER_2 = 3  # Кол-во выводимых постов на второй стр
NUMBER_OF_POSTS = POST_NUMBER_1 + POST_NUMBER_2  # Всего постов на странницах
COMMENTS_COUNT = 1  # Кол-во комментариев
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTest(TestCase):
    """Класс для тестирования view-функций posts"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создаём объекты класса Post, User, Group"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.author = User.objects.create_user(username='test_name',
                                              email='test@yandex.ru',
                                              password='test_pass',)
        cls.group1 = Group.objects.create(
            title='Заголовок для 1 тестовой группы',
            slug='test_slug1'
        )
        cls.group2 = Group.objects.create(
            title='Заголовок для 2 тестовой группы',
            slug='test_slug2'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая запись для создания 2 поста',
            group=cls.group2,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        """Удаляем файлы из media после тестирования"""
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаём неавторизованного и авторизованного клиента"""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Alex_Beglov')
        self.authorized_client_non_author = Client()
        self.authorized_client_non_author.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostViewTest.author)
        self.users = (self.guest_client,
                      self.authorized_client_author,
                      self.authorized_client_non_author)

    def test_pages_uses_correct_template(self):
        """View-функция использует соответствующий шаблон."""
        templates_page_names_guest = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTest.post.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostViewTest.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewTest.post.pk}
            ): 'posts/post_detail.html',

        }
        templates_page_names_user = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',

        }
        templates_page_names_author = {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewTest.post.pk}
            ): 'posts/create_post.html'
        }
        assert_func(self,
                    self.guest_client,
                    templates_page_names_guest)
        assert_func(self,
                    self.authorized_client_non_author,
                    templates_page_names_user)
        assert_func(self,
                    self.authorized_client_author,
                    templates_page_names_author)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        def aux_assert_fun(client, rel_path):
            """Вспомогательная функция"""
            response = client.get(reverse(**rel_path))
            first_object = response.context['page_obj'][0]
            context_names = {
                first_object.text: PostViewTest.post.text,
                first_object.author: PostViewTest.post.author,
                first_object.group: PostViewTest.post.group,
                first_object.image: f'{PostViewTest.post.image.name}'
            }
            for context_name, expected in context_names.items():
                with self.subTest(context_name=context_name):
                    self.assertEqual(
                        expected,
                        context_name,
                        f'Неправильное название {context_name}'
                    )

        rel_path = {'viewname': 'posts:index'}
        for user in self.users:
            aux_assert_fun(user, rel_path)

    def test_post_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        def aux_assert_fun(client, rel_path):
            """Вспомогательная функция"""
            response = client.get(reverse(**rel_path))
            first_object = response.context['post']
            second_object = response.context['comments']
            context_names = {
                first_object.text: PostViewTest.post.text,
                first_object.author: PostViewTest.post.author,
                first_object.group: PostViewTest.post.group,
                first_object.image: f'{PostViewTest.post.image.name}',
            }
            for context_name, expected in context_names.items():
                with self.subTest(context_name=context_name):
                    self.assertEqual(
                        expected,
                        context_name,
                        f'Неправильное название {context_name}'
                    )
            self.assertIsInstance(response.context['form'], CommentForm)

            self.assertEqual(
                len(second_object),
                COMMENTS_COUNT,
                (f'Количество выведенных постов'
                    f' не соответствует {COMMENTS_COUNT}')
            )
        rel_path = {
            'viewname': 'posts:post_detail',
            'kwargs': {
                'post_id': PostViewTest.post.id
            }
        }
        Comment.objects.create(
            post=PostViewTest.post,
            author=PostViewTest.author,
            text='Новый комментарий'
        )
        for user in self.users:
            aux_assert_fun(user, rel_path)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        def aux_assert_fun(client, rel_path):
            """Вспомогательная функция."""
            response = client.get(reverse(**rel_path))
            first_object = response.context['page_obj'][0]
            second_object = response.context['group']
            context_names = {
                first_object.text: PostViewTest.post.text,
                first_object.author: PostViewTest.post.author,
                first_object.group: PostViewTest.post.group,
                first_object.image: f'{PostViewTest.post.image.name}',
                second_object.title: PostViewTest.group2.title,
                second_object.slug: PostViewTest.group2.slug,
                second_object.description: PostViewTest.group2.description,
            }
            for context_name, expected in context_names.items():
                with self.subTest(context_name=context_name):
                    self.assertEqual(
                        expected,
                        context_name,
                        f'Неправильное название {context_name}'
                    )

        rel_path = {
            'viewname': 'posts:group_list',
            'kwargs': {
                'slug': PostViewTest.post.group.slug
            }
        }
        for user in self.users:
            aux_assert_fun(user, rel_path)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        def aux_assert_fun(client, rel_path):
            """Вспомогательная функция."""
            response = client.get(reverse(**rel_path))
            first_object = response.context['page_obj'][0]
            second_object = response.context['author']
            third_object = response.context['following']
            context_names = {
                first_object.text: PostViewTest.post.text,
                first_object.author: PostViewTest.post.author,
                first_object.group: PostViewTest.post.group,
                first_object.image: f'{PostViewTest.post.image.name}',
                second_object: PostViewTest.author,
                third_object: False,
            }
            for context_name, expected in context_names.items():
                with self.subTest(context_name=context_name):
                    self.assertEqual(
                        expected,
                        context_name,
                        f'Неправильное название {context_name}'
                    )

        rel_path = {
            'viewname': 'posts:profile',
            'kwargs': {
                'username': PostViewTest.post.author.get_username()
            }
        }
        for user in self.users:
            aux_assert_fun(user, rel_path)

    def test_create_post_show_correct_context(self):
        """
        Шаблон create_post сформирован с правильным контекстом.
        """
        rel_path = {
            'viewname': 'posts:post_create',
        }
        response = self.authorized_client_author.get(
            reverse(**rel_path)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(
                    form_field,
                    expected,
                    f'Поле формы {form_field} не совпадает с {expected}'
                )
        self.assertNotIn(
            'is_edit',
            response.context,
            'При создании поста в контексте is_edit быть не должно'
        )

    def test_post_edit_show_correct_context(self):
        """
        Шаблон post_create сформирован с правильным контекстом.
        """
        rel_path = {
            'viewname': 'posts:post_edit',
            'kwargs': {
                'post_id': PostViewTest.post.pk
            }
        }
        response = self.authorized_client_author.get(
            reverse(**rel_path)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(
                    form_field,
                    expected,
                    f'Поле формы {form_field} не совпадает с {expected}'
                )
        self.assertTrue(
            response.context['is_edit'],
            'При редактировании поста is_edit должна быть True'
        )

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        response = self.authorized_client_author.get(
            reverse('posts:group_list',
                    kwargs={'slug': PostViewTest.group1.slug}))
        self.assertNotContains(
            response,
            PostViewTest.post.text,
            msg_prefix=(
                f'Группа {PostViewTest.group1} '
                f'содержит записи {PostViewTest.group2}'
            )
        )


class PaginatorViewsTest(TestCase):
    """Класс для тестирования paginator."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создаём объекты User, Group и Post."""
        cls.author = User.objects.create_user(username='test_name',
                                              email='test@yandex.ru',
                                              password='test_pass',)
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.posts = []
        for i in range(NUMBER_OF_POSTS):
            cls.posts.append(
                Post(
                    text=f'Тестовый пост {i}',
                    author=cls.author,
                    group=cls.group
                )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        """Создаём авторизированного и не авторизированного пользователей."""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Alex_Beglov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.users = (self.guest_client,
                      self.authorized_client)

    def test_first_page_contains_ten_posts(self):
        """Тестируем первую страницу пагинатора."""
        list_urls = {
            reverse('posts:index'): 'index',
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ): 'group',
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.author.get_username()}
            ): 'profile',
        }
        for user in self.users:
            for tested_url in list_urls.keys():
                response = user.get(tested_url)
                self.assertEqual(
                    len(response.context.get('page_obj').object_list),
                    POST_NUMBER_1,
                    (f'Количество выведенных постов'
                     f' не соответствует {POST_NUMBER_1}')
                )
        Follow.objects.create(
            user=self.user,
            author=PaginatorViewsTest.author
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context.get('page_obj').object_list),
            POST_NUMBER_1,
            (f'Количество выведенных постов'
                f' не соответствует {POST_NUMBER_1}')
        )

    def test_second_page_contains_three_posts(self):
        """Тестируем вторую страницу пагинатора."""
        list_urls = {
            reverse('posts:index') + '?page=2': 'index',
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ) + '?page=2': 'group',
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.author.get_username()}
            ) + '?page=2': 'profile',
        }
        for user in self.users:
            for tested_url in list_urls.keys():
                response = user.get(tested_url)
                self.assertEqual(
                    len(response.context.get('page_obj').object_list),
                    POST_NUMBER_2,
                    (f'Количество выведенных постов'
                     f' не соответствует {POST_NUMBER_2}')
                )
        Follow.objects.create(
            user=self.user,
            author=PaginatorViewsTest.author
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index') + '?page=2'
        )
        self.assertEqual(
            len(response.context.get('page_obj').object_list),
            POST_NUMBER_2,
            (f'Количество выведенных постов'
                f' не соответствует {POST_NUMBER_2}')
        )


class CacheTests(TestCase):
    """Класс для тестирования cache."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создаём объект Post"""
        cls.author = User.objects.create_user(username='test_name',
                                              email='test@yandex.ru',
                                              password='test_pass',)
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая запись для создания поста',
        )

    def setUp(self):
        """Создаём гостя и авторизованного пользователя."""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Alex_Beglov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """Тест кэширования страницы index.html."""
        first_state = self.authorized_client.get(reverse('posts:index'))
        post_1 = Post.objects.get(pk=1)
        post_1.delete()
        second_state = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(first_state.content, second_state.content)
        cache.clear()
        third_state = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_state.content, third_state.content)

    def test_cache_paginator(self):
        """Тест того, что разные страницы пагинатора отдают разный контент."""
        posts = []
        for i in range(NUMBER_OF_POSTS):
            posts.append(
                Post(
                    text=f'Тестовый пост {i}',
                    author=CacheTests.author
                )
            )
        Post.objects.bulk_create(posts)
        first_state = self.authorized_client.get(
            reverse('posts:index')
        )
        second_state = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertNotEqual(first_state.content, second_state.content)

    def test_cache_different_users(self):
        """Тест того, что у гостя и пользователя будет разный контент."""
        first_state = self.authorized_client.get(reverse('posts:index'))
        second_state = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(first_state.content, second_state.content)


class FollowTests(TestCase):
    """Класс для тестирования функционала подписок."""

    def setUp(self):
        """
        Создаём клиентов: избранного автора и его подписчика, и пост автора.
        """
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(username='follower',
                                                      email='test_11@mail.ru',
                                                      password='test_pass')
        self.user_following = User.objects.create_user(username='following',
                                                       email='test22@mail.ru',
                                                       password='test_pass')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Тестовая запись для тестирования ленты'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow(self):
        """Подписаться."""
        follow_count = Follow.objects.count()
        self.client_auth_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        follow = Follow.objects.latest()
        self.assertEqual(follow.author, self.user_following)
        self.assertEqual(follow.user, self.user_follower)

    def test_unfollow(self):
        """Отписаться."""
        follow_count = Follow.objects.count()
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following)
        self.assertEqual(follow_count + 1, Follow.objects.count())
        self.client_auth_follower.get(reverse('posts:profile_unfollow',
                                      kwargs={'username':
                                              self.user_following.username}))
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_subscription_feed(self):
        """запись появляется в ленте подписчиков."""
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.client_auth_follower.get('/follow/')
        post_0 = response.context["page_obj"][0]
        self.assertEqual(post_0, self.post)
        response = self.client_auth_following.get('/follow/')
        self.assertNotContains(response,
                               self.post)
