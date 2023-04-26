from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserCreateFormTests(TestCase):
    """Класс для тестирования Forms приложения Users"""

    def setUp(self):
        """Создаём клиент"""
        self.client = Client()

    def test_signup(self):
        """Проверяем что при регистрации
          будет создан новый пользователь в БД"""
        counts_users = User.objects.count()
        form_data = {
            'first_name': 'Адександр',
            'last_name': 'Беглов',
            'username': 'Best_Gubernator',
            'email': 'beglov@yandex.ru',
            'password1': 'test_pass',
            'password2': 'test_pass',
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
        self.assertEqual(User.objects.count(), counts_users + 1)
        self.assertTrue(
            User.objects.filter(
                username=form_data['username'],
            ).exists()
        )
