from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from core.assert_func.assert_func import assert_func

User = get_user_model()


class UserViewTest(TestCase):
    """Класс для тестирования view-функций приложения User"""

    def setUp(self):
        """Создаём неавторизованный и авторизованный клиенты"""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Alex_Beglov',
                                             email='test@yandex.ru',
                                             password='test_pass',)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Проверка namespace, view-функция использует соответствущий шаблон"""
        templates_url_names_guest = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
        }
        templates_url_names_user = {
            reverse(
                'users:password_change_form'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
        }

        assert_func(self,
                    self.guest_client,
                    templates_url_names_guest)
        assert_func(self,
                    self.authorized_client,
                    templates_url_names_user)

    def test_signup_form_check(self):
        """Проверка формы для создания пользователя"""
        response = self.guest_client.get(
            reverse('users:signup')
        )
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.CharField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(
                    form_field,
                    expected,
                    f'Поле формы {form_field} не совпадает с {expected}'
                )
