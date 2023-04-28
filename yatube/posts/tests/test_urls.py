from http import HTTPStatus
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from core.assert_func.assert_func import assert_func

from ..models import Group, Post

User = get_user_model()


class PostUrlTests(TestCase):
    """Класс для тестирования страниц и адресов."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создаём экземпляр группы и поста для теста"""
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.author = User.objects.create_user(username='test_name',
                                              email='test@yandex.ru',
                                              password='test_pass',)
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая запись для тестового поста.',
            group=cls.group
        )

    def setUp(self):
        """Создаём неавторизованный, авторизованный клиент.
          Автора поста и другого пользователя"""
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostUrlTests.author)
        self.user = User.objects.create_user(username='Alex_Beglov')
        self.authorized_client_non_author = Client()
        self.authorized_client_non_author.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names_guest = {
            '/': 'posts/index.html',
            f'/group/{PostUrlTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostUrlTests.author.username}/': 'posts/profile.html',
            f'/posts/{PostUrlTests.post.pk}/': 'posts/post_detail.html',
        }
        templates_url_names_user = {
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        templates_url_names_author = {
            f'/posts/{PostUrlTests.post.pk}/edit/': 'posts/create_post.html',
        }
        assert_func(self,
                    self.guest_client,
                    templates_url_names_guest)
        assert_func(self,
                    self.authorized_client_non_author,
                    templates_url_names_user)
        assert_func(self,
                    self.authorized_client_author,
                    templates_url_names_author)

    def test_private_url(self):
        """без авторизации приватные URL недоступны"""
        url_names = (
            '/create/',
            '/follow/',
        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code,
                                 HTTPStatus.FOUND,
                                 f'Приватные URl {url_names} доступны')

    def test_redirect_anonymous_on_login(self):
        """
        Страница /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(reverse('posts:post_create'))
        url = urljoin(reverse('users:login'), "?next=/create/")
        self.assertRedirects(
            response,
            url,
            msg_prefix=('Страница /create/ не '
                        'перенаправляет анонимного пользователя')
        )

    def test_redirect_nonauthor_on_post_detail(self):
        """Страница /posts/<post_id>/edit/ перенаправит
          не автора на страницу поста"""
        response = (self.authorized_client_non_author.
                    get(reverse(
                        'posts:post_edit',
                        kwargs={'post_id': PostUrlTests.post.pk})))
        url = (reverse('posts:post_detail',
                       kwargs={'post_id': PostUrlTests.post.pk}))
        self.assertRedirects(
            response,
            url,
            msg_prefix=('Страница post/edit не перенаправляет '
                        'пользователя не являющегося автором поста')
        )
