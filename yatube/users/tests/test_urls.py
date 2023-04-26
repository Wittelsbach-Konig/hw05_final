from http import HTTPStatus
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from core.assert_func.assert_func import assert_func

User = get_user_model()


class UserUrlTests(TestCase):
    """Класс для тестирования URLs приложения users"""

    def setUp(self):
        """Создаём неавторизованный и авторизованный клиенты"""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Alex_Beglov',
                                             email='test@yandex.ru',
                                             password='test_pass',)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names_guest = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
        }
        templates_url_names_user = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
        }
        assert_func(self,
                    self.guest_client,
                    templates_url_names_guest)
        assert_func(self,
                    self.authorized_client,
                    templates_url_names_user)

    def test_private_url(self):
        """без авторизации приватные URL недоступны"""
        url_names = (
            '/auth/password_change/',
            '/auth/password_change/done/',
        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.FOUND,
                    'Приватные URL доступны без авторизации'
                )

    def test_redirect_anonymous_on_change_pass(self):
        """
        Страница /password_change/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(reverse('users:password_change_form'))
        url = urljoin(reverse('users:login'), "?next=/auth/password_change/")
        self.assertRedirects(
            response,
            url,
            msg_prefix=('Страница /password_change/ не перенаправляет'
                        ' анонимного пользователя на стр логина')
        )
